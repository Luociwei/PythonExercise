#!/bin/env python
# -*- coding: cp1252 -*-
#==========================================================================
# (c) 2015 Texas Instruments
#--------------------------------------------------------------------------
# Project : Methods and parameters for reading and writing hardware registers
# File    : device_rw.py
#--------------------------------------------------------------------------
# Redistribution and use of this file in source and binary forms, with
# or without modification, are permitted.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#==========================================================================

#==========================================================================
# IMPORTS
#==========================================================================
import sys
import time
from array import array, ArrayType


#==========================================================================
# CONSTANTS
#==========================================================================
CC_NOT_ZERO = '!CMD'
CC_ZERO = 0


#==========================================================================
# FUNCTIONS
#==========================================================================
def hw_sleep_ms(time_msec):
    '''
    this function is copied from other official file
    '''
    time.sleep(time_msec / 1000.0)


def write_reg(hw_handle, register, data_):
    # dummy read of MODE reg in case device is asleep
    hw_handle.write_reg(register, data_)


def write_reg_4cc(hw_handle, register, data_str):
    # i.e. write_reg_4cc(handle, 0x08, 'FLrr')
    data_out = array('B')
    data_out.fromstring(data_str)
    write_reg (hw_handle, register, data_out)


def read_reg(hw_handle, register, length):
    # dummy read of MODE reg in case device is asleep
    return hw_handle.read_reg(register, length)


def read_reg_4cc(hw_handle, register):
    return read_reg(hw_handle, register, 5)



#==========================================================================
# main
#==========================================================================


if __name__ == "__main__":
    print "This file contains helper functions related to reading and writing"
    print "device registers and is not intended to be run stand alone. To use,"
    print "import constituent functions into a script or python environment using:"
    print "from device_rw import *"
    sys.exit()

