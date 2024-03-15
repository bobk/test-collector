import enum
import os
import pprint
import zipfile
import requests
import json
import datetime

import azure.devops.connection
import azure.devops.v7_1.pipelines
import msrest.authentication

#from azure.devops.connection import Connection
#from msrest.authentication import BasicAuthentication

class Verb(enum.StrEnum):
    GET_LATEST_RUN = 'get_latest_run'

def exec_verb(inputargs : dict):

    print(inputargs)

    input_org = inputargs['org']
    input_project = inputargs['project']
    input_definition_id = inputargs['definition_id']
    input_artifact_subpath = inputargs['artifact_subpath']
#    input_slug = input_org + '/' + input_repo
#    input_workflow = inputargs['workflow']
#    input_verb = inputargs['verb']
#    input_status = inputargs['status']
#    input_patterns = inputargs['patterns']

    # using an access token
    azdo_auth = os.environ['AZURE_DEVOPS_PAT']
    azdo_org_url = 'https://dev.azure.com/' + input_org

    azdo_creds = msrest.authentication.BasicAuthentication('', azdo_auth)
    azdo_conn = azure.devops.connection.Connection(base_url=azdo_org_url, creds=azdo_creds)
    azdo_client = azdo_conn.clients_v7_1.get_pipelines_client()

    test1 = azdo_client.get_pipeline(input_project, input_definition_id)
    test2 = azdo_client.list_runs(input_project, input_definition_id)

    pprint.pprint(test1.__dict__)
    pprint.pprint(test2)
    pprint.pprint(test2[0].__dict__)
    pprint.pprint(test2[1].__dict__)
    apiurl = 'https://dev.azure.com/krcloud1/terraform/_apis/build/builds/430/artifacts?artifactName=junit.xml&api-version=6.0&format=zip'
#    success = urllib.request.urlretrieve(api, 'junit2.xml')
    resp1 = requests.get(apiurl, auth=('', azdo_auth), timeout=60)
    print(resp1.headers)
    print(resp1.content)
    downloadurl = json.loads(resp1.content)['resource']['downloadUrl']
    resp2 = requests.get(downloadurl, auth=('', azdo_auth), timeout=60)
    with open("junit_azdo.zip", "wb") as f:
        f.write(resp2.content)
    with zipfile.ZipFile("junit_azdo.zip", 'r') as zip_f:
        filepath = input_artifact_subpath + 'junit.xml'
        zip_f.getinfo(filepath).filename = "junit_azdo.xml"
        filedatetime = datetime.datetime(*(zip_f.getinfo(filepath).date_time))
        print(filedatetime)
        print('foo')
        zip_f.extract(filepath)
#        zip_f.extractall()
    os.remove("junit_azdo.zip")

#    print(success)

    return True, "junit_azdo.xml", filedatetime
