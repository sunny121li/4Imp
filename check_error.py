import os
import logging
import string
import shutil

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(filename='checkErrorLog.log', level=logging.DEBUG, format=LOG_FORMAT)
def checkError(_file):
    t='Error:'
    result = False
    with open(_file, 'r') as f: 
        lines = f.readlines()
        f.close()
        for line in lines:
            result = string.find(line,t)!=-1
            if result:
                return result
                break
            else:
                pass
    return result
def checkExit(_file):
    t = ' exit status '
    result = False
    with open(_file, 'r') as f: 
        lines = f.readlines()
        f.close()
        for line in lines:
            result = string.find(line,t)!=-1
            if result:
                return result
                break
            else:
                pass
    return result

fo = open("error.sh", "w") 
foexit = open("error_exit.sh","w")
logging.info("Begin to extract logs==========")
# root_path = "/Users/liyang/Downloads/Imp/extra_log"
root_path = sys.argv[1]
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
#                 print(log_file)
                log_file_full_path = os.path.join(log_file_dir,log_file)
#                 print(checkError(log_file_full_path))
                if checkError(log_file_full_path):
                    origin = log_file_full_path
                    new_path = os.path.join(os.path.join(os.path.join(root_path,folder),'error'),log_file)
                    fo.write('mv '+origin+' '+new_path+'\n')  
                    print(origin)
                if checkExit(log_file_full_path):
                    origin = log_file_full_path
                    new_path = os.path.join(os.path.join(os.path.join(root_path,folder),'error_exit'),log_file)
                    foexit.write('mv '+origin+' '+new_path+'\n')  
                    print(origin)
                else:
                    pass
        else:
            pass
fo.close()  
foexit.close()
