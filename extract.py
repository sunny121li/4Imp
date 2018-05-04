import os
import logging
import numpy as np
import sys
import gc

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(filename='extract.log', level=logging.DEBUG, format=LOG_FORMAT)

logging.info("Begin to extract logs==========")

log_path = sys.argv[1]


#log_path = "/Users/liyang/Downloads/Imp/log"


log_file_list = []
class ExtractInfo:
    domain = ''
    problem = ''
    dead_ends = ''
    number_of_registered_states = ''
    total_time = ''
    solution_found = ''
    plan_cost = ''
    u_recognized = ''
    def __init__(self, domain,problem,dead_ends,number_of_registered_states,total_time,solution_found,plan_cost,u_recognized): 
        self.domain = domain
        self.problem = problem
        self.dead_ends = dead_ends
        self.number_of_registered_states = number_of_registered_states
        self.total_time = total_time
        self.solution_found = solution_found
        self.plan_cost = plan_cost
        self.u_recognized = u_recognized
    def getRowC(self):
        row_c =  [self.domain,self.problem,self.number_of_registered_states,self.total_time,self.dead_ends,self.solution_found,self.plan_cost]
        return row_c
    def getRowE(self):
        row_e = [self.domain,self.problem,self.number_of_registered_states,self.total_time,self.dead_ends,self.u_recognized,self.solution_found]
        return row_e

def checkCommandType(lines):
    logging.debug('checkCommandType begin')
    command_type = 'none'
    search_arguments_index = -1
    search_arguments_line_index = 0
    index = 0
    for line in range(0,len(lines)):
        try:
            if lines[index].index('INFO     search arguments')>-1:
                search_arguments_line_index = index
                break
        except:
            pass
        index = index+1
        
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

def getFileLines(log_path,log_file):
    try:
        with open(os.path.join(log_path,log_file), 'r') as f: 
            lines = f.readlines()
        f.close()
        try:
            if lines[0].index('INFO     Running translator.')>-1:
                pass 
        except:
            lines = lines[1:]
            
        return lines
    except Exception,err:
        f.close()
        logging.error("Error at readFile %s"%log_file)
        logging.error(err)
        print(err)

def checkSolutionFound(lines):
    logging.debug("checkSolutionFound %s"%log_file)
    solutioned = False
    try:
        last_second_line = lines[-2].replace("\n",'')
        if last_second_line == 'Solution found.':
            solutioned = True
        return solutioned
    except Exception,err:
        f.close()
        logging.error("Error at checkSolutionFound %s"%log_file)
        logging.error(err)
        print(err)

def extract(lines,command_type):
    try:
        result_dic = {}
        indexs = range(-15,0)
        for index in indexs:
            result = lines[index].replace("\n",'').replace('.','').split(":")
            if len(result)>1:
                result_dic[result[0]]=result[1]
            else:
                result_dic[result[0]]=result[0]
        dead_ends =  result_dic['Dead ends']
        number_of_registered_states = result_dic['Number of registered states']
        total_time = result_dic['Total time']
        solution_found = result_dic['Solution found']
        plan_cost = result_dic['Plan cost']
        domain = eval(lines[1].split(":")[1])[1].split("/")[-2]
        problem = eval(lines[1].split(":")[1])[1].split("/")[-1].replace(".pddl","")
        log_file.replace('.log','').split("@")[1]
        u_recognized = ''#result_dic['u_recognized']
        extract_info = ExtractInfo(domain,problem,dead_ends,number_of_registered_states,total_time,solution_found,plan_cost,u_recognized)                 
        logging.debug(extract_info.domain)
        row = []
        if command_type=='c':
            row = extract_info.getRowC()
        else:
            row = extract_info.getRowE()
        return row
    except Exception,err:
        f.close()
        logging.error("Error at extract %s"%log_file)
        logging.error(err)
        print(err)
def overtime(lines):
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

if os.path.exists(log_path):
    log_file_list = os.listdir(log_path)
else:
    logging.error("The log path %s is Non-existent"%log_path)

filename = "extract.csv" 
extract_data = []
for log_file in log_file_list:
    lines = getFileLines(log_path,log_file)
    command_type = checkCommandType(lines)
    fd_info = []
    solutioned = checkSolutionFound(lines)
    if solutioned:
        logging.debug("%s : Solution found "%log_file)
        print("%s : Solution found "%log_file)
        extract_row = extract(lines,command_type)
        extract_data.append(extract_row)
    else:
        logging.debug("%s : dnot found or overtime"%log_file)
        print("%s : dnot found or overtime"%log_file)
        extract_row = overtime(lines)
        extract_data.append(extract_row)
    del lines
    gc.collect()
logging.debug("Export to csv %s"%filename)
np.savetxt(filename, extract_data,fmt='%s', delimiter = ',')
logging.info("End=========")


