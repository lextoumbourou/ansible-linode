#!/usr/bin/python
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
            name = dict(required=True, aliases=['hostname', 'label']),
            datacenter = dict(required=False),
            api_key = dict(required=True),
            plan = dict(required=True),
            payment_term = dict(required=True),
            distribution = dict(required=True),
            root_password = dict(required=True),
            disk_size = dict(required=True),
            state = dict(required=False, default='present'),
            display_group = dict(required=False),
            disk_label = dict(required=False, default='ansible_disk'),
            swap_size = dict(required=False, default=256),
            root_ssh_key = dict(required=False)
            wait = dict(choices=BOOLEANS, default=False),
        )
    )
    label = module.params.get('name')
    datacenter = module.params.get('datacenter')
    api_key = module.params.get('api_key')
    plan = module.params.get('plan')
    payment_term = module.params.get('payment_term')
    distribution = module.params.get('distribution')
    root_password = module.params.get('root_password')
    disk_size = module.params.get('disk_size')
    state = module.params.get('state')
    display_group = module.params.get('display_group')
    swap_size = module.params.get('swap_size')
    root_ssh_key = module.params.get('root_ssh_key')
    wait = module.params.get('wait')

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

    # Check that the payment term is valid
    valid_payment_terms = [1, 12, 24]
    payment_term = int(payment_term)
    if payment_term not in valid_payment_terms:
        module.fail_json(
            msg = 'Payment term %s not valid' % datacenter)

    # Get or create requested host
    linode_id = get_host_id(label, lin)
    if not linode_id:
        try:
            res = lin.linode_create(
                DatacenterID=dc_id, PlanID=plan_id, PaymentTerm=payment_term)
        except lin.api.Api as e: 
            module.fail_json(
                msg = 'Unable to create Linode. %s: %s' % (
                    e.values[0]['ERRORCODE'], e.values[0]['ERRORMESSAGE']))

        linode_id = res['LinodeID']

        # Update details to ensure we can find it again
        lin.linode_update(
            LinodeID=linode_id, label=label, lpm_displayGroup=display_group)

    # Check if we have a configuration profile, if not, create one from distribution
    # if there's no configuration profile, then nothing will happen.
    if not lin.linode_disk_list(LinodeID=linode_id):
        # Create the Linode from distribution
        kwargs = {'LinodeID': linode_id, 'DistributionID': dist_id, 
                  'rootPass': root_password, 'Size': disk_size, 'label': 'Root Partition'}
        if root_ssh_key:
            kwargs['rootSSHKey'] = root_ssh_key
        res = lin.linode_disk_createfromdistribution(**kwargs)

        # Wait for the disk to be created, if requested
        if wait:
            wait_for_job(res['JOBID'])
            
        # Create the swap disk
        kwargs = {'LinodeID': linode_id, 'Label': 'Swap Partition', 
                  'Type': 'swap', 'Size': swap_size}
        res = lin.linode_disk_create(**kwargs)

        # Wait for the disk to be created, if requested
        if wait:
            wait_for_job(res['JOBID'])


    # Update details
    lin.linode_update(
        LinodeID=linode_id, label=label, lpm_displayGroup=display_group)

    # Check boot status
    if state == 'booted' and not linode_is_booted(linode_id, lin):
        res = lin.boot(LinodeID=linode_id)

        # Wait for boot if requested
        if wait:
            wait_for_job(res['JOBID'])

# this is magic, see lib/ansible/module_common.py
#<<INCLUDE_ANSIBLE_MODULE_COMMON>>

main()
