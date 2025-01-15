#!/bin/bash

echo "startup dCloud script launched at: " > /home/cisco/deploy.log

date >> /home/cisco/deploy.log
whoami >> /home/cisco/deploy.log

ansible-playbook -e "ansible_user=cisco ansible_ssh_pass=cisco123 ansible_sudo_pass=cisco123" \
  /home/cisco/SRv6_dCloud_Lab/ansible/dcloud_startup_playbook.yml -v >> /home/cisco/deploy.log
