#!/usr/bin/python
DESCRIPTION = """
---
module: linode_manager
short_description: create and manage a Linode instance, return a LinodeID
description:
    - Creates Linodes instance and optionally waits for it to be 'booted'. 
    - Additional, the Linode instance can be shutdown, booted, restarted and destroyed.
    - Currently limited to one root disk created from a distribution and one swap disk
author_name: Lex Toumbourou
requirements: ["python-linode"] # Python API bindings for Linode
examples:
  - code: 'local_action: linode_manager api_key=1234 name=server_name 
           plan="Linode 512" datacenter=Tokyo payment_term=1 kernel=3.7.5-linode48 state=present
           root_disk_size=24320 swap_disk_size=256 root_password=hunter2 wait=true'
    description: "Creates a Linode if it doesn't exist"
options:
  api_key:
    description:
      - API key use to manage your Linodes
    required: true
    default: null
  name:
    description:
      - Name/label/hostname of the Linode instance
    required: true
    default: null
    aliases: 
    ['label', 'hostname']
  state:
    choices: [ present, absent, rebooted, shutdown, booted ] 
    description:
      - Present will create the Linode if it doesn't exist,
        absent will destroy it (be careful!),
        shutdown, booted and rebooted will perform the action the name implies,
        all except rebooted are idempotent actions
    required: true
    default: null
  datacenter:
    description:
       - String or datacenter id representing the Linode datacenters the server will reside
         Examples: http://www.linode.com/api/utility/avail.datacenters
         Only required if state is present
    required: false
    default: null
  plan:
    description:
      - String or plan id representing the Linode plan the server will use 
        Examples: http://www.linode.com/api/utility/avail.linodeplans
        Only required if state is present
    required: false
    default: null
  payment_term:
    choices: [ 1, 12, 24 ]
    description:
      - Length of time in months that you will prepay for the server
        Only required if the state is present
    required: false
    default: null
  distribution:
    description:
      - String or distribution id representing the OS on your server
        Examples: http://www.linode.com/api/utility/avail.distributions
        Only required if the state is present
    required: false
    default: null
  kernel:
    description:
       - String or kernel id representing the kernel for the configuration profile
         Examples: http://www.linode.com/api/utility/avail.kernels
         Only required if the state is present
    required: false
    default: null
  root_password:
    description:
      - String representing the root password for the Linode
        Note that if the Linode exists, the root password will *not* be changed
    required: false
    default: null
  root_disk_size:
    description:
      - Size of root disk in MB
        Only required if the state is present
    required: false
    default: null
  swap_disk_size:
    description:
      - Size of swap disk in MB
        Only required if the state is present
    required: false
    default: null
  root_ssh_key:
    description:
      - Optionally include an ssh key for root 
    required: false
    default: null
  display_group:
    description:
      - Optionally specify which display group to place the Linode in
    required: false
    default: null
  wait:
    description:
      - wait for Linode instance to be in state 'booted' before returning
    required: false
    default: false
  timeout:
    description:
      - optionally specify a timeout period in seconds to wait
    required: false
    default: 120
"""
  
import sys
import warnings

# I have to catch the warning here because the Linode API module has a Runtime Warning,
# this will need to be fixed before I'd recommend using this module since root passwords are sent
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    try:
        from linode import api
    except ImportError:
        print "failed=True msg='python-linode required for this module'"
        sys.exit(1)


def get_host_id(label, lin):
    """
    Return LINODEID if specified host is already created

    args:
        label - string - hostname
        lin - linode.api.Api object - connected Api class

    returns:
        bool
    """
    # See if the hostname is already in the domain list, if not, we'll create it 
    for host in lin.linode_list():
        if host['LABEL'] == label:
            return host['LINODEID']

    return None


def get_plan_id(plan, lin):
    """
    Return plan id if available

    args:
        plan - string or int - name or id of plan
        lin - linode.api.Api object - connected Api class

    returns:
        int or None
    """
    # If it's a number, we'll ensure it's an int
    try:
        plan = int(plan)
    except ValueError:
        pass

    for p in lin.avail_linodeplans():
        if p['PLANID'] == plan or p['LABEL'] == plan:
            return p['PLANID']

    return None


