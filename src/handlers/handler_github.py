import enum
import os
import datetime
import zipfile
import common.utils as utils
import re
from http import HTTPStatus

import urllib.request

from github import Github
from github import Auth

class Verb(enum.StrEnum):
    GET_LATEST_RUN = 'get_latest_run'

@utils.trace
def exec_verb(inputargs : dict, last_run_id : int):
    """
    this function is the handler for github data sources, called from main.py
    it accesses github, finds the latest run for the specified workflow, and looks
    for all artifacts in that run, that contain our desired file

    Parameters:
    inputargs (dict): complete set of config arguments for the specified data source
    last_run_id (int): the id from the last run of the specified data source workflow

    Returns:
    downloaded (bool): was a new file downloaded?
    outfilename (str): if so, what is the filename
    outfiledatetime (datetime): what is the datetime of the file
    run_id (int): a new latest run id to be placed back in the config_runs file
    """

#   setup initial items
    downloaded, outfilename, outfiledatetime, run_id = False, None, None, None

#   authenticate and connect
    gh_auth = Auth.Token(os.environ['GITHUB_TOKEN'])
    gh_url = inputargs['org'] + '/' + inputargs['repo']
    gh_creds = Github(auth=gh_auth)

#   access resource
    gh_workflow = gh_creds.get_repo(gh_url).get_workflow(inputargs['workflow'])
    utils.log_print(f"connected to = {gh_url}")

    if (inputargs['verb'] == Verb.GET_LATEST_RUN):
        utils.log_print(f"executing verb = {inputargs['verb']}")

#   for now, assume first returned run is latest
        gh_workflow_run = gh_workflow.get_runs(status=inputargs['status'])[0]
        run_id = gh_workflow_run.id
        utils.log_print(f"latest run_id = {str(run_id)}")

#   only do something if there is a new run
        if (run_id > last_run_id):
            utils.log_print(f"latest run_id > last_run_id")

#   get all the artifact files for the run and see if any match our filter
            gh_workflow_artifacts = gh_workflow_run.get_artifacts()
            input_patterns_compiled = map(re.compile, inputargs['artifact_patterns'])

            for artifact in gh_workflow_artifacts:
                utils.log_print(f"looking for artifact = {artifact.name}")
                if any(regex.match(artifact.name) for regex in input_patterns_compiled):

#   if we find one, go to the initial download URL
                    download_url_1 = artifact.archive_download_url
                    status_1, headers_1, _ = gh_workflow_run._requester.requestJson("GET", download_url_1)     # pylint: disable=W0212
                    utils.log_print(f"status = {str(status_1)}")

#   now use that response to obtain and go to the real download URL
                    if (status_1 == HTTPStatus.FOUND):
                        utils.log_print(f"initial download URL received, processing redirect")
                        # follow redirect
                        zip_output = (os.path.join(utils.OUTPUT_PATH, inputargs['zip_output']))
                        response_2 = urllib.request.urlretrieve(headers_1['location'], zip_output)
                        utils.log_print(f"response = {str(response_2[1])}")

                        if ((str(response_2[1]).find(artifact.name)) >= 0):
                            utils.log_print(f"downloaded and created = {zip_output}")

#   now we have the file downloaded, so process it looking for our actual artifact
                            with zipfile.ZipFile(zip_output, 'r') as zip_f:
                                zipfilesubpath = inputargs['artifact_subpath'] + artifact.name
                                outfilesubpath = inputargs['artifact_output'] + '.' + str(run_id)
#   note that we want to both extract the file to a different dir and change its name at the same time
                                zip_f.getinfo(zipfilesubpath).filename = outfilesubpath
                                zip_f.extract(zipfilesubpath, utils.OUTPUT_PATH)
                                outfiledatetime = datetime.datetime(*(zip_f.getinfo(zipfilesubpath).date_time))
                                outfilename = os.path.join(utils.OUTPUT_PATH, outfilesubpath)
                            utils.log_print(f"extracted = {outfilename}")
                            downloaded = True
                            os.remove(zip_output)
                            break
                        else:
                            utils.log_print(f"error received")
                    else:
                        utils.log_print(f"error received")
        else:
            utils.log_print(f"latest run_id <= last_run_id")

    # To close connections after use
    gh_creds.close()

    return downloaded, outfilename, outfiledatetime, run_id
