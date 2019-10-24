# http://docs.openstack.org/developer/python-novaclient/ref/v2/servers.html
import time, os, sys
import inspect
from os import environ as env
import subprocess
from celery import Celery

from novaclient import client
import keystoneclient.v3.client as ksclient
from keystoneauth1 import loading
from keystoneauth1 import session

BROKER_URL = "pyamqp://tweets:tweets@192.168.1.26/tweets"

def createWorkerVM( workerName ):
    print( "Creating VM: " + workerName )

    flavor = 'ssc.small'
    #private_net = '41e5c095-1e70-4279-9c30-d1d23fa8c926'
    private_net = 'SNIC 2019/10-13 Internal IPv4 Network'
    floating_ip_pool_name = 'Public External IPv4 network'
    floating_ip = '130.238.28.174'
    image_name = 'Ubuntu 18.04 LTS (Bionic Beaver) - latest'
    key_pair = 'GNentid_Lab1'

    loader = loading.get_plugin_loader('password')

    auth = loader.load_from_options(auth_url=env['OS_AUTH_URL'],
                                    username=env['OS_USERNAME'],
                                    password=env['OS_PASSWORD'],
                                    project_name=env['OS_PROJECT_NAME'],
                                    project_domain_name=env['OS_USER_DOMAIN_NAME'],
                                    project_id=env['OS_PROJECT_ID'],
                                    user_domain_name=env['OS_USER_DOMAIN_NAME'])

    sess = session.Session(auth=auth)
    nova = client.Client('2.1', session=sess)
    print( "User authorization completed." )

    image = nova.glance.find_image(image_name)
    #image = nova.images.find(name=image_name)

    flavor = nova.flavors.find(name=flavor)

    if private_net != None:
        net = nova.neutron.find_network(private_net)
        #net = nova.networks.find(id=private_net)
        nics = [{'net-id': net.id}]
    else:
        sys.exit("private-net not defined.")

    #print("Path at terminal when executing this file")
    print( os.getcwd() + "\n" )
    cfg_file_path =  os.getcwd()+'/cloud-cfg.txt'
    if os.path.isfile(cfg_file_path):
        userdata = open(cfg_file_path)
    else:
        sys.exit("cloud-cfg.txt is not in current working directory")

    secgroups = ['default', 'GNentid_SecurityGroupL1']

    print( "Creating instance ... " )
    instance = nova.servers.create(name=workerName, image=image, flavor=flavor, userdata=userdata, nics=nics, security_groups=secgroups, key_name=key_pair)
    #instance = nova.servers.create(name="GNentid_Python_vm1", image=image, flavor=flavor, nics=nics, security_groups=secgroups, key_name=key_pair)
    inst_status = instance.status
    print( "waiting for 10 seconds.. " )
    time.sleep(10)

    while inst_status == 'BUILD':
        print( "Instance: "+instance.name+" is in "+inst_status+" state, sleeping for 5 seconds more..." )
        time.sleep(5)
        instance = nova.servers.get(instance.id)
        inst_status = instance.status

    #floating_ip = nova.floating_ips.create(floating_ip_pool_name)
    #print( "Assigning floating ip " + floating_ip )
    #instance.add_floating_ip(floating_ip)

    print( "Instance: "+ instance.name +" is in " + inst_status + " state" )
    return( True )


def removeVM( workerName ):
    print( "Removing VM: " + workerName )

    loader = loading.get_plugin_loader('password')

    auth = loader.load_from_options(auth_url=env['OS_AUTH_URL'],
                                    username=env['OS_USERNAME'],
                                    password=env['OS_PASSWORD'],
                                    project_name=env['OS_PROJECT_NAME'],
                                    project_domain_name=env['OS_USER_DOMAIN_NAME'],
                                    project_id=env['OS_PROJECT_ID'],
                                    user_domain_name=env['OS_USER_DOMAIN_NAME'])

    sess = session.Session(auth=auth)
    nova = client.Client('2.1', session=sess)
    print( "User authorization completed." )
    
    # Remove the instance.
    servers = nova.servers.list(search_opts={'name': workerName})
    for instance in servers:

        inst_status = instance.status
        print( "Instance: "+ instance.name +" is in " + inst_status + " state" )
        instance.delete()

        while inst_status == 'ACTIVE':
            print( "Instance: "+instance.name+" is in "+inst_status+" state, sleeping for 5 seconds more..." )
            time.sleep(5)
            instance = nova.servers.get(instance.id)
            inst_status = instance.status

        break

    # Try to find it.
    servers = nova.servers.list(search_opts={'name': workerName})
    for instance in servers:
        return( False )

    return( True )


def execCommand( cmd ):
    print( 'Executing: ' + cmd )

    resOutput = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)    
    lines = [x.decode('utf8').strip() for x in resOutput.stdout.readlines()]
    
    return( lines )


def drainWorker( workerName ):
    workerName = workerName.lower()
    print( "Draining " + workerName )

    resOutput = execCommand('sudo docker node update --availability drain ' + workerName )
    for line in resOutput:
        print( line )

        if "Error:" in line:
            return( False )

    return( True )


def removeSwarmWorker( workerName ):
    workerName = workerName.lower()
    print( "Removing from SWARM: " + workerName )

    resOutput = execCommand('sudo docker node rm --force ' + workerName )
    for line in resOutput:
        print( line )

        if "Error:" in line:
            return( False )

    return( True )


def removeWorkerVM( workerName ):

    # 1. Drain the worker
    if not drainWorker( workerName ):
        print( "drainWorker failed.")
        return( False )

    # 2. Remove it from swarm
    if not removeSwarmWorker( workerName ):
        print( "removeSwarmWorker failed.")
        return( False )

    # 3. Remove the VM
    if not removeVM( workerName ):
        print( "removeVM failed")
        return( False )

    return( True )


def monitorWorkers( manager ):
    print( "Monitorig: " + manager )

    app = Celery('tweetsApp',
             backend='rpc://',
             broker=manager)

    stats = app.control.inspect().ping()
    if not stats is None: 
        for worker in stats:
            print( worker + " - Online" )

    

#removeWorkerVM( "gnentid-python-vm1" )
#createWorkerVM( "gnentid-python-vm2" )
monitorWorkers( BROKER_URL )