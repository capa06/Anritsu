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

