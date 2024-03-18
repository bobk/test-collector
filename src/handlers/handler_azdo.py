import enum
import os
import json
import datetime
import requests
import zipfile
import common.utils as utils

import azure.devops.connection
import azure.devops.v7_1.pipelines
import msrest.authentication

class Verb(enum.StrEnum):
    GET_LATEST_RUN = 'get_latest_run'

def exec_verb(inputargs : dict, last_run_id : int):

    utils.print_log(inputargs)

    downloaded = False
    # using an access token
    azdo_auth = os.environ['AZURE_DEVOPS_PAT']
    azdo_org_url = 'https://dev.azure.com/' + inputargs['org']

    azdo_creds = msrest.authentication.BasicAuthentication('', azdo_auth)
    azdo_conn = azure.devops.connection.Connection(base_url=azdo_org_url, creds=azdo_creds)
    azdo_client = azdo_conn.clients_v7_1.get_pipelines_client()

    test1 = azdo_client.get_pipeline(inputargs['project'], inputargs['definition_id'])
    test2 = azdo_client.list_runs(inputargs['project'], inputargs['definition_id'])

    utils.print_log(test1.__dict__)
    utils.print_log(test2)
    utils.print_log(test2[0].__dict__)
    utils.print_log(test2[1].__dict__)
    if (test2[0].id > last_run_id):
        apiurl = f'https://dev.azure.com/krcloud1/terraform/_apis/build/builds/{test2[0].id}/artifacts?artifactName=junit.xml&api-version=6.0&format=zip'
    #    success = urllib.request.urlretrieve(api, 'junit2.xml')
        resp1 = requests.get(apiurl, auth=('', azdo_auth), timeout=60)
        utils.print_log(resp1.headers)
        utils.print_log(resp1.content)
        downloadurl = json.loads(resp1.content)['resource']['downloadUrl']
        resp2 = requests.get(downloadurl, auth=('', azdo_auth), timeout=60)

        with open(inputargs['zip_output'], 'wb') as f:
            f.write(resp2.content)
        with zipfile.ZipFile(inputargs['zip_output'], 'r') as zip_f:
            filepath = inputargs['artifact_subpath'] + 'junit.xml'
            zip_f.getinfo(filepath).filename = inputargs['artifact_output']
            filedatetime = datetime.datetime(*(zip_f.getinfo(filepath).date_time))
            utils.print_log(filedatetime)
            zip_f.extract(filepath)
    #        zip_f.extractall()
        downloaded = True
        os.remove(inputargs['zip_output'])

#    utils.print_log(success)

    if (downloaded):
        return True, inputargs['artifact_output'], filedatetime, test2[0].id
    else:
        return False, None, None, None
