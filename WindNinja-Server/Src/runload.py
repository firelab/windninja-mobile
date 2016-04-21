#!/usr/bin/python3
import argparse
import shutil
import os
import sys



def _deployData(jobs, source_root, destination):
    
    data_foler_name = "Data"
    
    # test data folders
    test_data_folder = "1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a"
    template_folder_name = "".rjust(32, "d")
    job_names = []
       
    for j in range(jobs):  
        job_name = template_folder_name[0:len(template_folder_name) - len(str(j))] + str(j)
        dst_folder = os.path.join(destination, data_foler_name, "job", job_name)
        try: shutil.rmtree(dst_folder) 
        except: pass
        src_folder = os.path.join(source_root, "..", data_foler_name, "job", test_data_folder)
        print("copying test job folder: {} to {}".format(src_folder, dst_folder))
        shutil.copytree(src_folder, dst_folder)
        job_names.append(job_name)

    return job_names        

def _deployQueue(jobs, destination):
    data_foler_name = "Data"
    queue_folder_name = "queue"
    queue_folder = os.path.join(destination, data_foler_name, queue_folder_name)
    
    for j in jobs:
        #TODO: use enqueue from queue module
        name = "{0}.{1}".format(j, "pending")
        file = os.path.join(queue_folder, name)
        print("queueing test job: {}".format(file))
        open(file, "x").close()
        

parser = argparse.ArgumentParser()
parser.add_argument("jobs", type=int)
parser.add_argument("-d", "--destination", required=False)
parser.add_argument("-s", "--source_root", default=os.path.dirname(os.path.realpath(__file__)), required=False)

args = parser.parse_args()

print("{0} {1}".format(sys.version, sys.executable))
print("running windninja server load test:\n'{0}'jobs\nto {1}\nfrom{2}".format(args.jobs, args.destination, args.source_root))

jobs = _deployData(args.jobs, args.source_root, args.destination)
_deployQueue(jobs, args.destination)
print("complete!")