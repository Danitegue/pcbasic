@echo off
rem  Use this batch file to run the Brewer software without a Brewer
rem  connected.

rem ****************************************************************************
rem Use the variables in this section to configure the execution of the program
rem ****************************************************************************

rem PCBASIC_PATH is the path in which the pcbasic.py file is located
set PCBASIC_PATH=C:\PCBasic_Brewer_Repo\pcbasic_brewer

rem PYTHON_DIR is the folder in which the python.exe is located
set PYTHON_DIR=C:\Users\DS_Pandora\Anaconda2

rem Set the folder to mount as unit C: (For Brewer soft, we are going to mount the folder where the main.asc BASIC program is as C:)
set MOUNT_C=C:\PCBasic_Brewer_Repo\brw#185\Program

rem Set the folder to mount as unit D: (For brewer soft, we are going to mount the bdata folder as unit D:)
set MOUNT_D=C:\PCBasic_Brewer_Repo\brw#185\bdata185

rem Set the name of the BASIC program to run (For brewer soft, main.asc)
set PROGRAM=main.asc




rem ****************************************************************************
rem Do not change anything below this line
rem ****************************************************************************

rem Set the NOBREW enviroment variable: If NOBREW=1 the brewer program will run in offline mode (No COM port communications).
set NOBREW=1

rem Set the BREWDIR enviroment variable: where to find the main.asc respect the pcbasic mounted drives (full path)
set BREWDIR=C:\

rem save the current dir, to restore on exit
set CURR_DIR=%CD%

rem * Change the current path to the Brewer program directory to ensure correct operation (full path)
cd %MOUNT_C%

rem * Change the prompt as a reminder that the Brewer software is running
PROMPT Brewer $P$G

@echo on
rem * Run the Brewer software
%PCBASIC_PATH%\ansipipe-launcher.exe %PYTHON_DIR%\python.exe %PCBASIC_PATH%\run.py --mount=C:%MOUNT_C%,D:%MOUNT_D% --interface=ansi --run=%PROGRAM% --quit=False -f=10 --double=True --logfile=C:\Temp\pcbasic_brewer_log.txt 



rem * On exit, undo the changes what were done above
PROMPT $P$G
REM set BREWDIR=
REM set NOBREW=
cd %CURR_DIR%
ECHO "Have a nice day!"