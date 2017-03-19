@echo off
rem  Use this batch file to run the Brewer software without a Brewer
rem  connected.  DO NOT USE with Brewer connected since motors may
rem  move improperly.

rem ****************************************************************************
rem Use the variables in this section to configure the execution of the program
rem ****************************************************************************
rem Use NOBREW=1 if the brewer is not connected
set NOBREW=1
rem BREWER_PROGRAM indicates the brewer program folder in which the main.asc file is contained
set BREWER_PROGRAM=C:\GWBasic_Interpreter\brw#193\Program
rem MAIN_FILE is the name of the main GW-Basic file
set MAIN_FILE=main.asc
rem BREWER_BDATA indicates the brewer bdata folder
set BREWER_BDATA=C:\GWBasic_Interpreter\brw#193\bdata193
rem COM_PORT is the identifier of the port in which the brewer is connected
set COM_PORT=COM7
rem PCBASIC_PATH is the path in which the pcbasic.py file is located
set PCBASIC_PATH=C:\GWBasic_Interpreter\pcbasic_brewer
rem PYTHON_DIR is the folder in which the python.exe is located
set PYTHON_DIR=C:\Users\pandora\Anaconda2
rem ADDITIONAL_OPTIONS set other options that are desired to be used (for example, ADDITIONAL_OPTIONS="-f=10 --debug")
set ADDITIONAL_OPTIONS="-f=10 --max-memory=67108864"

rem ############################################################################
rem ############################################################################
rem ############################################################################
rem ############################################################################

rem ****************************************************************************
rem Do not change anything below this line
rem ****************************************************************************

REM set PATH=%PATH%;C:\Program Files (x86)\PC-BASIC

rem Set the BREWDIR enviroment variable: where to find the main.asc respect the pcbasic mounted drives (full path)
set BREWDIR=C:\

rem Set the NOBREW enviroment variable: 
set NOBREW=%NOBREW%

rem save the current dir, to restore on exit
set CURR_DIR=%CD%

rem * Change the current path to the Brewer program directory to ensure correct operation (full path)
cd %BREWER_PROGRAM%

rem * Change the prompt as a reminder that the Brewer software is running
PROMPT Brewer $P$G

@echo on
rem * Run the Brewer software
%PCBASIC_PATH%\ansipipe-launcher.exe %PYTHON_DIR%\python.exe %PCBASIC_PATH%\pcbasic.py %MAIN_FILE% --mount=C:%BREWER_PROGRAM%,D:%BREWER_BDATA% --quit=False --interface=ansi %ADDITIONAL_OPTIONS%



rem * On exit, undo the changes what were done above
PROMPT $P$G
set BREWDIR=
set NOBREW=
cd %CURR_DIR%
ECHO "Have a nice day!"