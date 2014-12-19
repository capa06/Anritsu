__author__ = 'chuyiq'

#! /usr/bin/env python



#######################################################################################################################

#

# Anritsu MT8820C instrument driver class

#

#######################################################################################################################





# ********************************************************************

# IMPORT SYSTEM COMPONENTS

# ********************************************************************

import os
import sys
import logging
import time
import re
from visa import *

# ********************************************************************

# DEFINE USER'S PATHS

# ********************************************************************
try:

    os.environ['PL1TESTBENCH_ROOT_FOLDER']

except KeyError:

    os.environ['PL1TESTBENCH_ROOT_FOLDER'] = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-3])

    print ">> os.environ['PL1TESTBENCH_ROOT_FOLDER']=%s" % os.environ['PL1TESTBENCH_ROOT_FOLDER']

else:

    pass

sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'config']))

# ********************************************************************

# IMPORT USER DEFINED COMPONENTS

# ********************************************************************

from vxi_11 import vxi_11_connection

from CfgError import CfgError


rm = ResourceManager()







# ****************************************************************************************************

# GLOBAL VARIABLES

# ****************************************************************************************************







# ****************************************************************************************************

# GLOBAL FUNCTIONS

# ****************************************************************************************************
class Anritsu_MT8820C(vxi_11_connection):

    default_lock_timeout=20000

