################################################################
# Program: DNAscan - script to run DNAscan on a list of samples
# Version 1.0
# Author: Alfredo Iacoangeli (alfredo.iacoangeli@kcl.ac.uk)
#################################################################

################################################################
# Script structure:
# 1. Import python modules
# 2. Define paths_configs viriables
# 3. Define options from command line
# 4. Parse options from command line
# 5. Run DNAscan for each line in the input sample list
#   5.1 Create create DNAscan input file option string per line in the input list
#   5.2 Create working dir tree
#   5.3 Run DNAscan for one sample
################################################################

import argparse, os, os.path, random, string, time
import paths_configs

from argparse import RawTextHelpFormatter
from subprocess import Popen, PIPE, call
from string import Template

def multisubprocess(commandline, thrNum, waitProcess=True, execute=True, logFile=None, generateTmp = False):
    tempFile=os.path.join(os.path.realpath(__file__).rsplit('/', 2)[0], 'tmp')
    if generateTmp:
        if not os.path.exists(tempFile):
            os.makedirs(tempFile)
    try:
        processes = [i+100 for i in range(thrNum)]
        #print(commandline)
        thrNumGPU = [i for i in range(thrNum)]
        if execute:
            while len(commandline) !=0:
                time.sleep(1)
                statusProcess=0
                for i in range(len(processes)):
                    if not isinstance(processes[i], int):
                        if processes[i].poll()!=0:
                            statusProcess=statusProcess + 1
                        else:
                            thrNumGPU.append(i)
                if statusProcess < thrNum:
                    runNow=[]
                    for i in range(thrNum - statusProcess):
                        if len(commandline)==0:
                            break
                        runNow.append(commandline.pop(0))
                    for cmd in runNow:
                        randomStr=''.join(random.choice(string.ascii_letters+string.digits) for i in range(100))   
                        #print('Start Command: ' + repr(cmd) + '\n\n')
                        if logFile==None:
                            popNum = thrNumGPU.pop(0)
                            print(cmd + ' ' + str(popNum))
                            #processes[popNum] = Popen(cmd + ' ' + str(popNum), shell=True)
                            processes[popNum] = Popen(cmd, shell=True)
                        else:
                            tmpFolder=os.path.join(logFile.rsplit('/',1)[0], 'commandTmp')
                            if not os.path.exists(tmpFolder):
                                os.makedirs(tmpFolder)

                            commandFile=os.path.join(tmpFolder, randomStr + '.sh')
                            writeFile=open(commandFile, 'w')
                            writeFile.write('#!/bin/bash' + '\n\n')
                            writeFile.write('export TEMP=' + tempFile + '; \n\n\n')
                            #writeFile.write('export R_HOME=' + self.tools_RHOME + '; \n\n\n')
                            writeFile.close()

                            cmdNew=cmd.replace('\t','\\t').replace('\n','\\n')
                            writeFile=open(commandFile, 'a')
                            writeFile.write(cmdNew + '\n') 
                            writeFile.write('\n\necho -e ' + repr("\nExecuted Command:") + ' >> ' + logFile + '\n') 
                            writeFile.write('echo ' + pipes.quote(cmdNew) + ' >> ' + logFile + '\n') 
                            writeFile.close()                            
                            #a=Popen('echo ' + repr(cmd) + ' >> ' + commandFile, shell=True)
                            #a.wait()
                            #writeFile=open(commandFile, 'a')
                            #writeFile.write('\n\necho -e ' + repr("\nExecuted Command: \n") + repr(cmd) + ' "\n" >> ' + logFile + '\n') 
                            #writeFile.close()

                            os.chmod(commandFile, 0o744)  
                            #if sys.version_info[0] == 2:
                                #os.chmod(commandFile, 0744)
                            #else:
                                #os.chmod(commandFile, 0o744)  
                            finalCMD1='script -a ' + logFile + ' -c '+ commandFile + '; '
                            finalCMD2='rm -rf ' + commandFile + '; echo -e "\n\n\n" >> ' + logFile + '; exit; '
                            finalCMD=finalCMD1 + finalCMD2
                            popNum = thrNumGPU.pop(0)
                            processes[popNum] = Popen(cmd + ' ' + str(popNum) + '; ', shell=True)
                            time.sleep(2)
            if waitProcess:
                for p in processes: 
                    try:
                        #p.wait(60*60*5)
                        p.communicate(60*60*15)
                    except:
                        pass
            return(processes)
        else:
            return(None)
    except IOError:
        print('multisubprocess IOError') 

