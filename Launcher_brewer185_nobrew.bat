@echo off
rem ****************************************************************************
rem Use the variables in this section to configure the execution of the Brewer program
rem ****************************************************************************

rem PCBASIC_PATH is the path in which the run.py file is located
set PCBASIC_PATH=C:\PCBasic_Brewer_Repo\pcbasic_brewer

rem PYTHON_DIR is the folder in which the python.exe is located
set PYTHON_DIR=C:\Users\DS_Pandora\Anaconda2

rem Set the folder to mount as unit C: (For Brewer soft, C: must be C: Otherwise SHELL commands won't work.)
set MOUNT_C=C:\

rem Set the folder to mount as unit D: (For Brewer soft, D: must be D: Otherwise SHELL commands won't work.)(Empty if not needed)
set MOUNT_D=

rem Set the name of the BASIC program to run (For brewer soft, main.asc)
set PROGRAM=main.asc

rem Set the LOG_DIR in order to write the pcbasic session log.
set LOG_DIR=C:\Temp

rem Set the BREWDIR enviroment variable: where to find the main.asc respect the pcbasic mounted drives (full path)
set BREWDIR=C:\PCBasic_Brewer_Repo\brw#185\Program

rem Set the NOBREW enviroment variable: If NOBREW=1 the brewer program will run in offline mode (No COM port communications).
set NOBREW=1


rem ****************************************************************************
rem Do not change anything below this line
rem ****************************************************************************

rem save the current dir, to restore on exit
set CURR_DIR=%CD%

rem * Change the current path to the Brewer program directory to ensure correct operation (full path)
cd %BREWDIR%

rem * Change the prompt as a reminder that the Brewer software is running
PROMPT Brewer $P$G

@echo on
rem * Run the Brewer software
%PCBASIC_PATH%\ansipipe-launcher.exe %PYTHON_DIR%\python.exe %PCBASIC_PATH%\run.py --mount=C:%MOUNT_C%,D:%MOUNT_D% --interface=ansi --run=%PROGRAM% --quit=False -f=10 --shell=cmd.exe --logfile=%LOG_DIR%\pcbasic_brewer_log.txt



rem * On exit, undo the changes what were done above
PROMPT $P$G
REM set BREWDIR=
REM set NOBREW=
cd %CURR_DIR%
ECHO "Have a nice day!"