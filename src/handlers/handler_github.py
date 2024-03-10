import enum
import re
import os
import urllib.request
import zipfile
import pprint

from github import Github
from github import Auth

class Verb(enum.StrEnum):
    GET_LATEST_RUN = 'get_latest_run'

def exec_verb(inputargs : dict):

    print(inputargs)

    input_org = inputargs['org']
    input_repo = inputargs['repo']
    input_slug = input_org + '/' + input_repo
    input_workflow = inputargs['workflow']
    input_verb = inputargs['verb']
    input_status = inputargs['status']
    input_patterns = inputargs['patterns']

    # using an access token
    gh_auth = Auth.Token(os.environ['GITHUB_TOKEN'])

    # First create a Github instance:
    # Public Web Github
    gh = Github(auth=gh_auth)

    # Github Enterprise with custom hostname
    #g = Github(base_url="https://{hostname}/api/v3", auth=auth)

    gh_repo = gh.get_repo(input_slug)
    gh_workflow = gh_repo.get_workflow(input_workflow)
    artifact_ret = None
    # assume first is latest
    if (input_verb == Verb.GET_LATEST_RUN):
        gh_workflow_run = gh_workflow.get_runs(status=input_status)[0]
        print(gh_workflow_run)
        gh_workflow_artifacts = gh_workflow_run.get_artifacts()
        input_patterns_compiled = map(re.compile, input_patterns)
        for artifact in gh_workflow_artifacts:
            if any(regex.match(artifact.name) for regex in input_patterns_compiled):
                pprint.pprint(vars(artifact))
                print(artifact.archive_download_url)
                print(artifact.created_at)
                status, headers, response = gh_workflow_run._requester.requestJson("GET", artifact.archive_download_url)     # pylint: disable=W0212
                print(headers)
                print(response)
                if status == 302:
                    zipfilename = f"{artifact.name}.zip"
                    # Follow redirect.
                    success = urllib.request.urlretrieve(headers['location'], zipfilename)
                    print(success)
#                    mybytes2 = success[1].as_bytes()
#                    print(mybytes2)
                    with zipfile.ZipFile(zipfilename, 'r') as zip_f:
                        zip_f.extractall()
#                        zip_f.getinfo('demo/junit.xml').filename = f"{artifact.name}"
#                        zip_f.extract('demo/junit.xml')
                    os.remove(zipfilename)
                    artifact_ret = artifact
                    break

    # To close connections after use
    gh.close()

    return True, artifact_ret.name, artifact_ret.created_at
