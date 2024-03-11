import os
import random
from junitparser import JUnitXml, TestSuite, TestCase, FloatAttr, Failure

#   os.environ['GITHUB_RUN_ID']  Build.ID
RUN_ID = (os.getenv('GITHUB_RUN_ID') or os.getenv('BUILD_BUILDID'))
suite = TestSuite('Application1.Component1')
suite.add_property('run_id', RUN_ID)

NUM_CASES = 5
CASE_CLASS_LIST = ['Stability', 'Functionality', 'Scalability', 'Security']
TestCase.coverage = FloatAttr('coverage')

for case in range(1, NUM_CASES + 1):
    case_class = random.choice(CASE_CLASS_LIST)
    case = TestCase(('case' + str(case)), ('class.' + case_class))
    case.coverage = random.randint(1, 100)
    if (random.randint(1, (2 * NUM_CASES)) == 1):
        case.result = [ Failure() ]
    suite.add_testcase(case)

xmlfile = JUnitXml()
xmlfile.add_testsuite(suite)
xmlfile.write('junit.xml')
