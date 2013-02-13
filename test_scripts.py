import os
import subprocess

import private

test_module = 'ansible/hacking/test-module'

# ===============================================================
# Tear down server if it exists
# ===============================================================
command = ("{0} -m ./linode_create.py -a "
           "'name=\"{1}\" api_key=\"{2}\" state=\"absent\"'").format(
                   test_module, private.LABEL, private.API_KEY)

subprocess.call(command, shell=True)

# ===============================================================
# Create server
# ===============================================================
command = ("{0} -m ./linode_create.py"
           " -a 'name=\"{1}\" api_key=\"{2}\" plan=\"{3}\" datacenter=\"{4}\""
           " payment_term=\"{5}\" state=\"present\" disk_size=\"{6}\""
           " root_password=\"{7}\" distribution=\"{8}\" swap_size=256 wait=true'").format(
                test_module, private.LABEL, private.API_KEY, 
                private.PLAN, private.DATACENTER, private.PAYMENT_TERM, private.DISK_SIZE,
                private.ROOT_PASS, private.DISTRIBUTION) 

subprocess.call(command, shell=True)
