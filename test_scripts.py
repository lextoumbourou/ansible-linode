import subprocess
import private

# Script shold look something like this
# ansible/hacking/test-module -m ./linode_create.py -a 'name="{{ HOSTNAME_TO_CREATE }}" api_key="{{ API_KEY }}" plan="{{ TEST_PLAN }}" datacenter="{{ TEST_DATACENTER }}" payment_term=1'

# Start off by creating the host, or modify it if it exists
command = ("ansible/hacking/test-module -m ./linode_create.py"
           "-a 'name=\"{0}\" api_key=\"{1}\" plan=\"{2}\" datacenter=\"{3}\""
           "payment_term=\"{4}\" state=\"present\"").format(
                private.LABEL, private.API_KEY, private.PLAN, 
                private.DATACENTER, private.PAYMENT_TERM)

subprocess.check_output(command, "Blah") 