def get_datacenter_id(datacenter, lin):
    """
    Return datacenter id if valid

    args:
        datacenter - string or int - name of datacenter or id
        lin - linode.api.Api object - connected Api class
    
    returns:
        int or None
    """
    # if it's a number, we'll ensure it's an int
    if datacenter.isdigit():
        datacenter = int(datacenter)

    for dc in lin.avail_datacenters():
        if type(datacenter) is int:
            if dc['DATACENTERID'] == datacenter:
                return dc['DATACENTERID']
        # If it's not an int, I'll search the datacenter string for the 
        # specified datacenter, allowing for 'Tokyo' to match 'Tokyo, JP' etc
        # I don't want to do string search everytime if the user gives an int
        else:
            if datacenter in dc['LOCATION']:
                return dc['DATACENTERID']

    return None


def get_distribution_id(distribution, lin):
    """
    Return distribution id if valid

    args:
        distribution - string or int - name of distribution or id
        lin - linode.api.Api object - connected Api class

    returns:
        int or None
    """
    # if it's a number, we'll ensure it's an int
    if distribution.isdigit():
        distribution = int(distribution)

    for d in lin.avail_distributions():
        if d['DISTRIBUTIONID'] == distribution or d['LABEL'] == distribution:
            return d['DISTRIBUTIONID']

    return None


def get_kernel_id(kernel, lin):
    """
    Return kernel id if valid

    args:
        kernel - string or int - name of kernel or id
        lin - linode.api.Api object - connected Api class

    returns:
        int or None
    """
    # if it's a number, we'll ensure it's an int
    if kernel.isdigit():
        kernel = int(kernel)

    for k in lin.avail_kernels():
        if type(kernel) is int:
            if (k['KERNELID'] == kernel):
                return k['KERNELID']
        else:
            if kernel in k['LABEL']:
                return k['KERNELID']

    return None


def linode_is_booted(linode_id, lin):
    """
    Return True if Linode is booted

    args:
        linode_id - int - linode identifier
        lin - linode.api.Api object - connected Api class

    returns:
        bool
    """
    data = lin.linode_list(LinodeID=linode_id)
    if data and data[0]['STATUS'] == 1:
        return True

    return False

def wait_for_job(job_id, linode_id, timeout, lin):
    """
    Wait until a job is complete up until mandatory timeout value

    args:
        job_id - int - job identifier
        timeout - int - time in seconds to wait for job to complete
        lin - linode.api.Api object - connected Api class

    returns:
        bool
    """
    count = 0
    while count <= timeout:
        job = lin.linode_job_list(LinodeID=linode_id, JobID=job_id)
        if job[0]['HOST_SUCCESS'] == 1:
            return True   
        time.sleep(2)
        count += 2

    return False


