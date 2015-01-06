__author__ = 'chuyiq'
'''
Created on 06 Jan 2015

@author: fsaracino
'''

# ********************************************************************
# IMPORT SYSTEM COMPONENTS
# ********************************************************************
import os
import sys
import shutil
import time
import logging

# ********************************************************************
# DEFINE USER'S PATHS
# ********************************************************************
try:
    os.environ['PL1TESTBENCH_ROOT_FOLDER']
except KeyError:
    os.environ['PL1TESTBENCH_ROOT_FOLDER'] = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-2])
    #print ">> os.environ['PL1TESTBENCH_ROOT_FOLDER']=%s" % os.environ['PL1TESTBENCH_ROOT_FOLDER']
else:
    pass

sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'config']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'utils']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'report', 'xls']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'report', 'csv']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'report', 'xml']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'struct']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['lte','common', 'struct']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['lte','libtest']))



# ********************************************************************
# GLOBAL VARIABLES HERE
# ********************************************************************
ts=time.strftime("%Y%m%d_%H%M%S", time.localtime())

# Test report folders: current is renamed to final
dir_curr   = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['lte', 'results', 'current'])
dir_latest = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['lte', 'results', 'latest'])
dir_final  = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['lte', 'results', ts+'_CMW500_TestReport'])


# ********************************************************************
# IMPORT USER DEFINED COMPONENTS
# ********************************************************************
from CfgError import CfgError
from os_utils import pyCopyDir

#from test_plan import test_plan, testtype_l
#from cfg_lte import *

from TestBlerLte import TestBlerLte

from StructXmlTestPlan import StructXmlTestPlan
from StructXmlTestUnitLte import StructXmlTestUnitLte

from CsvReportSummary import CsvReportSummary
from XmlReportSummary import csv2Xml

func_test_table={'LTE_FDD_PERCL_BLER'            : TestBlerLte,
                 'LTE_FDD_NIGHTLY_BLER'          : TestBlerLte,
                 'LTE_FDD_CUSTOM_BLER'           : TestBlerLte,
                 'LTE_FDD_CUSTOM_INTRA_HHO'      : TestBlerLte,
                 'LTE_FDD_NIGHTLY_BLER_FADING'   : TestBlerLte,
                 'LTE_FDD_WEEKLY_BLER_FADING'    : TestBlerLte,
                 'LTE_FDD_MONTHLY_BLER_FADING'   : TestBlerLte,
                 'LTE_FDD_CUSTOM_BLER_FADING'    : TestBlerLte,

                 'LTE_TDD_PERCL_BLER'            : TestBlerLte,
                 'LTE_TDD_NIGHTLY_BLER'          : TestBlerLte,
                 'LTE_TDD_CUSTOM_BLER'           : TestBlerLte,
                 'LTE_TDD_NIGHTLY_BLER_FADING'   : TestBlerLte,
                 'LTE_TDD_WEEKLY_BLER_FADING'    : TestBlerLte,
                 'LTE_TDD_MONTHLY_BLER_FADING'   : TestBlerLte,
                 'LTE_TDD_CUSTOM_BLER_FADING'    : TestBlerLte,

                 'LTE_CA_PERCL_BLER'             : TestBlerLte,
                 'LTE_CA_MONTHLY_BLER_FADING'    : TestBlerLte}





