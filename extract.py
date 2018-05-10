import os
import logging
import numpy as np
import sys
import gc
import string
import re
import csv

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(filename='extract.log', level=logging.DEBUG, format=LOG_FORMAT)

logging.info("Begin to extract logs==========")

root_path = sys.argv[1]
# root_path = "/Users/liyang/Downloads/Imp/extra_log"

# log_path = "/Users/liyang/Downloads/Imp/extra_log"


log_file_list = []
#定义解析类
class ExtractInfo:
    command_type = ''  #对照组c,实验组1:e1,实验组2:e2
    domain = ''  
    problem = '' 
    number_of_registered_states = ''
    total_time = ''
    dead_ends = ''
    u_recognized = ''
    solution_found = ''
    translator_facts = ''
    time_spent_on_hC_computations = ''
    summed_up_size_of_RN_components = ''
    
    def __init__(self, command_type,domain,problem,number_of_registered_states,total_time,dead_ends,u_recognized,solution_found,translator_facts,time_spent_on_hC_computations,summed_up_size_of_RN_components): 
        self.command_type = command_type
        self.domain = domain
        self.problem = problem
        self.number_of_registered_states = number_of_registered_states
        self.total_time = total_time
        self.dead_ends = dead_ends
        self.solution_found = solution_found
        self.u_recognized = u_recognized
        self.translator_facts = translator_facts
        self.time_spent_on_hC_computations = time_spent_on_hC_computations
        self.summed_up_size_of_RN_components = summed_up_size_of_RN_components
    def getRow(self):
        row = [self.command_type,self.domain,self.problem,self.number_of_registered_states,self.total_time,self.dead_ends,self.u_recognized,self.solution_found,self.translator_facts,self.time_spent_on_hC_computations,self.summed_up_size_of_RN_components]
        return row
    def getRowC(self):
        row_c =  [self.domain,self.problem,self.number_of_registered_states,self.total_time,self.dead_ends,self.solution_found,self.plan_cost]
        return row_c
    def getRowE(self):
        row_e = [self.domain,self.problem,self.number_of_registered_states,self.total_time,self.dead_ends,self.u_recognized,self.solution_found]
        return row_e
#判断命令类型是对照组还是实验组
#对照组 为 c
#实验组1 为 e1
#实验组2 为 e2
def checkCommandType(lines):
    logging.debug('checkCommandType begin')
    command_type = 'none'
    search_arguments_index = -1
    search_arguments_line_index = 0
    index = 0
    for line in range(0,len(lines)):
        try:
            #寻找search arguments
            if lines[index].index('INFO     search arguments')>-1:
                search_arguments_line_index = index
                break
        except:
            pass
        index = index+1
    #通过search_arguments判断  
    if search_arguments_line_index==0:
        return 'error'
    argments = eval(lines[search_arguments_line_index].replace("\n",'').split(":")[1])
    index_lazy_greedy = -1
    index_ucrn2_1 = -1
    index_uccp = -1
    for arg in argments:
        try:
            index_lazy_greedy = arg.index('lazy_greedy')
        except:
            pass
        try:
            index_ucrn2_1 = arg.index('ucrn2_1')
        except:
            pass
        try:
            index_uccp = arg.index('uccp')
        except:
            pass
       
        if index_lazy_greedy >-1:
            command_type = 'c'
        if index_uccp >-1:
            command_type = 'e1'
        if index_ucrn2_1 > -1:
            command_type = 'e2'
    logging.debug('checkCommandType finished ,command_type is %s'%command_type)
    return command_type

def getFileLines(log_file):
    try:
        with open(log_file, 'r') as f: 
            lines = f.readlines()
        f.close()
        try:
            #判断第一行
            if lines[0].index('INFO     Running translator.')>-1:
                pass 
        except:
            lines = lines[1:]
            
        return lines
    except Exception,err:
        logging.error("Error at readFile %s"%log_file)
        logging.error(err)
        print(err)
#判断solution结果
def checkSolutionFound(lines):
    logging.debug("checkSolutionFound %s"%log_file)
    solutioned = False
    try:
        last_second_line = lines[-2].replace("\n",'')
        if last_second_line == 'Solution found.':
            solutioned = True
        return solutioned
    except Exception,err:
        logging.error("Error at checkSolutionFound %s"%log_file)
        logging.error(err)
        print(err)

def extract_old(lines,command_type):
    try:
        result_dic = {}
        indexs = range(-27,0)
        for index in indexs:
            result = lines[index].replace("\n",'').split(":")
            
            if len(result)>1:
                result_dic[result[0]]=result[1]
            else:
                result_dic[result[0]]=result[0]
        dead_ends =  result_dic['Dead ends'].replace("state(s).","")
        
        number_of_registered_states = -1
        try:
            number_of_registered_states = result_dic['Number of registered states']
        except:
            pass
        
        total_time = result_dic['Total time'].replace("s",'')
        solution_found = 1 
        
        domain = eval(lines[1].split(":")[1])[1].split("/")[-2]
        problem = eval(lines[1].split(":")[1])[1].split("/")[-1].replace(".pddl","")
        log_file.replace('.log','').split("@")[1]
        u_recognized = ''
        extract_info = ExtractInfo(command_type,domain,problem,number_of_registered_states,total_time,dead_ends,u_recognized,solution_found,translator_facts,time_spent_on_hC_computations,summed_up_size_of_RN_components) 
        logging.debug(extract_info.domain)
        row = []
        if command_type=='c':
            row = extract_info.getRowC()
        else:
            row = extract_info.getRowE()
        return row
    except Exception,err:
        logging.error("Error at extract %s"%log_file)
        logging.error(err)
        print(err)
