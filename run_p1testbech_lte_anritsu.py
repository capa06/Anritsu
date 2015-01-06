__author__ = 'chuyiq'

'''
Created on 19 Dec 2014

@author: fsaracino
'''


# ********************************************************************
# IMPORT SYSTEM COMPONENTS
# ********************************************************************
import sys
import os
import logging
import re
import argparse
import bz2

from xml.etree.ElementTree import parse

# ********************************************************************
# DEFINE USER'S PATHS
# ********************************************************************
(cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))
os.environ['PL1TESTBENCH_ROOT_FOLDER'] = cmdpath
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'config']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'utils']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'struct']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'struct','templates']))

sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['lte']))
#sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['wcdma']))
#sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['gsm']))


# ********************************************************************
# IMPORT USER DEFINED COMPONENTS
# ********************************************************************
from CfgError import CfgError
from os_utils import cleanRun
from StructXml import StructXml
from TestbenchLTE import TestbenchLTE
#from TestbenchWCDMA import TestbenchWCDMA
#from TestbenchGSM import TestbenchGSM



def runTest(testconfig_s):
    """
        It allows to start the testbench as a function. For instance:
        res=runme(log='DEBUG', cmwip='0.0.0.0', rat='LTE', ctrlif='AT', test2execute='[0]', pwrmeas=0, usimemu=0)
    """

    # Configure logging
    from cfg_multilogging import cfg_multilogging
    loglevel=testconfig_s.log
    numeric_level=getattr(logging, loglevel.upper(), None)
    logging.root.level = numeric_level
    logfilename=os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['runTest.LOG'])    # Create LOG file absolute name
    cfg_multilogging(loglevel, logfilename)
    logger=logging.getLogger('runTest')

    # Further checks on arguments
    if testconfig_s.testerip is None:
        logger.error("ERROR: runme() : specify a valid CMW500 IP address")
        return CfgError.ERRCODE_TEST_FAILURE_PARAMCONFIG
    if testconfig_s.ctrlif is None:
        logger.error("ERROR: runme() : specify a valid control interface")
        return CfgError.ERRCODE_TEST_FAILURE_PARAMCONFIG
    if testconfig_s.rat.upper()=='GSM' or testconfig_s.rat.upper()=='WCDMA':
        logger.error("ERROR: RAT not supported yet")
        return CfgError.ERRCODE_TEST_FAILURE_PARAMCONFIG
    if (testconfig_s.psu or testconfig_s.pwrmeas) and testconfig_s.psugwip is None:
        logger.error("ERROR: runme() : specify a valid PSU Gateway IP address")
        return CfgError.ERRCODE_TEST_FAILURE_PARAMCONFIG
    # Build and check the absoulte path of the XML testplan file
    testconfig_s.testplan = testconfig_s.testplan.replace('/', os.sep)
    testconfig_s.testplan = os.path.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'], testconfig_s.testplan)
    if not os.path.isfile(testconfig_s.testplan):
        logger.error("XML testplan file not found: %s" % testconfig_s.testplan)
        sys.exit(CfgError.ERRCODE_SYS_FILE_IO)
    # Show info
    logger.info("*****************************************************************************************")
    logger.info("Starting test with the following configuration:")
    testconfig_s.struct_log(excl_l=['remoteDBpwd','scdu_pwd'])
    logger.info("*****************************************************************************************")

    # Select and start the test (function)
    if testconfig_s.rat in ['LTE_FDD', 'LTE_TDD', 'LTE_CA']:

        func_table={ 'LTE_FDD' : TestbenchLTE,
                     'LTE_TDD' : TestbenchLTE,
                     'LTE_CA'  : TestbenchLTE }  # 'WCDMA':TestbenchWCDMA, 'GSM':TestbenchGSM
        func=func_table[testconfig_s.rat]
        logger.debug("Calling %s..." % func)
        res=func(testconfig_s)
    else:
        logger.error("Invalid RAT : %s, valid range {LTE_FDD, LTE_TDD, LTE_CA}" % testconfig_s.rat)
        res=CfgError.ERRCODE_TEST_PARAM_INVALID

    logger.info("EXIT STATUS : (%s, %s)" % (res, CfgError.MSG[res]))
    return res



