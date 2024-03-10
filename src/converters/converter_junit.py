import csv
import datetime
import os
from junitparser import JUnitXml, TestCase, Attr

class MyTestCase(TestCase):
    coverage = Attr()

def exec_verb(inputargs: dict, filename: str, filedatetime: datetime.datetime):

    print(inputargs)
    print('converting to CSV')

    print(os.getcwd())
    xmlfile = JUnitXml.fromfile(filename)
    csvfile = open('foo.csv', 'a', newline='', encoding='UTF-8')
    for suite in xmlfile:
        print(suite.name)
        for my_property in suite.properties():
            if (my_property.name == 'run_id'):
                run_id = my_property.value
        for case in suite:
    #        for attribute in case.attributes():
    #            if (attribute.name == 'coverage'):
    #                coverage = attribute.value
            my_case = MyTestCase.fromelem(case)
            csvrow = [str(filedatetime), run_id, suite.name, case.name, case.classname, my_case.coverage]
            csv.writer(csvfile).writerow(csvrow)

    csvfile.close()
