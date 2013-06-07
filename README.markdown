# Linode Module for Ansible

## Overview

A simple way to manage Linodes via Ansible. Supports creating, destroying, shutting down, rebooting and starting a Linode.

## Installation

Copy the library directly into the directory where your Playbooks are located.

```
> cp -R library /etc/ansible/company_name/
```

## Options

<table>
<tr>
<th class="head">parameter</th>
<th class="head">required</th>
<th class="head">default</th>
<th class="head">choices</th>
<th class="head">comments</th>
</tr>
<tr>
<td>datacenter</td>
<td>no</td>
<td></td>
<td><ul></ul></td>
<td>String or id representing the Linode's datacenter (http://www.linode.com/api/utility/avail.datacenters)</td>
</tr>
<tr>
<td>name</td>
<td>yes</td>
<td></td>
<td><ul></ul></td>
<td>Name/label/hostname of the Linode instance</td>
</tr>
<tr>
<td>kernel</td>
<td>no</td>
<td></td>
<td><ul></ul></td>
<td>String or id representing the kernel for the configuration profile (http://www.linode.com/api/utility/avail.kernels)</td>
</tr>
<tr>
<td>swap_disk_size</td>
<td>no</td>
<td></td>
<td><ul></ul></td>
<td>Size of swap disk in MB</td>
</tr>
<tr>
<td>root_disk_size</td>
<td>no</td>
<td></td>
<td><ul></ul></td>
<td>Size of root disk in MB</td>
</tr>
<tr>
<td>root_ssh_key</td>
<td>no</td>
<td></td>
<td><ul></ul></td>
<td>Optionally include an ssh key for root</td>
</tr>
<tr>
<td>payment_term</td>
<td>no</td>
<td>1</td>
<td><ul><li>1</li><li>12</li><li>24</li></ul></td>
<td>Length of time in months for payment term</td>
</tr>
<tr>
<td>state</td>
<td>yes</td>
<td></td>
<td><ul><li>present</li><li>absent</li><li>rebooted</li><li>shutdown</li><li>booted</li></ul></td>
<td>Present will create the Linode if it doesn't exist, absent will destroy it (be careful!), shutdown, booted and rebooted will perform the action the name implies, all except rebooted are idempotent actions</td>
</tr>
<tr>
<td>display_group</td>
<td>no</td>
<td></td>
<td><ul></ul></td>
<td>Optionally specify which display group to place the Linode in</td>
</tr>
<tr>
<td>plan</td>
<td>no</td>
<td></td>
<td><ul></ul></td>
<td>String or id representing the Linode plan (http://www.linode.com/api/utility/avail.linodeplans)</td>
</tr>
<tr>
<td>timeout</td>
<td>no</td>
<td>120</td>
<td><ul></ul></td>
<td>optionally specify a timeout period in seconds to wait</td>
</tr>
<tr>
<td>distribution</td>
<td>no</td>
<td></td>
<td><ul></ul></td>
<td>String or id representing the OS on your server (http://www.linode.com/api/utility/avail.distributions)</td>
</tr>
<tr>
<td>api_key</td>
<td>yes</td>
<td></td>
<td><ul></ul></td>
<td>API key use to manage your Linodes</td>
</tr>
<tr>
<td>root_password</td>
<td>no</td>
<td></td>
<td><ul></ul></td>
<td>String representing the root password for the Linode (only changed at node creation)</td>
</tr>
<tr>
<td>wait</td>
<td>no</td>
<td></td>
<td><ul></ul></td>
<td>wait for Linode instance to be in state 'booted' before returning</td>
</tr>
</table>

## Examples

* Create a new Linode called 'server_name' on the Linode 512 payment plan, does nothing if device already exists

```
local_action: linode_manager api_key=1234 name=server_name  plan='Linode 512' datacenter=Tokyo payment_term=1 kernel=3.7.5-linode48 state=present root_disk_size=24320 swap_disk_size=256 root_password=hunter2 wait=true
```
* Restart a Linode called webserver01 and wait for it to finish booting

```
local_action: linode_manager name=webserver01 wait=yes
```

## Dependencies

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
