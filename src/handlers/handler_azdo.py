import enum
import os
import pprint

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
    input_build_id = inputargs['build_id']
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

    test1 = azdo_client.get_pipeline(input_project, input_build_id)
    test2 = azdo_client.list_runs(input_project, input_build_id)

    pprint.pprint(test1.__dict__)
    pprint.pprint(test2)
    pprint.pprint(test2[0].__dict__)

    return True, '', None
