# Linode Module for Ansible

## Status

Currently in beta. This is my first Ansible module and I'm still getting my head around how they work, so bare with me a bit.
If you are brave and want to play with it please go right ahead.

## Overview

A simple way to manage Linodes via Ansible. Supports creating, destroying, shutting down, rebooting and starting a Linode.

## Installation

Copy the library direction into the directory where you Playbooks are located.

```
> cp -R library /etc/ansible/company_name/
```
## Playbook Examples

Create a Linode
```
local_action: linode_manager api_key=abc123 name=webserver datacenter=Tokyo
              plan="Linode 512" payment_term=1 distribution="Ubuntu 12.04 LTS"
              kernel="3.7.5-linode48" root_disk_size=24320 swap_disk_size=256
              root_password=hunter2 display_group="Production" state=present wait=true
```

Remove a Linode
```
local_action: linode_manager api_key=123abc name=badserver state=absent
```

Shutdown a Linode
```
local_action: linode_manager api_key=123abc name=webserver state=shutdown'
```

## Options

Coming soon

## Dependacies

Requires **python-linode** available via pip.

```bash
> sudo pip install python-linode
```

## Limitations

* Only supports the creation of 1 disk from a distribution
* No support for NodeBalancer, StackScripts and DNS (again, perhaps a separate module should tackle this?)

## Tests

Unfortunately, due to the way modules are imported into Ansible, it is difficult to implement unit tests for them. So, I've automated the process of testing through a number of subprocess.call commands to ansible/hacking/test-module command. To run them, you'll need a valid Linode API key, and a willingness to spend a couple of dollars building boxes and tearing them down. Hopefully one day Linode will have a Sandbox, negating the need for this but until then...

To run the tests:

* Clone the Ansible repo and make the test-module script executable

```bash
> git clone git@github.com:ansible/ansible.git
> chmod +x ansible/hacking/test-module
```

* Create the private.py file and update it with your API key and details

```
> cp private-example.py private.py
> vi private.py
```

* Run test_scripts.py (by default, the scripts will charge your account, so be careful!)

```
> python test_scripts
```
