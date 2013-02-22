import os
import subprocess

import private

test_module = 'ansible/hacking/test-module'

# ===============================================================
# Tear down server if it exists
# ===============================================================
command = ("{0} -m ./library/linode_manager -a "
           "'name=\"{1}\" api_key=\"{2}\" state=\"absent\"'").format(
               test_module, private.LABEL, private.API_KEY)

subprocess.call(command, shell=True)

# ===============================================================
# Create server
# ===============================================================
command = ("{0} -m ./library/linode_manager"
           " -a 'name=\"{1}\" api_key=\"{2}\" plan=\"{3}\" datacenter=\"{4}\""
           " payment_term=\"{5}\" state=\"present\" root_disk_size=\"{6}\""
           " root_password=\"{7}\" distribution=\"{8}\" swap_disk_size=256 wait=true'").format(
                test_module, private.LABEL, private.API_KEY, 
                private.PLAN, private.DATACENTER, private.PAYMENT_TERM, private.DISK_SIZE,
                private.ROOT_PASS, private.DISTRIBUTION) 

subprocess.call(command, shell=True)

# ===============================================================
# Ensure that create server isn't run when Linode exists
# ===============================================================
command = ("{0} -m ./library/linode_manager"
           " -a 'name=\"{1}\" api_key=\"{2}\" plan=\"{3}\" datacenter=\"{4}\""
           " payment_term=\"{5}\" state=\"present\" root_disk_size=\"{6}\""
           " root_password=\"{7}\" distribution=\"{8}\" swap_disk_size=256 wait=true'").format(
                test_module, private.LABEL, private.API_KEY, 
                private.PLAN, private.DATACENTER, private.PAYMENT_TERM, private.DISK_SIZE,
                private.ROOT_PASS, private.DISTRIBUTION) 

subprocess.call(command, shell=True)

# ===============================================================
# Test reboot module call
# ===============================================================
command = ("{0} -m ./library/linode_manager"
           " -a 'name=\"{1}\" api_key=\"{2}\" state=\"rebooted\"'").format(
                   test_module, private.LABEL, private.API_KEY)

subprocess.call(command, shell=True)

# ===============================================================
# Test reboot module call with a wait
# ===============================================================
command = ("{0} -m ./library/linode_manager"
           " -a 'name=\"{1}\" api_key=\"{2}\" state=\"rebooted\" wait=\"yes\"'").format(
                   test_module, private.LABEL, private.API_KEY)

subprocess.call(command, shell=True)

# ===============================================================
# Test shutdown procedure
# ===============================================================
command = ("{0} -m ./library/linode_manager"
           " -a 'name=\"{1}\" api_key=\"{2}\" state=\"shutdown\" wait=\"yes\"'").format(
                   test_module, private.LABEL, private.API_KEY)

subprocess.call(command, shell=True)

# ===============================================================
# Test boot procedure
# ===============================================================
command4 = ("{0} -m ./library/linode_manager"
           " -a 'name=\"{1}\" api_key=\"{2}\" state=\"booted\" wait=\"yes\"'").format(
                   test_module, private.LABEL, private.API_KEY)

subprocess.call(command, shell=True)

# ===============================================================
# Tear down server
# ===============================================================
command = ("{0} -m ./library/linode_manager -a "
           "'name=\"{1}\" api_key=\"{2}\" state=\"absent\"'").format(
                   test_module, private.LABEL, private.API_KEY)

#subprocess.call(command, shell=True)

# ===============================================================
# Try to tear down server again. Ensure that changed=false
# ===============================================================
command = ("{0} -m ./library/linode_manager -a "
           "'name=\"{1}\" api_key=\"{2}\" state=\"absent\"'").format(
                   test_module, private.LABEL, private.API_KEY)

#subprocess.call(command, shell=True)
