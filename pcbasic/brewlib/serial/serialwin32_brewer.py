#! python
# Python Serial Port Extension for Win32, Linux, BSD, Jython
# serial driver for win32
# see __init__.py
#
# (C) 2001-2011 Chris Liechti <cliechti@gmx.net>
# this is distributed under a free software license, see license.txt
#
# Initial patch to use ctypes by Giovanni Bajo <rasky@develer.com>
#
# On 2015 - Nestor Morales - Added some changes for using this module for operating Brewer spectrophotometers.
# On 20170806 - Daniel Santana - Ported the nestor changes to the recommended version of pyserial that pcbasic needs.
# From the old version:
# Replaced all self._port_handle by self.hComPort
# Replaced all self._overlapped_write by self._overlappedWrite
# Replaced all self._overlapped_read by self._overlappedRead
# Replaced all self.is_open by self._isOpen
# Renamed the nestor _reconfigure_port by _reconfigurePort
# Replaced function name in_waiting by inWaiting
# Corrected the read function.
# Replaced self.out_waiting() to self.outWaiting
# Replaced _write_timeout by _writeTiemout
# Replaced the _update_break_state by setBreak,
# Replaced the _update_rts_state by setRTS,
# Replaced the update_dtr_state by setDTR,
# Replaced the GetCommModemStatus by _GetCommModemStatus
# Renamed the cts to getCTS
# Renamed the dsr to getDSR
# Renamed the ri to getRI
# Renamed the cd to getCD
# Renamed set_buffer_size by setBufferSize
# Renamed the set_output_flow_control by setXON



import ctypes
#from serial import win32
from . import win32

#from serial.serialutil import *
from .serialutil import *


import time
from datetime import datetime
import sys
import logging
from ... import config
#import util
#import expressions
#import state
#import basictoken as tk
#import vartypes
#import config

# Retrieve pcbasic options to activate the verbose mode
c = config.get_unicode_argv()
if '--use-serial-brewer-verbose=True' in c:
    verbose = True
else:
    verbose = False

#Simulate_Brewer_connected = True
Simulate_Brewer_connected = False

def device(portnum):
    """Turn a port number into a device name"""
    return 'COM%d' % (portnum+1) # numbers are transformed to a string




#Import the original win32 serial module
#import serial
#from serial.serialutil import SerialBase, SerialException, to_bytes, portNotOpenError, writeTimeoutError


