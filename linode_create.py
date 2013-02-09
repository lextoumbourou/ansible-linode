#!/usr/bin/python
import sys
import warnings

# I have to catch the warning here because the linode api has a Runtime Warning
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    try:
        from linode import api
    except ImportError:
        print "failed=True msg='python-linode required for this module'"
        sys.exit(1)


def host_exists(label, lin):
    """
    Return True if specified host is already created or False

    args:
        label - string - hostname
        lin - linode.api.Api object - connected Api class

    returns:
        bool
    """
    # See if the hostname is already in the domain list, if not, we'll create it 
    for host in lin.linode_list():
        if host['LABEL'] == label:
            return True
    return False


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
        if p['PLANID'] == plan:
            return p['PLANID']

        if p['LABEL'] == plan:
            return p['PLANID']

    return None


def get_datacenter_id(datacenter, lin):
    """
    Return datacenter id if valid

    args:
        datacenter - string or int - name of datacenter
        lin - linode.api.Api object - connected Api class
    
    returns:
        int or None
    """
    # if it's a number, we'll ensure it's an int
    try:
        datacenter = int(datacenter)
    except ValueError:
        pass

    for dc in lin.avail_datacenters():
        if type(datacenter) is int:
            if dc['DATACENTERID'] == datacenter:
                return dc['DATACENTERID']
        # If it's not an int, I'll search the datacenter string for the 
        # specified datacenter, allowing for 'Tokyo' to match 'Tokyo, JP' etc
        else:
            if datacenter in dc['LOCATION']:
                return dc['DATACENTERID']

    return None


def main():
    module = AnsibleModule(
        argument_spec = dict(
            name = dict(required=True, aliases=['hostname', 'label']),
            datacenter = dict(required=False),
            api_key = dict(required=True),
            plan = dict(required=True),
        )
    )
    label = module.params.get('name')
    datacenter = module.params.get('datacenter')
    api_key = module.params.get('api_key')
    plan = module.params.get('plan')

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
    datacenter_id = get_datacenter_id(datacenter, lin)
    if not datacenter_id:
        module.fail_json(
            msg = 'Datacenter %s not found' % datacenter)

    # Check that the payment term is valid, return the id if so



    if not host_exists(label, lin):
        host_create(label, plan, datacenter, lin)
       

# this is magic, see lib/ansible/module_common.py
#<<INCLUDE_ANSIBLE_MODULE_COMMON>>

main()