def main():
    module = AnsibleModule(
        argument_spec = dict(
            # Minimum args
            api_key = dict(required=True),
            name = dict(required=True, aliases=['hostname', 'label']),
            state = dict(default='present', choices=[
                'present', 'absent', 'rebooted', 'shutdown', 'booted']),

            # Args dependant on present (eg, if it's a new Linode, we need to know this stuff)
            datacenter = dict(required=False),
            plan = dict(required=False),
            payment_term = dict(required=False, choices=['1', '12', '24']),
            distribution = dict(required=False),
            kernel = dict(required=False, default='Latest 32 bit'),
            root_disk_size = dict(required=False),
            swap_disk_size = dict(required=False, default=256),
            root_password = dict(required=False),
            root_ssh_key = dict(required=False),

            # Non-required args
            display_group = dict(required=False),
            wait = dict(choices=BOOLEANS, default=False),
            timeout = dict(default=90)
        )
    )
    api_key = module.params.get('api_key')
    label = module.params.get('name')
    state = module.params.get('state')

    datacenter = module.params.get('datacenter')
    plan = module.params.get('plan')
    payment_term = module.params.get('payment_term')
    distribution = module.params.get('distribution')
    root_disk_size = module.params.get('root_disk_size')
    swap_disk_size = module.params.get('swap_disk_size')
    kernel = module.params.get('kernel')
    root_password = module.params.get('root_password')
    root_ssh_key = module.params.get('root_ssh_key')

    display_group = module.params.get('display_group')
    wait = module.params.get('wait')
    timeout = module.params.get('timeout')

    # Allow linode enviroment variables to be used if Ansible vars aren't set
    if not api_key and 'LINODE_API_KEY' in os.environ:
        api_key = os.environ['LINODE_API_KEY']
    
    lin = api.Api(api_key)

    # Try to pull down the domains associated with the API key, 
    # if this fails not much else will work so we give up
    try:
        domain = lin.domain_list()
    except api.ApiError as e:
        data = e.value[0]
        module.fail_json(
            msg = '%s: %s' % (data['ERRORCODE'], data['ERRORMESSAGE']))

    # Attempt to get the host
    linode_id = get_host_id(label, lin)

    # Start off with the basic Linode functionality
    if state != 'present':
        if not linode_id:
            # The server doesn't exist, so we're good
            if state == 'absent':
                module.exit_json(changed=False, name=label, state=state)
            else:
                module.fail_json(
                    msg = 'Unable to %s Linode, label "%s" not found' % (
                        state, label))

        # Perform one of the actions
        if state == 'rebooted':
            result = lin.linode_reboot(LinodeID=linode_id)
        elif state == 'booted':
           result = lin.linode_boot(LinodeID=linode_id)
        elif state == 'shutdown':
            result = lin.linode_shutdown(LinodeID=linode_id)
        elif state == 'absent':
            result = lin.linode_delete(LinodeID=linode_id, skipChecks=1)

        # Wait for the job to complete if requested
        if wait:
            job = wait_for_job(result['JobID'], linode_id, timeout, lin)
            if not job:
                module.fail_json(
                    msg = 'Timeout while waiting for job %s' % (job_result['JobID']))

        module.exit_json(changed=True, name=label, state=state)

    # Now for the heavy lifting...
    elif state == 'present':
        # Check plan is available, if so, return the id
        plan_id = get_plan_id(plan, lin)
        if not plan_id:
            module.fail_json(
                msg = 'Plan %s not found' % plan)

        # Check that datacenter is valid, if so return the id
        dc_id = get_datacenter_id(datacenter, lin)
        if not dc_id:
            module.fail_json(
                msg = 'Datacenter %s not found' % datacenter)

        # Get distribution id if it's valid
        dist_id = get_distribution_id(distribution, lin)
        if not dist_id:
            module.fail_json(
                msg = 'Distribution %s not found' % distribution)

        # Get kernel id if it's valid
        kernel_id = get_kernel_id(kernel, lin)
        if not kernel_id:
            module.fail_json(
                msg = 'Kernel %s not found' % kernel)

        # Get or create requested host
        linode_id = get_host_id(label, lin)
        if not linode_id:
            try:
                result = lin.linode_create(
                    DatacenterID=dc_id, PlanID=plan_id, PaymentTerm=payment_term)
            except lin.api.Api as e: 
                module.fail_json(
                    msg = 'Unable to create Linode. %s: %s' % (
                        e.values[0]['ERRORCODE'], e.values[0]['ERRORMESSAGE']))

            linode_id = result['LinodeID']

            # Update details to ensure we can find it again
            lin.linode_update(
                LinodeID=linode_id, label=label, lpm_displayGroup=display_group)

        # Check if we have a configuration profile, if not, create one from distribution
        # if there's no configuration profile, then nothing will happen.
        if not lin.linode_disk_list(LinodeID=linode_id):
            # Create the Linode from distribution
            kwargs = {'LinodeID': linode_id, 'DistributionID': dist_id, 
                      'rootPass': root_password, 'Size': root_disk_size, 'label': 'Root Partition'}
            if root_ssh_key:
                kwargs['rootSSHKey'] = root_ssh_key
            result = lin.linode_disk_createfromdistribution(**kwargs)
            root_disk_partition = result['DiskID']

            # Wait for the disk to be created, if requested
            if wait:
                wait_for_job(result['JobID'], linode_id, timeout, lin)
                
            # Create the swap disk
            kwargs = {'LinodeID': linode_id, 'Label': 'Swap Partition', 
                      'Type': 'swap', 'Size': swap_disk_size}
            result = lin.linode_disk_create(**kwargs)
            swap_disk_partition = result['DiskID']

            # Wait for the disk to be created, if requested
            if wait:
                wait_for_job(result['JobID'], linode_id, timeout, lin)

            # Create boot configuration
            result = lin.linode_config_create(
                LinodeID=linode_id, KernelID=kernel_id, Label=kernel, 
                DiskList='%d,%d' % (root_disk_partition, swap_disk_partition))

            config_id = result['ConfigID']

        # Update details
        lin.linode_update(
            LinodeID=linode_id, label=label, lpm_displayGroup=display_group)

        # Boot Linode
        if not linode_is_booted(linode_id, lin):
            result = lin.linode_boot(LinodeID=linode_id)

            # Wait for boot if requested
            if wait:
                wait_for_job(result['JobID'], linode_id, timeout, lin)

            module.exit_json(changed=True, linode_id=linode_id)

# this is magic, see lib/ansible/module_common.py
#<<INCLUDE_ANSIBLE_MODULE_COMMON>>

main()
