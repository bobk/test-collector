import enum
import os
import re
import urllib.request
import zipfile
import common.utils as utils

from github import Github
from github import Auth

class Verb(enum.StrEnum):
    GET_LATEST_RUN = 'get_latest_run'

def exec_verb(inputargs : dict, last_run_id : int):

    utils.print_log(str(inputargs))

    downloaded = False
    # using an access token
    gh_auth = Auth.Token(os.environ['GITHUB_TOKEN'])

    # First create a Github instance:
    gh = Github(auth=gh_auth)

    # Github Enterprise with custom hostname
    input_slug = inputargs['org'] + '/' + inputargs['repo']
    gh_repo = gh.get_repo(input_slug)

    gh_workflow = gh_repo.get_workflow(inputargs['workflow'])
    artifact_ret = None
    # assume first is latest
    if (inputargs['verb'] == Verb.GET_LATEST_RUN):
        gh_workflow_run = gh_workflow.get_runs(status=inputargs['status'])[0]
        utils.print_log(gh_workflow_run)
        run_id = gh_workflow_run.id
        if (run_id > last_run_id):
            gh_workflow_artifacts = gh_workflow_run.get_artifacts()
            input_patterns_compiled = map(re.compile, inputargs['artifact_patterns'])
            for artifact in gh_workflow_artifacts:
                if any(regex.match(artifact.name) for regex in input_patterns_compiled):
                    utils.print_log(vars(artifact))
                    utils.print_log(artifact.archive_download_url)
                    utils.print_log(artifact.created_at)
                    status, headers, response = gh_workflow_run._requester.requestJson("GET", artifact.archive_download_url)     # pylint: disable=W0212
                    utils.print_log(headers)
                    utils.print_log(response)
                    if status == 302:
                        # Follow redirect.
                        success = urllib.request.urlretrieve(headers['location'], inputargs['zip_output'])
                        utils.print_log(success)
                        with zipfile.ZipFile(inputargs['zip_output'], 'r') as zip_f:
                            zip_f.getinfo('junit.xml').filename = inputargs['artifact_output']
                            zip_f.extract('junit.xml')
                        os.remove(inputargs['zip_output'])
                        artifact_ret = artifact
                        downloaded = True
                        break

    # To close connections after use
    gh.close()

    if (downloaded):
        return downloaded, inputargs['artifact_output'], artifact_ret.created_at, run_id
    else:
        return False, None, None, None