# 2. Define paths_configs viriables

python_path = "python3"
dnascan_dir = '/workDir/Tools/DNAscan/scripts/'

# 3. Define options from command line

parser = argparse.ArgumentParser(prog='python analyse_list_of_samples.py ', usage='%(prog)s -format "string" -paired "string" -sample_list "string" -out_dir "string" -option_string "string"', description = '############Help Message############ \n\nThis is a script to run DNAscan on a list of samples. Each line of the list must contain the path to one sample. If samples are in paired reads in fastq format and you have two files per sample, these will have to be on the same line spaced bt a tab.\n\n E.g. sample.1.fq.gz  sample.2.fq.gz\n\nDNAscan uses the file paths_configs.py to locate the needed tools and files. Please make sure your paths_configs.py file is properly filled \n\nUsage example: \n\npython alalyse_list_of_files.py -option_string "-format fastq -mode intensive -reference hg19 -alignment -variantcalling -annotation" -out_dir /path/to/dir -sample_list list.txt -processN 2 -format bam\n\nPlease check the following list of required options\n\n################################################', formatter_class=RawTextHelpFormatter)

requiredNamed = parser.add_argument_group('required named arguments')

requiredNamed.add_argument( '-option_string' , required=True , action = "store" , dest = "option_string" , default = "" , help = 'string of option to pass to the main script. Do not include neither -out option nor -in option . E.g. "-format fastq -mode intensive -reference hg19 -alignment -variantcalling -annotation"' )

requiredNamed.add_argument( '-out_dir' , required=True , action = "store" , dest = "out_dir" , default = "" , help = 'working directory [string]' )

requiredNamed.add_argument( '-sample_list' , required=True , action = "store" , dest = "sample_list" , default = "" , help = 'file containing the list of samples to Analyse [string]' )

requiredNamed.add_argument( '-format' , required=True , action = "store" , dest = "format" , help = 'options are bam, sam, fastq, vcf [string]' )

requiredNamed.add_argument( '-paired' , required=True , action = "store" , dest = "paired" , default = "1" , help = 'options are 1 for paired end reads and 0 for single end reads [string]' )

requiredNamed.add_argument( '-processN' , required=True , action = "store" , dest = "processN" , default = "1" , help = 'how many process to use [int]' )

# 4. Parse options from command line

args = parser.parse_args()
print(args)

option_string = args.option_string

out_dir = args.out_dir

sample_list = args.sample_list

format = args.format

paired = args.paired

processN = args.processN

list_file = open( "%s" %(sample_list) , 'r' )

list_file_lines = list_file.readlines()



# 5. Run DNAscan for each line in the input sample list
cmdCreateTree = []
cmdRun = []
for sample in list_file_lines :
    
    # 5.1 Create create DNAscan input file option string per line in the input list
    
    if paired == "1" and format == "fastq" :
        
        input_file_string = "-in %s -in2 %s" %(sample.split('\t')[0] , sample.split('\t')[1].strip())
        sample_name = sample.split('\t')[0].split("/")[-1].split("_R1.f")[-2]
    else :
        
           input_file_string = "-in %s" %( sample.strip() ) 
           
           sample_name = sample.split('.')[-2].split("/")[-1] 
           
    # 5.2 Create working dir tree
    
    #os.system( "mkdir %s ; mkdir %s/%s" %( out_dir , out_dir , sample_name ) )
    cmdCreateTree.append("mkdir -p %s ; mkdir -p %s/%s" %( out_dir , out_dir , sample_name ))
    
    # 5.3 Run DNAscan for one sample
    
    #os.system( "%s %sDNAscan.py %s -sample_name %s %s -out %s/%s/ " %( python_path , dnascan_dir , option_string , sample_name , input_file_string , out_dir , sample_name) )
    cmdRun.append("%s %sDNAscan.py %s -sample_name %s %s -out %s/%s/ " %( python_path , dnascan_dir , option_string , sample_name , input_file_string , out_dir , sample_name))
    

        
multisubprocess(cmdCreateTree, 5, waitProcess=True, execute=True, logFile=None)
multisubprocess(cmdRun, int(processN), waitProcess=True, execute=True, logFile=None)
print("Done")