def TestbenchLTE(testconfig_s):
    logger=logging.getLogger('TestbenchLte')

    state = CfgError.ERRCODE_TEST_PASS

    try:
        # Clean any dir_curr from previous run
        if os.path.exists(dir_curr):
            shutil.rmtree(dir_curr)
        if os.path.exists(dir_latest):
            shutil.rmtree(dir_latest)

        # Configure CVS report
        #csv_f='%s_CMW500_TestReport_SUMMARY.csv' % testconfig_s.rat
        csv_abs_f= os.sep.join(dir_curr.split(os.sep)[:]+['%s_CMW500_TestReport_SUMMARY.csv' % testconfig_s.rat])
        csv_report=CsvReportSummary(csv_abs_f)
        logger.debug("CSV Test Summary File : %s" % csv_abs_f)

        # Loop through the testplan
        testplan_s=StructXmlTestPlan(xmlfile=testconfig_s.testplan, struct_name='testplan_s')


        for xmlfile_testunit in testplan_s.struct_testplan_iterator():
            logger.info("*****************************************************************************************")
            logger.info("Starting XML test unit execution: %s" % xmlfile_testunit)
            logger.info("*****************************************************************************************")

            num_iter, NUM_ITER_MAX = 0, 1

            while ( num_iter < NUM_ITER_MAX):
                num_iter += 1

                result = 0
                t0=time.localtime()                                               # Probe start time
                testunit_s=StructXmlTestUnitLte(xmlfile=xmlfile_testunit, struct_name='testunit_s')
                testunit_s.struct_log()

                logger.info("*****************************************************************************************")
                logger.info("Starting test execution of test %05d, iteration#%d of %d" % (testunit_s.common.testid, num_iter, NUM_ITER_MAX))
                logger.info("*****************************************************************************************")

                if 0: raw_input("Press [ENTER]")

                # Select the test function to call
                if not testunit_s.common.testtype in func_test_table.keys():
                    logger.error("Test type %s not supported or disabled: Test skipped" % testunit_s.common.testtype)
                    break
                else:
                    func=func_test_table[testunit_s.common.testtype]
                    logger.debug("Calling %s..." % func)
                    result = func(testconfig_s, testunit_s)

                # Break if the test execution was completed
                if result in [CfgError.ERRCODE_TEST_PASS, CfgError.ERRCODE_TEST_FAILURE, CfgError.ERRCODE_TEST_FAILURE_REFTHR, CfgError.ERRCODE_TEST_FAILURE_INCONCLUSIVE]:
                    break

            # Update test exit state
            if (state==CfgError.ERRCODE_TEST_PASS) and  (not result==CfgError.ERRCODE_TEST_PASS):
                state = CfgError.ERRCODE_TEST_FAILURE if (not result==CfgError.ERRCODE_TEST_FAILURE_INCONCLUSIVE) else result

            # Update test marker
            test_marker='INCONCLUSIVE'
            if result in [CfgError.ERRCODE_TEST_PASS]:
                test_marker='PASS'
            elif result in [CfgError.ERRCODE_TEST_FAILURE, CfgError.ERRCODE_TEST_FAILURE_REFTHR, CfgError.ERRCODE_TEST_FAILURE_ATTACH, CfgError.ERRCODE_TEST_FAILURE_CEST, CfgError.ERRCODE_TEST_FAILURE_INTRAHO, CfgError.ERRCODE_TEST_FAILURE_PARAMCONFIG ]:
                test_marker='FAILURE'
            else:
                pass


            t1=time.localtime()                                            # Probe end time
            t0_frmt=time.strftime("%Y/%m/%d %H:%M:%S", t0)
            t1_frmt=time.strftime("%Y/%m/%d %H:%M:%S", t1)
            dt=time.mktime(t1)-time.mktime(t0)                             # Compute duration [sec]

            logger.info("*****************************************************************************************")
            logger.info("start time     : %s" % t0_frmt)
            logger.info("end time       : %s" % t1_frmt)
            logger.info("duration [sec] : %s" % dt)
            logger.info("testid         : %s" % testunit_s.common.testid)
            logger.info("verdict        : %s" % test_marker)
            logger.info("result         : %s" % result)
            logger.info("description    : %s" % CfgError.MSG[result])
            logger.info("*****************************************************************************************")


            csv_report.append_entry([testunit_s.common.testid, test_marker, result, CfgError.MSG[result], t0_frmt, t1_frmt , dt])

    except SystemExit:
        exc_info = sys.exc_info()
        state=int('%s' % exc_info[1])

    logger.debug("Generating XLM summary file : %s" % (csv_abs_f))
    csv2Xml(csv_abs_f, os.path.splitext(os.path.basename(testconfig_s.testplan))[0])

    logger.debug("Copying folder %s--> %s" % (dir_curr, dir_latest))
    pyCopyDir(dir_curr, dir_latest)

    logger.debug("Copying folder %s --> %s" % (dir_curr, dir_final))
    pyCopyDir(dir_curr, dir_final)

    logger.debug("Removing folder %s" % dir_curr)
    shutil.rmtree(dir_curr)

    return (state)

# ********************************************************************
#                            MAIN
# ********************************************************************
if __name__ == '__main__':
    pass
