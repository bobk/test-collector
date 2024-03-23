import csv
import datetime
import os
from junitparser import JUnitXml, TestCase, Attr, Failure
import common.utils as utils

class MyTestCase(TestCase):
    coverage = Attr()

@utils.trace
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

    written = False
    outfilepath = os.path.join(utils.OUTPUT_PATH, inputargs['csv_output'])

    xmlfile = JUnitXml.fromfile(filename)
    utils.log_print(f"opened XML file = {filename}")
    csvfile = open(outfilepath, 'a', newline='', encoding='UTF-8')
    for suite in xmlfile:
        utils.log_print(f"found test suite = {suite.name}")
        for my_property in suite.properties():
            if (my_property.name == 'run_id'):
                run_id = my_property.value
                utils.log_print(f"found run_id = {str(run_id)}")
        for case in suite:
            utils.log_print(f"found test case = {case.name}")
            my_case = MyTestCase.fromelem(case)
            my_case_resultnum = 1 if (my_case.result == [Failure()]) else 0
            csvrow = [str(filedatetime), run_id, suite.name, case.name, case.classname, my_case_resultnum, my_case.coverage]
            csv.writer(csvfile).writerow(csvrow)

    utils.log_print(f"written = {outfilepath}")
    csvfile.close()
    written = True
    if (inputargs['xml_delete']):
        os.remove(filename)

    return written
