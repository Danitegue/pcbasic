# -*- coding: utf-8 -*-

#Daniel Santana, 20180321.

#This script emulates the shell commands actions that the brewer software sends to the operative system.

#Example of use in cmd: python Brewerfunctions.py md C:\Temporal\Newfolder
#This will build a new folder but using python code instead of system calls.

#If in the BASIC code there is a line: SHELL "md C:\Temporal\Newfolder"
#and PCBASIC is executed with the --shell="python C:\...\Brewerfunctions.py" option in the launcher
#PCBASIC will make the system call: "python Brewerfunctions.py md C:\Temporal\Newfolder"
#And this script will do the needed actions depending of the arguments contents.

#Script arguments:
#sys.argv[0] This is the name of the script: Brewerfunctions.py
#sys.argsv[1] This is the first argument after the name of the script: md
#sys.argsv[1:] This give a list with all the arguments incluedad after the name of the script: [md,C:\Temporal\Newfolder]
#This last one is what we analyze here.

import sys
import os
import datetime
import time




arguments=sys.argv[1:] #Get the list of arguments
if "/C" in arguments[0]: arguments=arguments[1:] #Delete the /C command that PCBASIC adds by default.
command = ' '.join(arguments) #Build a command line string
command = str(command.replace('\r', '\\r').replace('\n', '\\n'))
#print str(arguments)


#--------------Emulating functions-------------
def shell_copy(orig, dest):
    #Emulate the old win32 behavior of the shell copy function:
    sys.stdout.write("Brewerfunctions.py, shell_copy, emulating command: "+command +"\r\n")
    if "+" in orig:
        # Case: 'copy file1+file2 destination'
        files_to_append = orig.split("+")
        dest_temp=dest+".tmp"
        if os.path.exists(files_to_append[0]): #This will raise an error if file1 does not exist.
            ft = open(dest_temp, "wb")  #This will create a new temporal destination file.
            for path_i in files_to_append:
                if os.path.exists(path_i): #This will skip file2 if it does not exist without errors, like win32 behavior.
                    fi = open(path_i, "rb")
                    ft.write(fi.read())
                    fi.close()
            ft.close()
            ft = open(dest_temp, "rb")
            fd = open(dest, "wb") #This will remove the old contents of the file, it it exist.
            fd.write(ft.read())
            fd.close(); ft.close()
            os.remove(dest_temp) #Remove the temporal file.

        else:
            sys.stdout.write("Cannot copy file1 because it doesn't exist."+"\r\n")
    else:
        # Case: 'copy file1 destination':
        if os.path.exists(orig): #This will raise an error if file1 does not exist.
            dest_temp = dest + ".tmp"
            fs = open(orig, "rb")
            ft = open(dest_temp, "wb") #This will create the destination file.
            ft.write(fs.read())
            fs.close();ft.close()
            ft = open(dest_temp, "rb")
            fd = open(dest, "wb")  # This will remove the old contents of the file, if it exist.
            fd.write(ft.read())
            fd.close(); ft.close()
            os.remove(dest_temp)  # Remove the temporal file.
        else:
            sys.stdout.write("Cannot copy file1 because it doesn't exist."+"\r\n")

def shell_mkdir(dir):
    #Create a directory:
    sys.stdout.write("Brewerfunctions.py, shell_mkdir, emulating command: " + command+ "\r\n")
    os.makedirs(dir)

