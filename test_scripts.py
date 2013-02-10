import os
import subprocess

import private

current_dir = '.'

# Start off by creating the host, or modify it if it exists
command = ("{0}/ansible/hacking/test-module -m {1}/linode_create.py"
           " -a 'name=\"{2}\" api_key=\"{3}\" plan=\"{4}\" datacenter=\"{5}\""
           " payment_term=\"{6}\" state=\"present\" disk_size=\"{7}\""
           " root_password=\"{8}\" distribution=\"{9}\" swap_size=256 wait=true'").format(
                current_dir, current_dir, private.LABEL, private.API_KEY, 
                private.PLAN, private.DATACENTER, private.PAYMENT_TERM, private.DISK_SIZE,
                private.ROOT_PASS, private.DISTRIBUTION) 

subprocess.call(command, shell=True)