class Win32Serial(SerialBase):
    """Serial port implementation for Win32 based on ctypes."""

    BAUDRATES = (1200, 2400, 4800)
    #BAUDRATES = (50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800, 9600, 19200, 38400, 57600, 115200)

    def __init__(self, *args, **kwargs):
        self.hComPort = None
        self._overlappedRead = None
        self._overlappedWrite = None
        self._rtsToggle = False

        #Added for brewer connection diagnosis
        self.verbose = verbose

        self._rtsState = win32.RTS_CONTROL_ENABLE
        self._dtrState = win32.DTR_CONTROL_ENABLE


        SerialBase.__init__(self, *args, **kwargs)


    def open(self):
        """\
        Open port with current settings. This may throw a SerialException
        if the port cannot be opened.
        """
        if self.verbose:
            sys.stdout.write("Using SerialBrewer module for oppening communications\n")
        logging.info("Using SerialBrewer module for oppening communications")

        if self._port is None:
            raise SerialException("Port must be configured before it can be used.")
        if self._isOpen:
            raise SerialException("Port is already open.")
        # the "\\.\COMx" format is required for devices other than COM1-COM8
        # not all versions of windows seem to support this properly
        # so that the first few ports are used with the DOS device name
        port = self.name
        try:
            if port.upper().startswith('COM') and int(port[3:]) > 8:
                port = '\\\\.\\' + port
        except ValueError:
            # for like COMnotanumber
            pass
        self.hComPort = win32.CreateFile(port,
                win32.GENERIC_READ | win32.GENERIC_WRITE,
                0,  # exclusive access
                None,  # no security
                win32.OPEN_EXISTING,
                win32.FILE_ATTRIBUTE_NORMAL | win32.FILE_FLAG_OVERLAPPED,
                0)
        if self.hComPort == win32.INVALID_HANDLE_VALUE:
            self.hComPort = None    # 'cause __del__ is called anyway
            raise SerialException("could not open port %r: %r" % (self.portstr, ctypes.WinError()))

        try:
            self._overlappedRead = win32.OVERLAPPED()
            self._overlappedRead.hEvent = win32.CreateEvent(None, 1, 0, None)
            self._overlappedWrite = win32.OVERLAPPED()
            #~ self._overlappedWrite.hEvent = win32.CreateEvent(None, 1, 0, None)
            self._overlappedWrite.hEvent = win32.CreateEvent(None, 0, 0, None)

            # # Setup a 4k buffer
            # win32.SetupComm(self.hComPort, 4096, 4096)

            # Save original timeout values:
            self._orgTimeouts = win32.COMMTIMEOUTS()
            win32.GetCommTimeouts(self.hComPort, ctypes.byref(self._orgTimeouts))

            #This is going to be done afterwards, for each baudrate, in the tryConnection procedure.
            #self._reconfigurePort()

            # Clear buffers:
            # Remove anything that was there
            #win32.PurgeComm(self.hComPort,
            #         win32.PURGE_TXCLEAR | win32.PURGE_TXABORT |
            #         win32.PURGE_RXCLEAR | win32.PURGE_RXABORT)

            #-------------------------------------------------------------
            # Brewer Command Procedure - Look for the correct baudrate

            success = False
            for baudrate in self.BAUDRATES:
                self._baudrate = baudrate
                success = self.tryConnection()
                if success:
                    time.sleep(1)
                    win32.PurgeComm(self.hComPort,
                             win32.PURGE_TXCLEAR | win32.PURGE_TXABORT |
                             win32.PURGE_RXCLEAR | win32.PURGE_RXABORT)
                    break


            success_output = ""
            success_output += "************************\n"
            if (success):
                success_output += "Connection with Brewer Successful!(" + str(self.baudrate) + ")\n"
            else:
                success_output += "Communication with Brewer failed\n"
            success_output += "************************\n"

            if self.verbose:
                sys.stdout.write(success_output)
            logging.info(success_output)

        except:
            try:
                self._close()
            except:
                # ignore any exception when closing the port
                # also to keep original exception that happened when setting up
                pass
            self.hComPort = None
            raise
        else:
            self._isOpen = True


    def _reconfigurePort(self):
        """Set communication parameters on opened port."""
        if not self.hComPort:
            raise SerialException("Can only operate on a valid port handle")

        # win32.SetCommMask(self.hComPort, win32.EV_ERR)

        # Setup the connection info.
        # Get state and modify it:
        comDCB = win32.DCB()
        win32.GetCommState(self.hComPort, ctypes.byref(comDCB))
        comDCB.BaudRate = self._baudrate

        comDCB.fRtsControl = win32.RTS_CONTROL_ENABLE
        comDCB.fDtrControl = win32.DTR_CONTROL_ENABLE

        comDCB.ByteSize = 8
        comDCB.Parity = win32.NOPARITY
        comDCB.StopBits = win32.ONESTOPBIT

        comDCB.fBinary = 1  # Enable Binary Transmission
        # Char. w/ Parity-Err are replaced with 0xff (if fErrorChar is set to TRUE)

        comDCB.fOutxDsrFlow = self._dsrdtr
        comDCB.fOutX = self._xonxoff
        comDCB.fInX = self._xonxoff
        comDCB.fNull = 0
        comDCB.fErrorChar = 0
        comDCB.fAbortOnError = 0
        #comDCB.XonChar = serial.XON
        #comDCB.XoffChar = serial.XOFF
        comDCB.XonChar = XON
        comDCB.XoffChar = XOFF

        timeouts = win32.COMMTIMEOUTS()
        # ReadIntervalTimeout,ReadTotalTimeoutMultiplier,
        #  ReadTotalTimeoutConstant,WriteTotalTimeoutMultiplier,
        #  WriteTotalTimeoutConstant

        timeouts.ReadIntervalTimeout = 0 #win32.MAXDWORD
        timeouts.ReadTotalTimeoutMultiplier = 0
        timeouts.ReadTotalTimeoutConstant = 0
        timeouts.WriteTotalTimeoutMultiplier = 0
        timeouts.WriteTotalTimeoutConstant = 0
        win32.SetCommTimeouts(self.hComPort, ctypes.byref(timeouts))

        if not win32.SetCommState(self.hComPort, ctypes.byref(comDCB)):
            raise SerialException("Cannot configure port, something went wrong. Original message: %r" % ctypes.WinError())

        # if not self.hComPort:
        #     raise SerialException("Can only operate on a valid port handle")
        #
        # # Set Windows timeout values
        # # timeouts is a tuple with the following items:
        # # (ReadIntervalTimeout,ReadTotalTimeoutMultiplier,
        # #  ReadTotalTimeoutConstant,WriteTotalTimeoutMultiplier,
        # #  WriteTotalTimeoutConstant)
        # timeouts = win32.COMMTIMEOUTS()
        # # ReadIntervalTimeout,ReadTotalTimeoutMultiplier,
        # #  ReadTotalTimeoutConstant,WriteTotalTimeoutMultiplier,
        # #  WriteTotalTimeoutConstant
        #
        # timeouts.ReadIntervalTimeout = win32.MAXDWORD
        # timeouts.ReadTotalTimeoutMultiplier = 0
        # timeouts.ReadTotalTimeoutConstant = 0
        # timeouts.WriteTotalTimeoutMultiplier = 0
        # timeouts.WriteTotalTimeoutConstant = 0
        # win32.SetCommTimeouts(self.hComPort, ctypes.byref(timeouts))
        # # timeouts = win32.COMMTIMEOUTS()
        # # if self._timeout is None:
        # #     pass  # default of all zeros is OK
        # # elif self._timeout == 0:
        # #     timeouts.ReadIntervalTimeout = win32.MAXDWORD
        # # else:
        # #     timeouts.ReadTotalTimeoutConstant = max(int(self._timeout * 1000), 1)
        # # if self._timeout != 0 and self._inter_byte_timeout is not None:
        # #     timeouts.ReadIntervalTimeout = max(int(self._inter_byte_timeout * 1000), 1)
        # #
        # # if self._writeTimeout is None:
        # #     pass
        # # elif self._writeTimeout == 0:
        # #     timeouts.WriteTotalTimeoutConstant = win32.MAXDWORD
        # # else:
        # #     timeouts.WriteTotalTimeoutConstant = max(int(self._writeTimeout * 1000), 1)
        # # win32.SetCommTimeouts(self.hComPort, ctypes.byref(timeouts))
        #
        # win32.SetCommMask(self.hComPort, win32.EV_ERR)
        #
        # # Setup the connection info.
        # # Get state and modify it:
        # comDCB = win32.DCB()
        # win32.GetCommState(self.hComPort, ctypes.byref(comDCB))
        # comDCB.BaudRate = self._baudrate
        #
        # if self._bytesize == serial.FIVEBITS:
        #     comDCB.ByteSize = 5
        # elif self._bytesize == serial.SIXBITS:
        #     comDCB.ByteSize = 6
        # elif self._bytesize == serial.SEVENBITS:
        #     comDCB.ByteSize = 7
        # elif self._bytesize == serial.EIGHTBITS:
        #     comDCB.ByteSize = 8
        # else:
        #     raise ValueError("Unsupported number of data bits: %r" % self._bytesize)
        #
        # if self._parity == serial.PARITY_NONE:
        #     comDCB.Parity = win32.NOPARITY
        #     comDCB.fParity = 0  # Disable Parity Check
        # elif self._parity == serial.PARITY_EVEN:
        #     comDCB.Parity = win32.EVENPARITY
        #     comDCB.fParity = 1  # Enable Parity Check
        # elif self._parity == serial.PARITY_ODD:
        #     comDCB.Parity = win32.ODDPARITY
        #     comDCB.fParity = 1  # Enable Parity Check
        # elif self._parity == serial.PARITY_MARK:
        #     comDCB.Parity = win32.MARKPARITY
        #     comDCB.fParity = 1  # Enable Parity Check
        # elif self._parity == serial.PARITY_SPACE:
        #     comDCB.Parity = win32.SPACEPARITY
        #     comDCB.fParity = 1  # Enable Parity Check
        # else:
        #     raise ValueError("Unsupported parity mode: %r" % self._parity)
        #
        # if self._stopbits == serial.STOPBITS_ONE:
        #     comDCB.StopBits = win32.ONESTOPBIT
        # elif self._stopbits == serial.STOPBITS_ONE_POINT_FIVE:
        #     comDCB.StopBits = win32.ONE5STOPBITS
        # elif self._stopbits == serial.STOPBITS_TWO:
        #     comDCB.StopBits = win32.TWOSTOPBITS
        # else:
        #     raise ValueError("Unsupported number of stop bits: %r" % self._stopbits)
        #
        # comDCB.fBinary = 1  # Enable Binary Transmission
        # # Char. w/ Parity-Err are replaced with 0xff (if fErrorChar is set to TRUE)
        # if self._rs485_mode is None:
        #     if self._rtscts:
        #         comDCB.fRtsControl = win32.RTS_CONTROL_HANDSHAKE
        #     else:
        #         comDCB.fRtsControl = win32.RTS_CONTROL_ENABLE if self._rtsState else win32.RTS_CONTROL_DISABLE
        #     comDCB.fOutxCtsFlow = self._rtscts
        # else:
        #     # checks for unsupported settings
        #     # XXX verify if platform really does not have a setting for those
        #     if not self._rs485_mode.rts_level_for_tx:
        #         raise ValueError(
        #                 'Unsupported value for RS485Settings.rts_level_for_tx: %r' % (
        #                     self._rs485_mode.rts_level_for_tx,))
        #     if self._rs485_mode.rts_level_for_rx:
        #         raise ValueError(
        #                 'Unsupported value for RS485Settings.rts_level_for_rx: %r' % (
        #                     self._rs485_mode.rts_level_for_rx,))
        #     if self._rs485_mode.delay_before_tx is not None:
        #         raise ValueError(
        #                 'Unsupported value for RS485Settings.delay_before_tx: %r' % (
        #                     self._rs485_mode.delay_before_tx,))
        #     if self._rs485_mode.delay_before_rx is not None:
        #         raise ValueError(
        #                 'Unsupported value for RS485Settings.delay_before_rx: %r' % (
        #                     self._rs485_mode.delay_before_rx,))
        #     if self._rs485_mode.loopback:
        #         raise ValueError(
        #                 'Unsupported value for RS485Settings.loopback: %r' % (
        #                     self._rs485_mode.loopback,))
        #     comDCB.fRtsControl = win32.RTS_CONTROL_TOGGLE
        #     comDCB.fOutxCtsFlow = 0
        #
        # if self._dsrdtr:
        #     comDCB.fDtrControl = win32.DTR_CONTROL_HANDSHAKE
        # else:
        #     comDCB.fDtrControl = win32.DTR_CONTROL_ENABLE if self._dtrState else win32.DTR_CONTROL_DISABLE
        # comDCB.fOutxDsrFlow = self._dsrdtr
        # comDCB.fOutX = self._xonxoff
        # comDCB.fInX = self._xonxoff
        # comDCB.fNull = 0
        # comDCB.fErrorChar = 0
        # comDCB.fAbortOnError = 0
        # comDCB.XonChar = serial.XON
        # comDCB.XoffChar = serial.XOFF
        #
        # if not win32.SetCommState(self.hComPort, ctypes.byref(comDCB)):
        #     raise SerialException("Cannot configure port, something went wrong. Original message: %r" % ctypes.WinError())

    #~ def __del__(self):
        #~ self.close()

    # def tryMultipleConnections(self, port):
    #     baudrates = [ 1200, 300, 9600 ]
    #     for baudrate in baudrates:
    #         print "Testing baudrate ", baudrate
    #         self._baudrate = baudrate
    #         if (self.tryConnection(baudrate, port)):
    #             return True

    def tryConnection(self):
        # if not self.hComPort:
        #     raise SerialException("Can only operate on a valid port handle")
        #
        # # win32.SetCommMask(self.hComPort, win32.EV_ERR)
        #
        # # Setup the connection info.
        # # Get state and modify it:
        # comDCB = win32.DCB()
        # win32.GetCommState(self.hComPort, ctypes.byref(comDCB))
        # comDCB.BaudRate = self._baudrate
        #
        # comDCB.fRtsControl = win32.RTS_CONTROL_DISABLE
        # comDCB.fDtrControl = win32.DTR_CONTROL_DISABLE
        #
        # comDCB.ByteSize = 8
        # comDCB.Parity = win32.NOPARITY
        # comDCB.StopBits = win32.ONESTOPBIT
        #
        # comDCB.fBinary = 1  # Enable Binary Transmission
        # # Char. w/ Parity-Err are replaced with 0xff (if fErrorChar is set to TRUE)
        #
        # comDCB.fOutxDsrFlow = self._dsrdtr
        # comDCB.fOutX = self._xonxoff
        # comDCB.fInX = self._xonxoff
        # comDCB.fNull = 0
        # comDCB.fErrorChar = 0
        # comDCB.fAbortOnError = 0
        # comDCB.XonChar = serial.XON
        # comDCB.XoffChar = serial.XOFF
        #
        # timeouts = win32.COMMTIMEOUTS()
        # # ReadIntervalTimeout,ReadTotalTimeoutMultiplier,
        # #  ReadTotalTimeoutConstant,WriteTotalTimeoutMultiplier,
        # #  WriteTotalTimeoutConstant
        #
        # timeouts.ReadIntervalTimeout = win32.MAXDWORD
        # timeouts.ReadTotalTimeoutMultiplier = 0
        # timeouts.ReadTotalTimeoutConstant = 0
        # timeouts.WriteTotalTimeoutMultiplier = 0
        # timeouts.WriteTotalTimeoutConstant = 0
        # win32.SetCommTimeouts(self.hComPort, ctypes.byref(timeouts))
        #
        # if not win32.SetCommState(self.hComPort, ctypes.byref(comDCB)):
        #     raise SerialException("Cannot configure port, something went wrong. Original message: %r" % ctypes.WinError())

        self._reconfigurePort()

        success = False
        for test_number in range(1,6):
            if self.verbose:
                sys.stdout.write("Trying communication (%d), attempt #%d -> \n" % (self.baudrate, test_number))
                logging.info("Trying communication (%d), attempt #%d -> " % (self.baudrate, test_number))

            # Initial test: prompt found? ("->")
            response = self.check_brewer_communication()
            if not response==True:
                if self.verbose:
                    sys.stdout.write("Test "+str(test_number)+" failed\r")
                    logging.info("Test "+str(test_number)+" failed")
                    time.sleep(1)
                continue
            else:
                return True

            success = self.check_brewer_id()

        return False



    def check_brewer_communication(self):
        t1 = datetime.now()
        #self.write('\r\r\r\r')
        self.write('\r')
        ReadWhile = 5.0 #seconds
        input_string = ""
        answ_key = False
        answ_timeout = False
        while ((not answ_key) and (not answ_timeout)):
            t2 = datetime.now()
            elapsed=float((t2-t1).seconds)
            #while(((datetime.now() - t1).microseconds / 1.0e6) < ReadWhile):
            if elapsed < ReadWhile:
                if (self.inWaiting != 0):
                    input_string += self.read(self.inWaiting)
                    #print "received",str(input_string)
                    if  (input_string.find("->") > 0):
                        answ_key = True
                    else:
                        time.sleep(0.1)
            else:
                print "No key received after ", ReadWhile, 'seconds.'
                answ_timeout = True


        if Simulate_Brewer_connected:
            print "Simulating a brewer connected..."
            return True

        # If prompt is found, return true
        if (input_string.find("->") != -1):
            return True
        else:
            print "No -> found in brewer answer:", str(input_string)
            return False

    def check_brewer_id(self):
        t1 = datetime.now()
        self.write('?BREWER.ID\r')
        # self.write('F,0,2:V,120,1\r')

        input_string = ""
        while((datetime.now() - t1).microseconds < 200000):
            if (self.inWaiting != 0):
                input_string += self.read(3)
            time.sleep(0.001)

        final_string = ''
        for c in input_string:
            if (ord(c) >= 48) and (ord(c) <= 57):
                final_string += c

        try:
            self._brewer_id = int(final_string)
        except:
            return False

        if self.verbose:
            sys.stdout.write("Communication with Brewer #%d completed\n" % self._brewer_id)
        logging.info("Communication with Brewer #%d completed" % self._brewer_id)

        return True

    def _close(self):
        """internal close port helper"""
        if self.hComPort:
            # Restore original timeout values:
            win32.SetCommTimeouts(self.hComPort, self._orgTimeouts)
            # Close COM-Port:
            win32.CloseHandle(self.hComPort)
            if self._overlappedRead is not None:
                win32.CloseHandle(self._overlappedRead.hEvent)
                self._overlappedRead = None
            if self._overlappedWrite is not None:
                win32.CloseHandle(self._overlappedWrite.hEvent)
                self._overlappedWrite = None
            self.hComPort = None

    def close(self):
        """Close port"""
        if self._isOpen:
            self._close()
            self._isOpen = False

    def makeDeviceName(self, port):
        return device(port)

    #  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -

    @property
    def inWaiting(self):
        """Return the number of bytes currently in the input buffer."""
        flags = win32.DWORD()
        comstat = win32.COMSTAT()
        if not win32.ClearCommError(self.hComPort, ctypes.byref(flags), ctypes.byref(comstat)):
            raise SerialException('call to ClearCommError failed')
        return comstat.cbInQue

    # read nestor
    # def read(self, size=1):
    #     """\
    #     Read size bytes from the serial port. If a timeout is set it may
    #     return less characters as requested. With no timeout it will block
    #     until the requested number of bytes is read."""
    #     if not self.hComPort:
    #         raise portNotOpenError
    #     if size > 0:
    #         win32.ResetEvent(self._overlappedRead.hEvent)
    #         flags = win32.DWORD()
    #         comstat = win32.COMSTAT()
    #         if not win32.ClearCommError(self.hComPort, ctypes.byref(flags), ctypes.byref(comstat)):
    #             raise SerialException('call to ClearCommError failed')
    #         n = min(comstat.cbInQue, size) if self.timeout == 0 else size
    #         if n > 0:
    #             buf = ctypes.create_string_buffer(n)
    #             rc = win32.DWORD()
    #             read_ok = win32.ReadFile(self.hComPort, buf, n, ctypes.byref(rc), ctypes.byref(self._overlappedRead))
    #             if not read_ok and (win32.GetLastError() != win32.ERROR_IO_PENDING):
    #                 raise SerialException("ReadFile failed (%r)" % ctypes.WinError())
    #             win32.GetOverlappedResult(self.hComPort, ctypes.byref(self._overlappedRead), ctypes.byref(rc), True)
    #             read = buf.raw[:rc.value]
    #         else:
    #             read = bytes()
    #     else:
    #         read = bytes()
    #
    #     return bytes(read)


    #read dani
    def read(self, size=1):
        """Read size bytes from the serial port. If a timeout is set it may
           return less characters as requested. With no timeout it will block
           until the requested number of bytes is read."""
        if not self.hComPort: raise portNotOpenError
        if size > 0:
            win32.ResetEvent(self._overlappedRead.hEvent)
            flags = win32.DWORD()
            comstat = win32.COMSTAT()
            if not win32.ClearCommError(self.hComPort, ctypes.byref(flags), ctypes.byref(comstat)):
                raise SerialException('call to ClearCommError failed')
            if self.timeout == 0:
                n = min(comstat.cbInQue, size)
                if n > 0:
                    buf = ctypes.create_string_buffer(n)
                    rc = win32.DWORD()
                    #If the win32.ReadFile function succeeds, the return value is nonzero (TRUE)
                    #If the function fails, or is completing asynchronously, the return value is zero (FALSE). To get extended error information, call the GetLastError function.
                    # This is giving an error. With win32.GetLastError we can see that is the error 997
                    # which means Overlapped I/O operation is in progress.

                    err = win32.ReadFile(self.hComPort, buf, n, ctypes.byref(rc), ctypes.byref(self._overlappedRead))
                    if err==0:
                        errcode=win32.GetLastError()
                        if errcode != win32.ERROR_IO_PENDING: #win32.ERROR_IO_PENDING=997
                            logging.warning("Got win32.GetLastError() = %s", str(errcode))
                            raise SerialException("ReadFile failed (%r)" % ctypes.WinError())

                    #win32.WaitForSingleObject will return a zero if the ovelapped function has finished.
                    err1 = win32.WaitForSingleObject(self._overlappedRead.hEvent, win32.INFINITE)

                    #Added by Dani on 20170808, if this is not present, the ctypes.byref(rc) is not updated when the overlapped
                    #operation is finished.
                    if not err1:
                        err2 = win32.GetOverlappedResult(self.hComPort, ctypes.byref(self._overlappedRead), ctypes.byref(rc),True)
                        #If the function succeeds, the return value is nonzero.
                        if err2 != 0:
                            #rc.value is zero, so the read is always empty.
                            read = buf.raw[:rc.value]
                        else:
                            logging.warning("Error in GetOverlappedResult = %s", str(err2))
                            read = bytes()
                    else:
                        logging.warning("Error in WaitForSingleObject = %s", str(err1))
                        read = bytes()

                else:
                    read = bytes()
            else:
                # case self.timeout != 0
                buf = ctypes.create_string_buffer(size)
                rc = win32.DWORD()
                err = win32.ReadFile(self.hComPort, buf, size, ctypes.byref(rc), ctypes.byref(self._overlappedRead))
                if err==0:
                    errcode = win32.GetLastError()
                    if errcode != win32.ERROR_IO_PENDING:  # win32.ERROR_IO_PENDING=997
                        logging.warning("Got win32.GetLastError() = %s", str(errcode))
                        raise SerialException("ReadFile failed (%r)" % ctypes.WinError())

                # win32.WaitForSingleObject will return a zero if the ovelapped function has finished.
                err1 = win32.WaitForSingleObject(self._overlappedRead.hEvent, self.timeout)

                if not err1:
                    err2 = win32.GetOverlappedResult(self.hComPort, ctypes.byref(self._overlappedRead), ctypes.byref(rc), True)
                    # If the function succeeds, the return value is nonzero.
                    if err2 != 0:
                        # rc.value is zero, so the read is always empty.
                        read = buf.raw[:rc.value]
                    else:
                        logging.warning("Error in GetOverlappedResult = %s", str(err2))
                        read = bytes()
                else:
                    logging.warning("Error in WaitForSingleObject = %s", str(err1))
                    read = bytes()
        else:
            logging.warning("Error, Bytes to read has to be > 0.")
            read = bytes()
        return bytes(read)




    def write(self, data):
        """Output the given byte string over the serial port."""
        
        #This was not commented in the nestor version, but is not present in the last serialwin32 version:
        self._writeTimeout = 0
        self.flush()

        if not self.hComPort: raise portNotOpenError
        #~ if not isinstance(data, (bytes, bytearray)):
            #~ raise TypeError('expected %s or bytearray, got %s' % (bytes, type(data)))
        # convert data (needed in case of memoryview instance: Py 3.1 io lib), ctypes doesn't like memoryview
        data = to_bytes(data)
        if data:
            win32.ResetEvent(self._overlappedWrite.hEvent)
            n = win32.DWORD()
            err = win32.WriteFile(self.hComPort, data, len(data), ctypes.byref(n), self._overlappedWrite)
            if not err:
                errcode = win32.GetLastError()
                if errcode != win32.ERROR_IO_PENDING:
                    logging.warning("win32.WriteFile failed, got error= %s", str(errcode))
                    raise SerialException("WriteFile failed (%r)" % ctypes.WinError())
                else:
                    # Wait for the write to complete.
                    win32.WaitForSingleObject(self._overlappedWrite.hEvent, win32.INFINITE)
                    # Retrieve the status of the object
                    err2 = win32.GetOverlappedResult(self.hComPort, self._overlappedWrite, ctypes.byref(n), True)
                    # If the function succeeds, the return value is nonzero.
                    if err2 == 0:
                        logging.warning('Got GetOverlappedResult error while retrieving the writting operation')

            if self._writeTimeout != 0:  # if blocking (None) or w/ write timeout (>0)
                # Wait for the write to complete.
                #~ win32.WaitForSingleObject(self._overlappedWrite.hEvent, win32.INFINITE)
                #GetOverlappedResult - If the function succeeds, the return value is nonzero
                err = win32.GetOverlappedResult(self.hComPort, self._overlappedWrite, ctypes.byref(n), True)

            if n.value != len(data):
                logging.warning("Error while writting, the number of bytes to send (%s) not the same of bytes sent (%s)",str(n.value), str(len(data)))
                raise writeTimeoutError
            return n.value
        else:
            return 0

    def flush(self):
        """Flush of file like objects. In this case, wait until all data
        is written."""
        while self.outWaiting:
            time.sleep(0.05)
        # XXX could also use WaitCommEvent with mask EV_TXEMPTY, but it would
        # require overlapped IO and its also only possible to set a single mask
        # on the port---

    #This is not present in the original werialwin32:
    def reset_input_buffer(self):
        """Clear input buffer, discarding all that is in the buffer."""
        if not self.hComPort:
            raise portNotOpenError
        win32.PurgeComm(self.hComPort, win32.PURGE_RXCLEAR | win32.PURGE_RXABORT)

    # This is not present in the original werialwin32:
    def reset_output_buffer(self):
        """\
        Clear output buffer, aborting the current output and discarding all
        that is in the buffer.
        """
        if not self.hComPort:
            raise portNotOpenError
        win32.PurgeComm(self.hComPort, win32.PURGE_TXCLEAR | win32.PURGE_TXABORT)

    # def _update_break_state(self):
    #     """Set break: Controls TXD. When active, to transmitting is possible."""
    #     if not self.hComPort:
    #         raise portNotOpenError
    #     if self._break_state:
    #         win32.SetCommBreak(self.hComPort)
    #     else:
    #         win32.ClearCommBreak(self.hComPort)
    
    def setBreak(self, level=1):
        """Set break: Controls TXD. When active, to transmitting is possible."""
        if not self.hComPort: raise portNotOpenError
        if level:
            win32.SetCommBreak(self.hComPort)
        else:
            win32.ClearCommBreak(self.hComPort)

    # def _update_rts_state(self):
    #     """Set terminal status line: Request To Send"""
    #     if self._rtsState:
    #         win32.EscapeCommFunction(self.hComPort, win32.SETRTS)
    #     else:
    #         win32.EscapeCommFunction(self.hComPort, win32.CLRRTS)

    def setRTS(self, level=1):
        """Set terminal status line: Request To Send"""
        # remember level for reconfigure
        if level:
            self._rtsState = win32.RTS_CONTROL_ENABLE
        else:
            self._rtsState = win32.RTS_CONTROL_DISABLE
        # also apply now if port is open
        if self.hComPort:
            if level:
                win32.EscapeCommFunction(self.hComPort, win32.SETRTS)
            else:
                win32.EscapeCommFunction(self.hComPort, win32.CLRRTS)



    # def _update_dtr_state(self):
    #     """Set terminal status line: Data Terminal Ready"""
    #     if self._dtrState:
    #         win32.EscapeCommFunction(self.hComPort, win32.SETDTR)
    #     else:
    #         win32.EscapeCommFunction(self.hComPort, win32.CLRDTR)

    def setDTR(self, level=1):
        """Set terminal status line: Data Terminal Ready"""
        # remember level for reconfigure
        if level:
            self._dtrState = win32.DTR_CONTROL_ENABLE
        else:
            self._dtrState = win32.DTR_CONTROL_DISABLE
        # also apply now if port is open
        if self.hComPort:
            if level:
                win32.EscapeCommFunction(self.hComPort, win32.SETDTR)
            else:
                win32.EscapeCommFunction(self.hComPort, win32.CLRDTR)

    # def _GetCommModemStatus(self):
    #     if not self.hComPort:
    #         raise portNotOpenError
    #     stat = win32.DWORD()
    #     win32.GetCommModemStatus(self.hComPort, ctypes.byref(stat))
    #     return stat.value
    
    def _GetCommModemStatus(self):
        stat = win32.DWORD()
        win32.GetCommModemStatus(self.hComPort, ctypes.byref(stat))
        return stat.value

    # @property
    # def cts(self):
    #     """Read terminal status line: Clear To Send"""
    #     return win32.MS_CTS_ON & self._GetCommModemStatus() != 0

    @property
    def getCTS(self):
        """Read terminal status line: Clear To Send"""
        if not self.hComPort: raise portNotOpenError
        return win32.MS_CTS_ON & self._GetCommModemStatus() != 0

    # @property
    # def dsr(self):
    #     """Read terminal status line: Data Set Ready"""
    #     return win32.MS_DSR_ON & self._GetCommModemStatus() != 0

    @property
    def getDSR(self):
        """Read terminal status line: Data Set Ready"""
        if not self.hComPort: raise portNotOpenError
        return win32.MS_DSR_ON & self._GetCommModemStatus() != 0

    # @property
    # def ri(self):
    #     """Read terminal status line: Ring Indicator"""
    #     return win32.MS_RING_ON & self._GetCommModemStatus() != 0

    @property
    def getRI(self):
        """Read terminal status line: Ring Indicator"""
        if not self.hComPort: raise portNotOpenError
        return win32.MS_RING_ON & self._GetCommModemStatus() != 0

    # @property
    # def cd(self):
    #     """Read terminal status line: Carrier Detect"""
    #     return win32.MS_RLSD_ON & self._GetCommModemStatus() != 0
    
    @property
    def getCD(self):
        """Read terminal status line: Carrier Detect"""
        if not self.hComPort: raise portNotOpenError
        return win32.MS_RLSD_ON & self._GetCommModemStatus() != 0

    # - - platform specific - - - -

    def setBufferSize(self, rx_size=4096, tx_size=None):
        """\
        Recommend a buffer size to the driver (device driver can ignore this
        value). Must be called before the port is opended.
        """
        if tx_size is None: tx_size = rx_size
        win32.SetupComm(self.hComPort, rx_size, tx_size)


    def setXON(self, level=True):
        """\
        Manually control flow - when software flow control is enabled.
        This will send XON (true) and XOFF (false) to the other device.
        WARNING: this function is not portable to different platforms!
        """
        if not self.hComPort: raise portNotOpenError
        if level:
            win32.EscapeCommFunction(self.hComPort, win32.SETXON)
        else:
            win32.EscapeCommFunction(self.hComPort, win32.SETXOFF)


    # def set_output_flow_control(self, enable=True):
    #     """\
    #     Manually control flow - when software flow control is enabled.
    #     This will do the same as if XON (true) or XOFF (false) are received
    #     from the other device and control the transmission accordingly.
    #     WARNING: this function is not portable to different platforms!
    #     """
    #     if not self.hComPort:
    #         raise portNotOpenError
    #     if enable:
    #         win32.EscapeCommFunction(self.hComPort, win32.SETXON)
    #     else:
    #         win32.EscapeCommFunction(self.hComPort, win32.SETXOFF)

    @property
    def outWaiting(self):
        """Return how many bytes the in the outgoing buffer"""
        flags = win32.DWORD()
        comstat = win32.COMSTAT()
        if not win32.ClearCommError(self.hComPort, ctypes.byref(flags), ctypes.byref(comstat)):
            raise SerialException('call to ClearCommError failed')
        return comstat.cbOutQue

    #This was not commented in the nestor code
    #def setBreak(self, value=1):
    #    return

    # This was not present in the nestor code
    # functions useful for RS-485 adapters
    def setRtsToggle(self, rtsToggle):
        """Change RTS toggle control setting."""
        self._rtsToggle = rtsToggle
        if self._isOpen: self._reconfigurePort()

    # This was not present in the nestor code
    def getRtsToggle(self):
        """Get the current RTS toggle control setting."""
        return self._rtsToggle

    # This was not present in the nestor code
    rtsToggle = property(getRtsToggle, setRtsToggle, doc="RTS toggle control setting")



# assemble Serial class with the platform specific implementation and the base
# for file-like behavior. for Python 2.6 and newer, that provide the new I/O
# library, derive from io.RawIOBase
try:
    import io
except ImportError:
    # classic version with our own file-like emulation
    class Serial(Win32Serial, FileLike):
        pass
else:
    # io library present
    class Serial(Win32Serial, io.RawIOBase):
        pass


# Nur Testfunktion!!
if __name__ == '__main__':
    s = Serial(0)
    sys.stdout.write("%s\n" % s)

    s = Serial()
    sys.stdout.write("%s\n" % s)

    s.baudrate = 19200
    s.databits = 7
    s.close()
    s.port = 0
    s.open()
    sys.stdout.write("%s\n" % s)

