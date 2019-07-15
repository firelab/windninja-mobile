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
    """Create a tarball of the windninja_server source."""
    logger.info(f"Creating tarball of windninja_server..")
    tar_files = ' '.join(['windninja_server', 'bin', 'setup.py'])
    run(f'rm -f {tarname}')
    run(f"tar -czvf {tarname} --exclude='*.tar.gz' --exclude='fabfile.py' {tar_files}")
    logger.info(f"Successfully created tarball")


def upload_and_unpack(connection, tarname):
    """Upload a tarball to a remote host.

    Args:
        connection (fabric.Connection): Fabric connection for the remote host
        tarname (str): Name of the tarball to upload
    """
    logger.info(f"Copying {tarname} to on {connection.host}")
    connection.put(tarname, '/tmp')
    connection.run(f'tar -C /tmp -xzvf /tmp/{tarname}', hide=True)
    logger.info(f"Successfully coped and exactracted windninja_server source.")


def deploy_data(connection, source, destination):
    """Deploys the 'data' folder to the remote host

    Assumes that the files have been uploaded and the root tarball was unpacked
    to `source`.

    Args:
        connection (fabric.Connection): Fabric connection for the remote host
        source (str): Path on the remote host where the root tarball was unpacked.
        destination (str): Where to copy the files to on the remote host
    """
    data_folder_name = "data"

    # Primary data store folders
    # If these folders already exist, nothing happens.
    for f in ["account", "feedback", "job", "queue", "notification"]:
        dst_folder = os.path.join(destination, data_folder_name, f)
        logger.info(f"creating datastore folder: {dst_folder}")
        connection.run(f'mkdir -p {dst_folder}')

    # dem folder and files
    # If this folder exists, it will be removed before the new folder is
    # copied over so DEM files can be updated.
    f = "dem"
    src_folder = os.path.join(source, "..", data_folder_name, f)
    dst_folder = os.path.join(destination, data_folder_name, f)

    connection.run(f'rm -rf {dst_folder}')
    logger.info(f"copying test job folder: {src_folder} to {dst_folder}")
    connection.run(f"cp -R {src_folder} {dst_folder}")

    # test data folders
    # These folders are for testing the server after deployment.
    for f in   ["23becdaadf7c4ec2993497261e63d813", "1a111111111111111111111111111111"]:
        src_folder = os.path.join(source, "..", data_folder_name, "job", f)
        dst_folder = os.path.join(destination, data_folder_name, "job", f)
        run(f'rm -rf {dst_folder}')
        logger.info(f"copying test job folder: {src_folder} to {dst_folder}")
        connection.run(f"cp -R {src_folder} {dst_folder}")

    # TODO (lmalott): Figure out if it is really necessary to add executable
    # permissions to these directories.
    root_data_folder = os.path.join(destination, 'data')
    connection.sudo(f'chmod 777 -R {root_data_folder}')


def deploy_config(connection, source, destination):
    src_file = os.path.join(source, "windninjaserver.config.yaml")
    dst_folder = os.path.join(destination, "app")

    logger.info("creating application folder: {}".format(dst_folder))
    connection.run(f'mkdir -p {dst_folder}')

    logger.info(f"copying config file: {src_file} to {dst_folder}")
    connection.run(f"cp -R {src_file} {dst_folder}")

    #job wrapper config
    src_file = os.path.join(source, "windninjawrapper", "windninjawrapper.config.yaml")
    dst_folder = os.path.join(dst_folder, "windninjawrapper")

    logger.info("creating job wrapper folder: {}".format(dst_folder))
    connection.run(f'mkdir -p {dst_folder}')

    logger.info(f"copying config file: {src_file} to {dst_folder}")
    connection.run(f"cp -R {src_file} {dst_folder}")


def deploy_app(connection, source, destination):
    connection.run(f'rm -rf {destination}/app')
    connection.run(f'mkdir -p {destination}/app')

    # copy main folders
    for filename in ["windninjaweb", "windninjaqueue", "windninjaconfig", "windninjawrapper"]:
        src_folder = os.path.join(source, filename)
        dst_folder = os.path.join(destination, "app", filename)
        logger.info(f"copying {filename} folder: {src_folder} to {dst_folder}")
        connection.run(f"cp -R {src_folder} {dst_folder}")

    # copy top level files
    for f in ["runqueue.py", "../setup.py"]:
        src_file = os.path.join(source, f)
        dst_folder = os.path.join(destination, "app")
        logger.info(f"copying {f} file: {src_file} to {dst_folder}")
        connection.run(f"cp -R {src_file} {dst_folder}")

    bin_source = os.path.join(source, "..", "bin")
    connection.sudo(f"cp -R {bin_source} {destination}")


def deploy_apache(connection, source):
    src_file = os.path.join(source, "windninjaweb", "apache", "WindNinjaApp.conf")
    dst_folder = "/etc/apache2/sites-available"

    logger.info(f"copying apache config file: {src_file} to {dst_folder}")
    connection.sudo(f"cp -R {src_file} {dst_folder}")


def deploy_supervisor(connection, source):
    src_file = os.path.join(source, "windninjaqueue", "supervisor", "WindNinjaApp.conf")
    dst_folder = "/etc/supervisor/conf.d"

    logger.info(f"copying supervisor config file: {src_file} to {dst_folder}")
    connection.sudo(f"cp -R {src_file} {dst_folder}")


def reload_services(connection):
    logger.info('Reloading apache and supervisor')
    connection.sudo('mkdir -p /var/log/WindNinjaServer')
    connection.sudo('a2ensite WindNinjaApp')
    connection.sudo('service apache2 reload')
    connection.sudo('supervisorctl reload /etc/supervisor/supervisord.conf')
    connection.sudo('supervisorctl status')


@click.command()
@click.argument("parts", type=click.Choice(["all", "app", "config", "data", "apache", "supervisor"]))
@click.option('-t', '--target', default=None)
@click.option('-d', '--destination', default='/tmp/srv')
@click.option('-h', '--host' )
@click_log.simple_verbosity_option()
def deploy(parts, target, destination, host):
    """Deploy windninja_server to a remote destination.

    Args:
        parts (str): What to deploy.
        target (str): What tarball to upload. If empty, a tarball will be created.

    """
    logger.info(f"{sys.version} {sys.executable}")
    config = Config(overrides={'connect_kwargs': {'key_filename': 'WindNinjaMobile.pem'}})
    connection = Connection(host, config=config)

    source = '/tmp/windninja_server'

    if target is None:
        tag = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        target = f'windninja_server_{tag}.tar.gz'
        pack(target)

    # prepare a tarball of the source code and copy it to the host
    logger.info(f"Deploying windninja server {host}")
    upload_and_unpack(connection, target)

    connection.sudo(f'chown -R ubuntu:ubuntu {destination}')

    try:
        if parts == "all":
            # deploy_data is excluded because uploading the DEM files can take 30 minutes
            deploy_app(connection, source, destination)
            deploy_config(connection, source, destination)
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

        reload_services(connection)
    finally:
        connection.sudo(f'chown -R root:root {destination}')

    logger.info("complete!")


if __name__=="__main__":
    deploy()