if __name__ == '__main__':

    PL1TESTBENCH_VER="1.0.0"

    cleanRun()

    # Configure parser
    parser = argparse.ArgumentParser(prog=cmdname,
                                     formatter_class=argparse.RawDescriptionHelpFormatter, prefix_chars='-',
                                     usage='%(prog)s -xml <fileconfig.xml>',
                                     description='''Description:\n  start pl1testbench for LTE operations''',
                                     epilog='''Example:\n python runme.py my_testconfig.xml''')

    parser.add_argument("-xml",          type=str,  default='lte_testconfig.xml', help='test configuration file in XLM format. DEFAULT=lte_testconfig.xml')
    parser.add_argument("-log",          type=str, choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'], default=None, help="logging level" )
    parser.add_argument("-rat",          type=str, choices=['GSM','WCDMA', 'LTE_FDD', 'LTE_TDD', 'LTE_CA'],   default=None, help="radio access technology")
    parser.add_argument("-testerip",     type=str,                                                            default=None, help='tester IP address' )
    parser.add_argument("-testername",   type=str,                                                            default=None, help='tester name' )
    parser.add_argument("-ctrlif",       type=str,                                                            default=None, help="modem communication control interface")
    parser.add_argument("-testplan",     type=str,                                                            default=None, help="relative path to the XML testplan")
    parser.add_argument("-usimemu",      type=int, choices=[0, 1],                                            default=None, help="enable/disable USIM emulator")
    parser.add_argument("-psu",          type=int, choices=[0, 1],                                            default=None, help="enable/disable PSU")
    parser.add_argument("-pwrmeas",      type=int, choices=[0, 1],                                            default=None, help="enable/disable power measurements")
    parser.add_argument("-psugwip",      type=str,                                                            default=None, help='PSU gateway IP address' )
    parser.add_argument("-psugpib",      type=int,                                                            default=None, help='PSU GPIB port' )
    parser.add_argument("-scdu",         type=int, choices=[0, 1],                                            default=None, help="enable/disable SCDU")
    parser.add_argument("-scdu_ip",      type=str,                                                            default=None, help="SCDU IP address")
    parser.add_argument("-scdu_port",    type=int, choices=[1, 2, 3, 4, 5, 6, 7, 8],                          default=None, help="SCDU port")
    parser.add_argument("-scdu_uid",     type=str,                                                            default=None, help="SCDU username")
    parser.add_argument("-scdu_pwd",     type=str,                                                            default=None, help="SCDU pwd")
    parser.add_argument("-reboot",       type=int, choices=[0, 1],                                            default=None, help="reboot the modem before tests")
    parser.add_argument("-msglog",       type=int, choices=[0, 1, 2, 3],                                      default=None, help="enable/disable BEANIE logs. Temporary disabled")
    parser.add_argument("-remoteDB",     type=int, choices=[0, 1],                                            default=None, help="enable/disable MySQL database")
    parser.add_argument("-remoteDBhost", type=str,                                                            default=None, help='MySQL host' )
    parser.add_argument("-remoteDBuid",  type=str,                                                            default=None, help='MySQL user ID' )
    parser.add_argument("-remoteDBpwd",  type=str,                                                            default=None, help='MySQL pwd' )
    parser.add_argument("-remoteDBname", type=str,                                                            default=None, help='MySQL database name' )

    # Parse command line options
    args=parser.parse_args()

    # Call main functions
    if not os.path.isfile(args.xml):
        print "ERROR::XML configuration file not found: %s" % args.xml
        res = CfgError.ERRCODE_TEST_PARAM_INVALID
    else:
        testconfig_s=StructXml(xmlfile=args.xml, struct_name='testconfig_s', node_name='opts')

        # Allow any command-line arguments to override XML values.
        for param in args.__dict__.keys():
            val = getattr(args, param)
            if val is not None:
                if param in ['remoteDBpwd', 'scdu_pwd']:
                    val = bz2.compress(val)
                setattr(testconfig_s, param, val)
        res=runTest(testconfig_s)

    exit(res)
