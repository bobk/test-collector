import enum
import os
import datetime
import zipfile
import common.utils as utils
import re
from http import HTTPStatus

import json
import requests

import azure.devops.connection
import azure.devops.v7_1.pipelines
import azure.devops.v7_1.build
import msrest.authentication

class Verb(enum.StrEnum):
    GET_LATEST_RUN = 'get_latest_run'

AZDO_ROOT = 'https://dev.azure.com/'

@utils.trace
def exec_verb(inputargs : dict, last_run_id : int):
    """
    this function is the handler for azdo data sources, called from main.py
    it accesses azdo, finds the latest run for the specified workflow, and looks
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
    azdo_auth = os.environ['AZURE_DEVOPS_PAT']
    azdo_url = AZDO_ROOT + inputargs['org']
    azdo_creds = msrest.authentication.BasicAuthentication('', azdo_auth)
    azdo_conn = azure.devops.connection.Connection(base_url=azdo_url, creds=azdo_creds)

#   access resource
    azdo_pipelines = azdo_conn.clients_v7_1.get_pipelines_client()
    azdo_build = azdo_conn.clients_v7_1.get_build_client()
    utils.log_print(f"connected to = {azdo_url}")

    if (inputargs['verb'] == Verb.GET_LATEST_RUN):
        utils.log_print(f"executing verb = {inputargs['verb']}")

#   for now, assume first returned run is latest
        azdo_pipeline_run = azdo_pipelines.list_runs(inputargs['project'], inputargs['definition_id'])[0]
        run_id = azdo_pipeline_run.id
        utils.log_print(f"latest run_id = {str(run_id)}")

#   only do something if there is a new run
        if (run_id > last_run_id):
            utils.log_print(f"latest run_id > last_run_id")

#   get all the artifact files for the run and see if any match our filter
            azdo_pipeline_artifacts = azdo_build.get_artifacts(inputargs['project'], run_id)
            input_patterns_compiled = map(re.compile, inputargs['artifact_patterns'])

            for artifact in azdo_pipeline_artifacts:
                utils.log_print(f"looking for artifact = {artifact.name}")
                if any(regex.match(artifact.name) for regex in input_patterns_compiled):

#   if we find one, go to the initial download URL
                    download_url_1 = f'{azdo_url}/{inputargs['project']}/_apis/build/builds/{run_id}/artifacts?artifactName={artifact.name}&api-version=6.0&format=zip'
                    response_1 = requests.get(download_url_1, auth=('', azdo_auth), timeout=60)
                    utils.log_print(f"response = {str(response_1.content)}")

#   now use that response to obtain and go to the real download URL
                    if (response_1.status_code == HTTPStatus.OK):
                        utils.log_print(f"initial download URL received, processing redirect")
                        # follow redirect
                        zip_output = os.path.join(utils.OUTPUT_PATH, inputargs['zip_output'])
                        response_2 = requests.get(json.loads(response_1.content)['resource']['downloadUrl'], auth=('', azdo_auth), timeout=60)
                        utils.log_print(f"response = {str(response_2)}")

                        if (response_2.status_code == HTTPStatus.OK):
                            with open(zip_output, 'wb') as f:
                                f.write(response_2.content)
                            utils.log_print(f"downloaded and created = {zip_output}")

#   now we have the file downloaded, so process it looking for our actual artifact
                            with zipfile.ZipFile(zip_output, 'r') as zip_f:
                                zipfilesubpath = inputargs['artifact_subpath'] + artifact.name
                                outfilesubpath = inputargs['artifact_output'] + ('.' + str(run_id))
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

# To close connections after use - following is not needed/does not exist in AZDO Python lib
    # azdo_conn.close()

    return downloaded, outfilename, outfiledatetime, run_id
