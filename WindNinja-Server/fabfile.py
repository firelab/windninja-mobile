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


def pack(tarname):
    logger.info(f"Creating tarball of windninja_server..")
    tar_files = ' '.join(['windninja_server', 'setup.py'])
    run(f'rm -f {tarname}')
    run(f"tar -czvf {tarname} --exclude='*.tar.gz' --exclude='fabfile.py' {tar_files}", hide=True)
    logger.info(f"Successfully created tarball")

def upload_and_unpack(connection, tarname):
    logger.info(f"Copying {tarname} to on {connection.host}")
    connection.put(tarname, '/tmp')
    connection.run(f'tar -C /tmp -xzvf /tmp/{tarname}', hide=True)
    logger.info(f"Successfully coped and exactracted windninja_server source.")

def deploy_data(connection, source, destination):
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
    src_folder = os.path.join(source, "..", data_folder_name, f)
    logger.info(f"copying test job folder: {src_folder} to {dst_folder}")
    connection.put(src_folder, remote=dst_folder)

    # test data folders
    for f in   ["23becdaadf7c4ec2993497261e63d813", "1a111111111111111111111111111111"]:
        dst_folder = os.path.join(destination, data_folder_name, "job", f)
        run(f'rm -rf {dst_folder}')
        src_folder = os.path.join(source, "..", data_folder_name, "job", f)
        logger.info("copying test job folder: {src_folder} to {dst_folder}")
        connection.run(f"cp -R {src_folder} {dst_folder}")


def deploy_config(connection, source, destination):

    dst_folder = os.path.join(destination, "App")
    logger.info("creating application folder: {}".format(dst_folder))
    connection.run(f'mkdir -p {dst_folder}')
    src_file = os.path.join(source, "windninjaserver.config.yaml")

    logger.info(f"copying config file: {src_file} to {dst_folder}")
    connection.run(f"cp -R {src_file} {dst_folder}")

    #job wrapper config
    dst_folder = os.path.join(dst_folder, "windninjawrapper")
    logger.info("creating job wrapper folder: {}".format(dst_folder))
    connection.run(f'mkdir -p {dst_folder}')

    src_file = os.path.join(source, "windninjawrapper", "windninjawrapper.config.yaml")

    logger.info(f"copying config file: {src_file} to {dst_folder}")
    connection.run(f"cp -R {src_file} {dst_folder}")


def deploy_app(connection, source, destination):

    ignore = shutil.ignore_patterns("__pycache__", "*.pyc", "*.conf", "*.config.yaml", "*.config.template.yaml")

    connection.run(f'rm -rf {destination}')
    connection.run(f'mkdir -p {destination}/App')

    # copy main folders
    for filename in ["windninjaweb", "windninjaqueue", "windninjaconfig", "windninjawrapper"]:
        dst_folder = os.path.join(destination, "App", filename)
        src_folder = os.path.join(source, filename)
        logger.info(f"copying {filename} folder: {src_folder} to {dst_folder}")
        connection.run(f"cp -R {src_folder} {dst_folder}")

    # copy top level files
    for f in ["runqueue.py"]:
        src_file = os.path.join(source, f)
        dst_folder = os.path.join(destination, "App")
        logger.info(f"copying {f} file: {src_file} to {dst_folder}")
        connection.run(f"cp -R {src_file} {dst_folder}")


def deploy_apache(connection, source):
    src_file = os.path.join(source, "windninjaweb", "apache", "WindNinjaApp.conf")
    dst_folder = "/etc/apache2/sites-available"
    logger.info(f"copying apache config file: {src_file} to {dst_folder}")
    connection.run(f"cp -R {src_file} {dst_folder}")


def deploy_supervisor(connection, source):
    src_file = os.path.join(source, "windninjaqueue", "supervisor", "WindNinjaApp.conf")
    dst_folder = "/etc/supervisor/conf.d"
    logger.info("copying supervisor config file: {src_file} to {dst_folder}")
    connection.run(f"cp -R {src_file} {dst_folder}")


@click.command()
@click.argument("parts", type=click.Choice(["all", "app", "config", "data", "apache", "supervisor"]))
@click.option('-d', '--destination', default='/tmp/srv')
@click.option('-h', '--host' )
@click_log.simple_verbosity_option()
def deploy(parts, destination, host):
    logger.info(f"{sys.version} {sys.executable}")
    config = Config(overrides={'connect_kwargs': {'key_filename': 'WindNinjaMobile.pem'}})
    connection = Connection(host, config=config)

    tag = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    tarname = f'windninja_server_{tag}.tar.gz'
    source = '/tmp/windninja_server'

    logger.info(f"deploying windninja server {host}")

    # prepare a tarball of the source code and copy it to the host
    pack(tarname)
    upload_and_unpack(connection, tarname)

    if parts == "all":
        deploy_app(connection, source, destination)
        deploy_config(connection, source, destination)
        deploy_data(connection, source, destination)
        deploy_apache(connection, source)
        deploy_supervisor(connection, source)
    elif parts == "app":
        deploy_app(connection, source, destination)
    elif parts == "config":
        deploy_config(connection, source, destination)
    elif parts == "data":
        deploy_data(connection, source, destination)
    elif parts == "apache":
        deploy_apache(connection, source)
    elif parts == "supervisor":
        deploy_supervisor(connection, source)

    logger.info("complete!")


if __name__=="__main__":
    deploy()
