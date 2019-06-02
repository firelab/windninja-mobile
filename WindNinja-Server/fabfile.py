import sys
import os
import logging
import shutil
import distutils
from datetime import datetime

import click
import click_log
from fabric import Connection, Config
from invoke import run

logger = logging.getLogger(__name__)
click_log.basic_config(logger)


TAR_NAME = 'windninja.tar.gz'



def pack():
    tar_files = ' '.join(['windninja_server', 'setup.py'])
    run(f'rm -f {TAR_NAME}')
    run(f"tar -czvf {TAR_NAME} --exclude='*.tar.gz' --exclude='fabfile.py' {tar_files}")

def upload_and_unpack(connection):
    connection.put(TAR_NAME, '/tmp')
    connection.run(f'tar -C /tmp -xzvf /tmp/{TAR_NAME}')

def deploy_data(connection, source_root, destination):
    data_folder_name = "Data"

    # primary data store folders
    for f in ["account", "feedback", "job", "queue", "notification"]:
        dst_folder = os.path.join(destination, data_folder_name, f)
        logger.info(f"creating datastore folder: {dst_folder}")
        connection.run(f'mkdir -p {dst_folder}')

    # dem folder and files
    f = "dem"
    dst_folder = os.path.join(destination, data_folder_name, f)

    connection.run(f'rm -rf {dst_folder}')
    src_folder = os.path.join(source_root, "..", data_folder_name, f)
    logger.info(f"copying test job folder: {src_folder} to {dst_folder}")
    connection.put(src_folder, remote=dst_folder)

    # test data folders
    for f in   ["23becdaadf7c4ec2993497261e63d813", "1a111111111111111111111111111111"]:
        dst_folder = os.path.join(destination, data_folder_name, "job", f)
        try: shutil.rmtree(dst_folder)
        except: pass
        src_folder = os.path.join(source_root, "..", data_folder_name, "job", f)
        logger.info("copying test job folder: {src_folder} to {dst_folder}")
        shutil.copytree(src_folder, dst_folder)


def deploy_config(connection, source_root, destination):

    dst_folder = os.path.join(destination, "App")
    logger.info("creating application folder: {}".format(dst_folder))
    os.makedirs(dst_folder, exist_ok=True)
    src_file = os.path.join(source_root, "windninjaserver.config.yaml")
    logger.info("copying config file: {} to {}".format(src_file, dst_folder))
    shutil.copy(src_file, dst_folder)

    #job wrapper config
    dst_folder = os.path.join(dst_folder, "windninjawrapper")
    logger.info("creating job wrapper folder: {}".format(dst_folder))
    os.makedirs(dst_folder, exist_ok=True)
    src_file = os.path.join(source_root, "windninjawrapper", "windninjawrapper.config.yaml")
    logger.info("copying config file: {} to {}".format(src_file, dst_folder))
    shutil.copy(src_file, dst_folder)


def deploy_app(connection, source_root, destination):

    ignore = shutil.ignore_patterns("__pycache__", "*.pyc", "*.conf", "*.config.yaml", "*.config.template.yaml")

    #NOTE: destinations must not exist for shutil.copytree
    # could use distutils.dir_utils.copytree() but that doesn't have ignore options
    # some SE threads have a modified version of shutil.copytree that does the combo
    connection.run(f'rm -rf {destination}')

    # copy main folders
    # TODO (lmalott): these need to be updated to reference the remote paths
    for filename in ["windninjaweb", "windninjaqueue", "windninjaconfig", "windninjawrapper"]:
        dst_folder = os.path.join(destination, "App", filename)
        src_folder = os.path.join(source_root, filename)
        logger.info(f"copying {filename} folder: {src_folder} to {dst_folder}")
        connection.put(src_folder, remote=dst_folder)

    # copy top level files
    for f in ["runqueue.py"]:
        src_file = os.path.join(source_root, f)
        dst_folder = os.path.join(destination, "App")
        logger.info("copying {} file: {} to {}".format(f, src_file, dst_folder))
        shutil.copy(src_file, dst_folder)


def deploy_apache(connection, source_root):
    src_file = os.path.join(source_root, "windninjaweb", "apache", "WindNinjaApp.conf")
    dst_folder = "/etc/apache2/sites-available"
    logger.info(f"copying apache config file: {src_file} to {dst_folder}")
    shutil.copy(src_file, dst_folder)


def deploy_supervisor(connection, source_root):
    src_file = os.path.join(source_root, "windninjaqueue", "supervisor", "WindNinjaApp.conf")
    dst_folder = "/etc/supervisor/conf.d"
    logger.info("copying supervisor config file: {} to {}".format(src_file, dst_folder))
    shutil.copy(src_file, dst_folder)


@click.command()
@click.argument("parts", type=click.Choice(["all", "app", "config", "data", "apache", "supervisor"]))
@click.option('-d', '--destination', default='/tmp')
@click.option('-s', '--source', default=os.path.dirname(os.path.realpath(__file__)))
@click.option('-h', '--host' )
def deploy(parts, destination, source, host):
    logger.info(f"{sys.version} {sys.executable}")
    logger.info("deploying windninja server '{1}'\nfrom {2}\nto {0}".format(destination, parts, source))

    config = Config(overrides={'connect_kwargs': {'key_filename': 'WindNinjaMobile.pem'}})
    connection = Connection('ubuntu@ec2-52-61-205-101.us-gov-west-1.compute.amazonaws.com', config=config)

    tag = datetime.now().strftime('%y.%m.%d_%H.%M.%S')
    destination = os.path.join(destination, tag)

    # prepare a tarball of the source code and copy it to the host
    pack()
    upload_and_unpack(connection)

    if parts == "all":
        deploy_app(connection, source_root, destination)
        deploy_config(connection, source_root, destination)
        deploy_data(connection, source_root, destination)
        deploy_apache(connection, source_root)
        deploy_supervisor(connection, source_root)
    elif parts == "app":
        deploy_app(connection, source, destination)
    elif parts == "config":
        deploy_config(connection, source_root, destination)
    elif parts == "data":
        deploy_data(connection, source_root, destination)
    elif parts == "apache":
        deploy_apache(connection, source_root)
    elif parts == "supervisor":
        deploy_supervisor(connection, source_root)

    logger.info("complete!")


if __name__=="__main__":
    deploy()
