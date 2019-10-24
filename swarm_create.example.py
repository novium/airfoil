from os import environ as env
import os
import openstack

openstack = openstack.connect(auth_url=env['OS_AUTH_URL'],
                                username=env['OS_USERNAME'],
                                password=env['OS_PASSWORD'],
                                user_domain_name=env['OS_USER_DOMAIN_NAME'],
                                project_name=env['OS_PROJECT_NAME'],
                                project_domain_name=env['OS_USER_DOMAIN_NAME'],
                                project_id=env['OS_PROJECT_ID'])

access_token = "d23d1e2157079fc366f63c468651daf2a77b6f02"

swarm_manager = """
#cloud-config
users:
  - name: ubuntu
    sudo: ['ALL=(ALL) NOPASSWD:ALL']
    groups: sudo
    shell: /bin/bash
    ssh-authorized-keys:
        - ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEAgXQbUSsu6Ab/AWsHhBBNL3fkO9ZUWbquQqMjmrlFfhvrjle8IMdUYZsrpVTRnWOTnlqjLteQ9g6jIVwHq1Awx68Kyep4rJOM73owl0APrS6jMtd3uiB9eY7PL8YfxPZSmA/eF/dxAzWhY7T2pHDr1dRpzAn8+nlU52jTtsKfI7qeBlOinw5mhzxp7NaVw8RhNpfzykf3sdtPCchvK+YyDpTKpoKgGiFMv5cbfPL+KATmyE6Mhh7XtNZcbFZ5JZ9VQJavKFowrehVCp3ao8eiL/lXCAKyve1lb79n3iCLj3Cbarf6l0ddityPS7+oKS1qHpEMhb6LMVFTz2DcCaUcgQ==
apt_update: true
apt_upgrade: true
byobu_default: system 

chpasswd:
  list: |
    ubuntu:secretpassword

password: secretpassword
chpasswd: { expire: False }
ssh_pwauth: True

runcmd:
 - source /home/ubuntu/.bashrc
 - curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add 
 - add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
 - apt-get update
 - apt-get install -y docker-ce
 - docker login docker.pkg.github.com -u novium -p d23d1e2157079fc366f63c468651daf2a77b6f02
 - docker swarm join --token SWMTKN-1-2foghgc951krq15esascyzdjse1x7lkftx3qjsve3y2gamvzy8-5pc24whn79mvecjn40pjww64s 104.248.135.161:2377 
"""

swarm_worker = """
#cloud-config

apt_update: true
apt_upgrade: true
byobu_default: system 

runcmd:
 - source /home/ubuntu/.bashrc
 - curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add 
 - add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
 - apt-get update
 - apt-get install -y docker-ce
 - docker login docker.pkg.github.com -u novium -p d23d1e2157079fc366f63c468651daf2a77b6f02
"""

def create_server(type, config):
    if type == 'worker':
        image = openstack.compute.find_image('Ubuntu 18.04 LTS (Bionic Beaver) - latest')
        flavor = openstack.compute.find_flavor('ACCHT18.normal')
        net = openstack.network.find_network('SNIC 2019/10-32 Internal IPv4 Network')

        ip = openstack.network.find_available_ip()
        if ip == None:
            # This hopefully doesn't happen
            ip = openstack.network.create_ip()

        server = openstack.compute.create_server(name="deltafault-manager", image_id=image.id, key_name="deltafault",
                                        flavor_id=flavor.id, networks=[{'uuid': net.id}])
        server = openstack.compute.wait_for_server(server)

        openstack.compute.add_floating_ip_to_server(server, ip.floating_ip_address)
        
        return server

def destroy_server(server):
    openstack.compute.delete_server(server)

if __name__ == "__main__":
    server = create_server('worker', swarm_manager)
