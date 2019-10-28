#!/usr/bin/env python3
"""workerMonitor.py"""

# http://docs.openstack.org/developer/python-novaclient/ref/v2/servers.html
import time, os, sys, signal, socket
import inspect
from os import environ as env
import subprocess
from celery import Celery
import json

from novaclient import client
import keystoneclient.v3.client as ksclient
from keystoneauth1 import loading
from keystoneauth1 import session

# Some operation constants.
BROKER_URL = "pyamqp://tweets:tweets@192.168.1.26/tweets"
WORKERS_UPPER_LIMIT = 0.5
WORKERS_LOWER_LIMIT = 0.1
WORKERS_MIN         = 1
WORKERS_STEP        = 2
WORKERS_PANIC_STEP  = 4
WORKERS_NAME        = socket.gethostname()
RELEASE_CALLS       = 5

# Workers info.
numWorkers   = 0
numTasks     = 0
releaseCalls = 0

def signal_handler(sig, frame):
    print( "\nShutting down..." )
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


def execCommand( cmd ):
    print( '\bExecuting: ' + cmd )

    resOutput = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)    
    lines = [x.decode('utf8').strip() for x in resOutput.stdout.readlines()]
    
    return( lines )


def getWorkerName( name ):
    rname = name.split('@', 1)

    if len(rname) > 1:
        return rname[1]
    else:
        return name 


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
            try:
                instance = nova.servers.get(instance.id)
                inst_status = instance.status
            except:
                break

        break

    # Try to find it.
    servers = nova.servers.list(search_opts={'name': workerName})
    for instance in servers:
        return( False )

    return( True )


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


def createWorkerCL( workerName ):
    print( "\tAdding worker: ", workerName )
    cmd = "celery -A ctweetsw worker -n celery@" + workerName + " --quiet &"
    os.system( cmd )

    time.sleep(1.5)


def removeWorkerCL( workerName ):
    print( "\tReleasing: ", workerName )
    cmd = "ps auxww | grep \"" + workerName + "\" | awk '{print $2}' | xargs kill -9 2> /dev/null"
    cmdRes = os.system( cmd )


def addMoreWorkers( allWorkers, panic ):
    print( "Adding more workes." )

    upperLimit = WORKERS_PANIC_STEP if panic else WORKERS_STEP
    for w in range(upperLimit):
        workerName = WORKERS_NAME + "-" + str(w +1 + len(allWorkers) )
        createWorkerCL( workerName )

    global releaseCalls
    releaseCalls = 0


def releaseWorkers( allWorkers, busyWorkers ):
    print( "Releasing workers." )    

    # Do not release every time. Wait a little. 
    global releaseCalls
    releaseCalls = releaseCalls +1
    if releaseCalls <= RELEASE_CALLS:
        print( "\tWaiting ", releaseCalls )
        return
    else:
        releaseCalls = 0

    for w in busyWorkers:
        print( "\tBusy: ", w )

    toRemove = []
    for w in allWorkers:
        if not w in busyWorkers:
            toRemove.append( w )

    toRemove.sort()
    while len( toRemove ) > WORKERS_MIN:
        worker = toRemove[ len(toRemove) -1 ]
        removeWorkerCL( worker )
        toRemove.remove( worker )


def monitorWorkers( manager ):
    print( "Monitorig: " + manager )

    app = Celery('tweetsApp',
             backend='rpc://',
             broker=manager)

    while True:
        numWorkers = 0
        numTasks   = 0
        utilization = 0
        busyWorkers = []
        allWorkers  = []
        inspect = app.control.inspect()

        workers = inspect.ping()
        if not workers is None: 
            numWorkers = len( workers )
            for worker in workers:
                allWorkers.append( getWorkerName(worker) )
                print( worker + " - Online" )

        # Count active tasks.
        allTasks = inspect.active()
        if not allTasks is None:
            for workerId in allTasks:
                
                workerTasks = allTasks[workerId]
                numTasks = numTasks + len( workerTasks )

                if len( workerTasks ) != 0:
                    busyWorkers.append( getWorkerName(workerId) )

        # Count queued tasks too.
        allTasks = inspect.reserved()
        if not allTasks is None:
            for workerId in allTasks:
                
                workerTasks = allTasks[workerId]
                numTasks = numTasks + len( workerTasks )

                # for task in workerTasks:
                #     print( type(task) )
                #     print( task['id'], task['name'] )

        if numWorkers != 0:
            utilization = numTasks / numWorkers
        panic = (utilization > 1)
        
        print( "Workers     :", numWorkers )
        print( "Tasks       :", numTasks )
        if panic:
            print( "Utilization : %3.1f %%  Panic!!! " % (utilization * 100.0) )
        else:
            print( "Utilization : %3.1f %%" % (utilization * 100.0) )

        if( utilization >= WORKERS_UPPER_LIMIT ):
            addMoreWorkers( allWorkers, panic )
        else:
            if( utilization <= WORKERS_LOWER_LIMIT and numWorkers > WORKERS_MIN ):
                releaseWorkers( allWorkers, busyWorkers )

        print( "===========================================" )
        time.sleep(5)



#removeWorkerVM( "gnentid-lab3-v2" )
#createWorkerVM( "gnentid-lab3-v2" )
monitorWorkers( BROKER_URL )
