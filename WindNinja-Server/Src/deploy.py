#!/usr/bin/python3
import argparse
import sys
import os
import shutil
import distutils

def _deployData(source_root, destination):
    
    data_foler_name = "Data"
    
    # primary data store folders
    for f in ["account", "feedback", "job", "queue", "notification"]:
        dst_folder = os.path.join(destination, data_foler_name, f)
        print("creating datastore folder: {}".format(dst_folder))
        os.makedirs(dst_folder, exist_ok=True)
    
    # dem folder and files
    f = "dem"
    dst_folder = os.path.join(destination, data_foler_name, f)
    try: shutil.rmtree(dst_folder) 
    except: pass
    src_folder = os.path.join(source_root, "..", data_foler_name, f)
    print("copying test job folder: {} to {}".format(src_folder, dst_folder))
    shutil.copytree(src_folder, dst_folder)
    
    # test data folders
    for f in   ["23becdaadf7c4ec2993497261e63d813", "1a111111111111111111111111111111"]:  
        dst_folder = os.path.join(destination, data_foler_name, "job", f)
        try: shutil.rmtree(dst_folder) 
        except: pass
        src_folder = os.path.join(source_root, "..", data_foler_name, "job", f)
        print("copying test job folder: {} to {}".format(src_folder, dst_folder))
        shutil.copytree(src_folder, dst_folder)
    
def _deployConfig(source_root, destination):

    dst_folder = os.path.join(destination, "App")
    print("creating application folder: {}".format(dst_folder))
    os.makedirs(dst_folder, exist_ok=True)
    src_file = os.path.join(source_root, "windninjaserver.config.yaml")
    print("copying config file: {} to {}".format(src_file, dst_folder))
    shutil.copy(src_file, dst_folder)
    
    #job wrapper config
    dst_folder = os.path.join(dst_folder, "windninjawrapper")
    print("creating job wrapper folder: {}".format(dst_folder))
    os.makedirs(dst_folder, exist_ok=True)
    src_file = os.path.join(source_root, "windninjawrapper", "windninjawrapper.config.yaml")
    print("copying config file: {} to {}".format(src_file, dst_folder))
    shutil.copy(src_file, dst_folder)
    
   
def _deployApp(source_root, destination):

    ignore = shutil.ignore_patterns("__pycache__", "*.pyc", "*.conf", "*.config.yaml", "*.config.template.yaml")

    #NOTE: destinations must not exist for shutil.copytree 
    # could use distutils.dir_utils.copytree() but that doesn't have ignore options
    # some SE threads have a modified version of shutil.copytree that does the combo
    
    # copy main folders
    for f in ["windninjaweb", "windninjaqueue", "windninjaconfig", "windninjawrapper"]:   
        dst_folder = os.path.join(destination, "App", f)
        try: shutil.rmtree(dst_folder) 
        except: pass
        src_folder = os.path.join(source_root, f)
        print("copying {} folder: {} to {}".format(f, src_folder, dst_folder))
        shutil.copytree(src_folder, dst_folder, ignore=ignore)

    # copy top level files
    for f in ["runqueue.py"]:
        src_file = os.path.join(source_root, f)
        dst_folder = os.path.join(destination, "App")
        print("copying {} file: {} to {}".format(f, src_file, dst_folder))
        shutil.copy(src_file, dst_folder)

def _deployApache(source_root):
    src_file = os.path.join(source_root, "windninjaweb", "apache", "WindNinjaApp.conf")
    dst_folder = "/etc/apache2/sites-available"
    print("copying apache config file: {} to {}".format(src_file, dst_folder))
    shutil.copy(src_file, dst_folder )

def _deploySupervisor(source_root):
    src_file = os.path.join(source_root, "windninjaqueue", "supervisor", "WindNinjaApp.conf")
    dst_folder = "/etc/supervisor/conf.d"
    print("copying supervisor config file: {} to {}".format(src_file, dst_folder))
    shutil.copy(src_file, dst_folder)
    
parser = argparse.ArgumentParser()
parser.add_argument("parts", choices=["all", "app", "config", "data", "apache", "supervisor"])
parser.add_argument("-d", "--destination", required=False)
parser.add_argument("-s", "--source_root", default=os.path.dirname(os.path.realpath(__file__)), required=False)

args = parser.parse_args()

print("{0} {1}".format(sys.version, sys.executable))
print("deploying windninja server '{1}'\nfrom {2}\nto {0}".format(args.destination, args.parts, args.source_root))

#build the destination root
os.makedirs(args.destination, exist_ok=True)

if args.parts == "all": 
    _deployApp(args.source_root, args.destination)
    _deployConfig(args.source_root, args.destination)
    _deployData(args.source_root, args.destination)
    _deployApache(args.source_root)
    _deploySupervisor(args.source_root)
elif args.parts == "app": 
    _deployApp(args.source_root, args.destination)
elif args.parts == "config": 
    _deployConfig(args.source_root, args.destination)
elif args.parts == "data": 
    _deployData(args.source_root, args.destination)
elif args.parts == "apache": 
    _deployApache(args.source_root)
elif args.parts == "supervisor": 
    _deploySupervisor(args.source_root)

print("complete!")