def shell_setdate():
    #This function changes the date in the bdata\###\OP_ST.### file.
    sys.stdout.write("Brewerfunctions.py, shell_setdate, emulating command: " + command+ "\r\n")

    #Read bdata path and instrument info from OP_ST.FIL:
    program_dir = os.environ['BREWDIR']
    opstfil_dir = os.path.join(os.path.realpath(program_dir), 'OP_ST.FIL')
    f = open(opstfil_dir, 'r')
    opstfil_content=f.read()
    f.close()
    instr_number = opstfil_content.split()[0]
    bdata_dir=opstfil_content.split()[1]

    #Build the data/###/OP_ST.### dir
    opstinstr_dir = os.path.join(os.path.realpath(bdata_dir),str(instr_number),'OP_ST.'+str(instr_number))
    opstinstr_bak_dir = os.path.join(os.path.realpath(bdata_dir), str(instr_number), 'OP_ST_bak.' + str(instr_number))

    #Create a backup of the OP_ST.### first. (OP_ST_bak.###)
    shell_copy(opstinstr_dir,opstinstr_bak_dir)

    #Open OP_ST.###
    f=open(opstinstr_dir,'rb');c0 = f.read();f.close() #read Contents. In binary mode for being able to detect the EOF if exist.
    #Detect carriage return type
    if "\r\n" in c0:
        cr="\r\n"
    elif "\n" in c0:
        cr = "\n"
    elif "\r" in c0:
        cr = "\r"
    cs = c0.rsplit(cr)
    #Modify content: Update the date
    date=datetime.datetime.now()
    cs[6]=str(date.day).zfill(2) #Set Day 'DD'
    cs[7]=str(date.month).zfill(2)#Set Month 'MM'
    cs[8]=str(date.year)[-2:] #Set Year 'YY'
    cs[23]='1' #Set A\D Board to '1'.
    c1=cr.join(cs)
    f = open(opstinstr_dir,'wb');f.write(c1); f.close() #Re-Build the modified file



def shell_noeof(file):
    sys.stdout.write("Brewerfunctions.py, shell_noeof, emulating command: " + command+ "\r\n")
    #This function create a copy of file without EOF ('0x1a') characters, into tmp.tmp
    #'noeof.exe filename'
    fin_dir=file #Usually a bdata dir.
    fout_dir=os.path.join(os.environ['BREWDIR'],"tmp.tmp") #Into program dir.
    if os.path.exists(fin_dir):
        fi=open(fin_dir,'rb') #Binary open for being able to detect the EOF char
        fo=open(fout_dir,'wb')
        while True:
            char=fi.read(1)
            if not char: break
            if char == '\x1a': continue
            fo.write(char)
        fi.close()
        fo.close()
    else:
        sys.stdout.write("File not found: "+str(fin_dir)+ "\r\n")


def shell_append(file1,file2):
    #Append files: 'append file1 file2'
    sys.stdout.write("Brewerfunctions.py, shell_append, emulating command: " + command+ "\r\n")
    copytemp=os.path.join(os.environ['BREWDIR'],"copy.tmp")
    tmptmp=os.path.join(os.environ['BREWDIR'],"copy.tmp")
    if not os.path.isfile(file2):
        shell_copy(file1, file2)
    else:
        shell_copy(file2+'+'+file1,os.path.join(os.environ['BREWDIR'],"copy.tmp"))
        shell_noeof(copytemp) # The resultant file will be on tmp.tmp
        shell_copy(tmptmp, file2)
        os.remove(copytemp)
        os.remove(tmptmp)




#Missing functions:
#ND.rtn -> SHELL 'format a:'
#NC.rtn -> SHELL"n
#TD.rtn -> SHELL("cmd /C")


#---------------------------------------------
#Evaluate the contents of the first argument of the SHELL call:

if "copy" in arguments[0].lower(): #Example 'copy file1+file2 destination' or 'copy file1 destination'
    shell_copy(arguments[1],arguments[2])

elif "md" in arguments[0].lower(): #Example 'md C:\Temporal\Newfolder'
    shell_mkdir(arguments[1])

elif "setdate" in arguments[0].lower(): #Example 'setdate.exe'
    shell_setdate()

elif "noeof" in arguments[0].lower(): #Example 'noeof filename'
    shell_noeof(arguments[1])

else:
    sys.stdout.write("Brewerfunctions.py, Ignored unrecognized shell command: "+ command+ "\r\n")

