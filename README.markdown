# Linode Module for Ansible

## Status

This code is currently in Alpha and should not be used in production. I'm hoping to get a Beta release out as soon as possible.

## Overview

A simple way to manage devices host at Linode.

## How to Use

At this stage, just don't.

## Tests

Unfortunately, due to the way modules are imported into Ansible, it is difficult to implement unit tests for them. So, I've automated the process of testing through a number of subprocess.call commands to ansible/hacking/test-module command. To run them, you'll need a valid Linode API key, and a willingness to spend a couple of dollars building boxes and tearing them down. Hopefully one day Linode will have a Sandbox, negating the need for this but until then...

To run the tests:

* Clone the Ansible repo and make the test-module script executable

```
git clone git@github.com:ansible/ansible.git
chmod +x ansible/hacking/test-module
```

* Create the private.py file and update it with your API key and details

```
cp private-example.py private.py
vi private.py
```