class Anr(object):

    def __init__(self, name, ip_addr):

        self.name    = name

        self.ip_addr = ip_addr

        logging.debug ('init-routine')

        #self.dev = Anritsu_MT8820C(ip_addr, timeout=20)
        ip_socket='TCPIP0::'+ip_addr+'::56001::SOCKET'
        self.dev=rm.open_resource(ip_socket,read_termination='\n')
        #self=rm.open_resource(ip_socket,read_termination='\n')
        #self.dev = rohde_and_schwarz_CMW500(ip_addr, timeout=20)
        self.dev.write("*CLS")

        self.resultsFile = ""



    # ***************************

    # Private methods

    # ***************************

    def _param_write(self, cmd, param, param_tag):

        cmd_wr = cmd + (" %s" % param)

        self.write(cmd_wr)

        check = self._param_write_check(cmd, param, param_tag)

        return check



    def _param_write_check(self, cmd, param, param_tag):

        logger = logging.getLogger('%s._param_config_check' % self.name)

        cmd_rd = cmd + "?"

        readback    = self.read(cmd_rd)

        if ((type(param) is int) or (type(param) is float)):

            res         = 0 if (float(param)==float(readback)) else 1

        else:

            res         = 0 if (param in str(readback)) else 1

        logger.debug("CHECKPOINT %-15s : %s (%s, readback=%s)" % (param_tag, ('FAIL' if res else 'PASS'), param, readback))

        self.param_check += res

        return res



    def _param_write_nocheck(self, cmd, param):

        cmd_wr = cmd + (" %s" % param)

        self.write(cmd_wr)



    def _param_read(self, cmd):

        cmd_rd = cmd + "?"

        readback    = self.read(cmd_rd)

        return readback



    def _param_read_check(self, cmd, param):

        logger = logging.getLogger('%s._param_read_check' % self.name)

        cmd_rd = cmd + "?"

        readback    = self.read(cmd_rd)

        if ((type(param) is int) or (type(param) is float)):

            res         = 0 if (float(param)==float(readback)) else 1

        else:

            res         = 0 if (param in str(readback)) else 1

        logger.debug("CHECK READ : %-15s : %s (%s, readback=%s)" % (cmd, ('FAIL' if res else 'PASS'), param, readback))

        return res



    #======================================================================

    # Instrument access functionalities

    #======================================================================

    def close(self):

        #self.write(r"GTL")

        #self.dev.disconnect()
        self.write('GTL')
        self.dev.close()



    def reset(self):

        self.write(r'*CLS')

        self.write("&ABO")

        self.write("&BRK")

        self.write("*RST")

        self.wait_for_completion()

        self.write("*CLS")

        self.wait_for_completion()

        self.write("&GTR")



    def reboot(self):    # FOR CMU ONLY BUT THIS NEVER WORKED

        self.write("*SYST:REB:ERR ON")



    def gotolocal(self):

        self.write('&GTL')



    def write(self, command):

        logger=logging.getLogger('%s.write' % self.name)

        logger.debug ("   %s write command \"%s\"" % (self.name, command))

        self.dev.write(command)

        self.wait_for_completion()


    def ask(self,command):
        logger=logging.getLogger('%s.write' % self.name)
        logger.debug("  %s write command \"%s\"" % (self.name,command))
        reading=self.dev.ask(command)
        return reading
    def preset(self):

        self.write("SYSTem:RESet:ALL")

        self.wait_for_completion()



    def read(self, command):

        logger=logging.getLogger('%s.read' % self.name)



        logger.debug ("   %s read command \"%s\"" % (self.name, command))

        self.dev.write(command)

        #reading = self.dev.read()[2].strip()
        reading= self.dev.read()
        lettercount = 25

        readingshort = reading[0:lettercount]

        if len(reading)>lettercount:

            logger.debug ("   %s read response \"%s\"..........." % (self.name, readingshort))

        else:

            logger.debug ("   %s read response \"%s\"" % (self.name, reading))



        return reading



    def wait_response(self, scpi_query_cmd="", exp_rsp="", timeout = 5):

        logger = logging.getLogger('%s.wait_response' % self.name)



        if scpi_query_cmd == "":

            logger.error("no scpi command query")

            return

        else:

            logger.debug("Waiting for response: %s" %exp_rsp)

            start_time= int(time.time())

            elapsed_time = 0

            while elapsed_time <= timeout:

                status = self.read(scpi_query_cmd)

                logger.debug("response is: %s " %status)

                if status == exp_rsp:

                    logger.info("Expected response received within %s secs"  % timeout)

                    return True

                time.sleep(1)

                cum_time = int(time.time())

                elapsed_time = cum_time - start_time

                logger.debug (elapsed_time)



            logger.error("Expected response not received within %s secs"  % timeout)



            return False



    def wait_for_completion(self, timeout=30):

        num_iter      = 0

        NUM_ITER_MAX  = timeout

        POLL_INTERVAL = 1

        while (num_iter < NUM_ITER_MAX):

            completed=(self.read("*OPC?") == "1")

            if completed: break

            num_iter += 1

            time.sleep(POLL_INTERVAL)

        if num_iter == NUM_ITER_MAX:

            sys.exit(CfgError.ERRCODE_SYS_CMW_TIMEOUT)



    def read_state(self):

        curr_state = self.read("FETCh:LTE:SIGN:PSWitched:State?")

        self.wait_for_completion()

        return curr_state



    def insert_pause(self, tsec):

        logger = logging.getLogger('%s.insert_pause' % self.name)

        remaining_time = tsec

        sleep_time   = 5  if (tsec > 5) else 1

        logger.info("pause %s [sec]" % tsec)

        while (remaining_time > 0):

            logger.info("  remaining time : %s [sec]" % (remaining_time))

            time.sleep(sleep_time)

            remaining_time -= sleep_time



    def check_sw_version(self):

        logger=logging.getLogger("%s.check_sw_version" % self.name)



        check_l   = {'CMW_BASE':(3, 2, 50), 'CMW_LTE_Sig':(3, 2, 81), 'CMW_WCDMA_Sig':(3,2,50), 'CMW_GSM_Sig':(3,2,50), }

        verdict_d = {0:'PASS', 1:'FAIL', 2:'UNKNOWN'}



        cmwswinfo=self.read("SYSTem:BASE:OPTion:VERSion?")

        self.wait_for_completion()

        logger.debug("SYSTem:BASE:OPTion:VERSion? %s" % cmwswinfo)



        if not cmwswinfo:

            logger.warning("Failed retrieving CMW info. SW version may be incorrect")

            return 'None'



        result=[]

        for k,v in check_l.iteritems():

            verdict=2

            # Extract THE SW version string

            tmp=re.compile('%s,[v|V|x|X][0-9]+[.][0-9]+[.][0-9]+' % k)

            check_str=k

            if tmp.search(cmwswinfo):

                # here if string is detected

                check_str=(tmp.search(cmwswinfo)).group()

                # Extract the version number

                tmp=re.compile('[.0-9]+')

                xyz=((tmp.search(check_str)).group()).split('.')

                x=int(xyz[0])

                y=int(xyz[1])

                z=int(xyz[2])

                if ((x>v[0]) or (x==v[0] and y>v[1]) or (x==v[0] and y==v[1] and z>=v[2])):

                    verdict=0

                else:

                    verdict=1

                    logger.error("Incorrect SW version %s. Required v%s.%s.%s or later" % (check_str, v[0], v[1], v[2]))

                    sys.exit(CfgError.ERRCODE_SYS_CMW_INCORRECT_SW_VERSION)

            else:

                verdict=2

            logger.info("%s check point ...%s" % (check_str, verdict_d[verdict]))

            result.append(check_str)



        testerinfo = ' '.join(result)

        #result  = [x.replace(',', '_') for x in cmwinfo]



        return testerinfo



    #======================================================================

    # DEBUG functionalities

    #======================================================================

    def scpi_monitor_start(self):

        self.write("TRACe:REMote:MODE:DISPlay:ENABle ANALysis")

        self.write("TRACe:REMote:MODE:DISPlay:CLEar")

        self.write("TRACe:REMote:MODE:DISPlay:ENABle ON")

        self.insert_pause(5)

        self.write("TRACe:REMote:MODE:DISPlay:ENABle LIVE")



    def scpi_monitor_stop(self):

        self.write("TRACe:REMote:MODE:DISPlay:ENABle OFF")

        #if 1: self.write("TRACe:REMote:MODE:DISPlay:CLEar")

        #raw_input("scpi_monitor_stop: Checkpoint")



    def scpi_error_count(self):

        tmp=self.write("SYSTem:ERRor:COUNt?")

        return tmp



    def scpi_error_queue(self):

        err_queue=self.write("SYSTem:ERRor:ALL?")

        print "ERROR QUEUE : %s" % err_queue



    def scpi_monitor_clear(self):

        self.write("TRACe:REMote:MODE:DISPlay:ENABle ANALysis")

        self.write("TRACe:REMote:MODE:DISPlay:CLEar")

        self.write("TRACe:REMote:MODE:DISPlay:ENABle OFF")

        self.insert_pause(5)



    #======================================================================

    # External fader functions

    #======================================================================

    def external_fader_scenario_siso(self, route_conf):

        self.write(r'ROUTe:LTE:SIGN:SCENario:SCFading %s' % route_conf)



    def external_fader_scenario(self, route_conf):

        self.write(r'ROUTe:LTE:SIGN:SCENario:TROFading:EXTernal %s' % route_conf)



    def digiIQin_conf(self, path_index, pep, lev):

        self.write(r'SENSe:LTE:SIGN:IQOut:PATH%s?' % path_index)

        self.write(r'CONFigure:LTE:SIGN:IQIN:PATH%s %s, %s' % (path_index, pep, lev))





if __name__ == '__main__':
    anr=Anr('MT8820C','10.21.141.234')
    #anr.write('*IDN?')
    #anr.read('*IDN?')
    print anr.ask('*IDN?')
    anr.write('CALLSA')
    print anr.ask('*ESR?')
    anr.close()
    #pass