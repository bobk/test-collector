import csv
import datetime
import os
from junitparser import JUnitXml, TestCase, Attr, Failure
import common.utils as utils

class MyTestCase(TestCase):
    coverage = Attr()

def exec_verb(inputargs: dict, filename: str, filedatetime: datetime.datetime):
    """
    this function is the converter for junit XML data file format, called from main.py
    it takes a junit.xml file and extracts the data into CSV format to append to an existing file

    Parameters:
    inputargs (dict): complete set of config arguments for the specified file format
    filename (str): what is the input filename
    filedatetime (datetime): what is the datetime of the file

    Returns:
    written (bool): was the data written properly?
    
    """

    utils.log_print("executing: " + __file__)
    utils.log_print(inputargs)
    utils.log_print("working dir: " + os.getcwd())
    written = False

    xmlfile = JUnitXml.fromfile(filename)
    utils.log_print("opened XML file: " + filename)
    csvfile = open(inputargs['csv_output'], 'a', newline='', encoding='UTF-8')
    for suite in xmlfile:
        utils.log_print("found test suite = " + suite.name)
        for my_property in suite.properties():
            if (my_property.name == 'run_id'):
                run_id = my_property.value
                utils.log_print("found run_id = " + str(run_id))
        for case in suite:
            utils.log_print("found test case = " + case.name)
            my_case = MyTestCase.fromelem(case)
            if (my_case.result == [Failure()]):
                my_case_resultnum = 1
            else:
                my_case_resultnum = 0
            csvrow = [str(filedatetime), run_id, suite.name, case.name, case.classname, my_case_resultnum, my_case.coverage]
            csv.writer(csvfile).writerow(csvrow)

    utils.log_print("written: " + inputargs['csv_output'])
    csvfile.close()
    written = True
    if (inputargs['xml_delete']):
        os.remove(filename)

    return written