def extract(lines,command_type):
#     lines = open('/Users/liyang/Downloads/Imp/fd09/52/log_nr/pegsol-sat11-strips-nr-p07.log','r').readlines()
    re_INFO_translator_input = 'INFO     translator input'
    re_Registered = 'Registered:'
    re_Total_time = 'Total time:'
    re_Dead_ends = 'Dead ends:'
    re_u_recognized_dead_ends = 'u-recognized dead ends:'
    re_Solution_found = 'Solution found.'
    re_unSolutioned = 'Search stopped without finding a solution.'
    re_Translator_facts = 'Translator facts:'
    re_Time_spent_on_hC_computations = 'Time spent on hC computations:'
    re_Summed_up_size_of_RN_components = 'Summed up size of RN components:'
    re_INFO_search_arguments = 'INFO     search arguments:'
        
    domain = ''  
    problem = '' 
    number_of_registered_states = '-1'
    total_time = '-1'
    dead_ends = '-1'
    u_recognized = '-1'
    solution_found = '-1'
    translator_facts = '-1'
    time_spent_on_hC_computations = '-1'
    summed_up_size_of_RN_components = '-1'
    for line in lines:
        line = line.replace('\n','')
        if re.match(re_INFO_translator_input, line):
            domain = eval(line.split(":")[1])[1].split("/")[-2]
            problem = eval(line.split(":")[1])[1].split("/")[-1].replace(".pddl","")
        if re.match(re_Registered,line):
            number_of_registered_states = int(line[re.match(re_Registered,line).span()[1]:].replace(' state(s).','').strip())
        if re.match(re_Total_time,line):
            total_time = float(line[re.match(re_Total_time,line).span()[1]:].replace('s','').strip())
        if re.match(re_Dead_ends,line):
            dead_ends = int(line[re.match(re_Dead_ends,line).span()[1]:].replace(' state(s).','').strip())
        if re.match(re_u_recognized_dead_ends,line):
            u_recognized = int(line[re.match(re_u_recognized_dead_ends,line).span()[1]:].replace(' state(s).','').strip())
        if re.match(re_Solution_found,line):
            solution_found = 1
        if re.match(re_Translator_facts,line):
            translator_facts = int(line[re.match(re_Translator_facts,line).span()[1]:].strip())
        if re.match(re_Time_spent_on_hC_computations,line):
            time_spent_on_hC_computations = float(line[re.match(re_Time_spent_on_hC_computations,line).span()[1]:].replace('s','').strip())
        if re.match(re_Summed_up_size_of_RN_components,line):
            summed_up_size_of_RN_components = int(line[re.match(re_Summed_up_size_of_RN_components,line).span()[1]:].split('(')[0].strip())
        if re.match(re_unSolutioned,line):
            solution_found = 0
    data = [command_type,domain,problem,number_of_registered_states,total_time,dead_ends,u_recognized,solution_found,translator_facts,time_spent_on_hC_computations,summed_up_size_of_RN_components]
    print(data)
    return data

def checkUnSolutioned(lines):
    un_solutioned_str = 'Search stopped without finding a solution.'
    find = False
    for line in lines:
        line = line.replace('\n','')
        if re.match(un_solutioned_str, line):
            find =  True
            break
    return find
        
        
    
def unsolutioned(lines):
    domain = eval(lines[1].split(":")[1])[1].split("/")[-2]
    problem = eval(lines[1].split(":")[1])[1].split("/")[-1].replace(".pddl","")
    solution_found = -1
    extract_info = ExtractInfo(domain,problem,'','','',solution_found,'','')                 
    logging.debug(extract_info.domain)
    if command_type=='c':
        row = extract_info.getRowC()
    else:
        row = extract_info.getRowE()
    return row
def extract_log(log_path):
    lines = getFileLines(log_path)
    #获取类别
    command_type = checkCommandType(lines)
    fd_info = []
    #获取SolutionFound 
    solutioned = checkSolutionFound(lines)
    unsolutioned = checkUnSolutioned(lines)
    print(solutioned,unsolutioned)
    if solutioned:
        logging.debug("%s : Solution found "%log_file)
        print("%s : Solution found "%log_file)
        extract_row = extract(lines,command_type) #solutioned
    elif unsolutioned:
        logging.debug("%s : dnot found"%log_file)
        print("%s : dnot found"%log_file)
        extract_row = extract(lines,command_type) #unsolutioned(lines)    
    else:
        logging.debug("%s : overtime"%log_file)
        print("%s : overtime"%log_file)
        extract_row = extract(lines,command_type) #overtime(lines)
    del lines
    gc.collect()
    return extract_row
logging.info("Begin to extract logs==========")
#定义输出文件名
filename = "extract_extra.csv" 
#定义输出数组
f = open(filename, 'w')
writer = csv.writer(f)
extract_data = []

folders = ['52','53','54','55','56']
log_folders = ['log_cp','log_nr','log_hff']
log_file_list = []
for folder in folders:
    for log_folder in log_folders:
        log_path = os.path.join(os.path.join(root_path,folder),log_folder)
        if os.path.exists(log_path):
            log_file_dir = os.path.join(os.path.join(root_path,folder),log_folder)
            log_file_list = os.listdir(log_file_dir)
            for log_file in log_file_list:
              
                log_file_full_path = os.path.join(log_file_dir,log_file)
                print(log_file_full_path)
                _data = extract_log(log_file_full_path)
                print(_data)
                if _data:
                    writer.writerow(_data)
        else:
            pass
f.close()
       
logging.debug("Export to csv %s"%filename)

print('End')
logging.info("End=========")





