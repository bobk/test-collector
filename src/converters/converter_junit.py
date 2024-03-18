import csv
import datetime
import os
from junitparser import JUnitXml, TestCase, Attr, Failure
import common.utils as utils

class MyTestCase(TestCase):
    coverage = Attr()

def exec_verb(inputargs: dict, filename: str, filedatetime: datetime.datetime):

    utils.print_log(inputargs)
    utils.print_log('converting to CSV')

    utils.print_log(os.getcwd())
    xmlfile = JUnitXml.fromfile(filename)
    csvfile = open(inputargs['csv_output'], 'a', newline='', encoding='UTF-8')
    for suite in xmlfile:
        utils.print_log(suite.name)
        for my_property in suite.properties():
            if (my_property.name == 'run_id'):
                run_id = my_property.value
        for case in suite:
    #        for attribute in case.attributes():
    #            if (attribute.name == 'coverage'):
    #                coverage = attribute.value
            my_case = MyTestCase.fromelem(case)
            if (my_case.result == [Failure()]):
                utils.print_log('fail')
            else:
                utils.print_log('pass')
            csvrow = [str(filedatetime), run_id, suite.name, case.name, case.classname, my_case.coverage]
            csv.writer(csvfile).writerow(csvrow)

    csvfile.close()
    if (inputargs['xml_delete']):
        os.remove(filename)
