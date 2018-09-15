


# OpenShift on AWS
This project automates the installation of OpenShift on AWS using ansible.  It follows the [OpenShift + AWS Reference Architecture](https://access.redhat.com/documentation/en-us/reference_architectures/2018/html/deploying_and_managing_openshift_3.9_on_amazon_web_services/) closely. By default the following is deployed, 3 masters, 3 Infra nodes, 3 app nodes, Logging (EFK), Metrics, Prometheus & Grafana. SSH access is restricted into the cluster by allowing only the bastion to reach each Node,  ssh is then proxied from the ansible control host via the bastion accesing nodes by hostname.  `ssh <ec2 instance >`    To quickly standup an ansible deploy host have a look at [vagrant-rhel](https://github.com/hornjason/vagrant-rhel).


## Topology
![topology](https://access.redhat.com/webassets/avalon/d/Reference_Architectures-2018-Deploying_and_Managing_OpenShift_3.9_on_Amazon_Web_Services-en-US/images/e3a4c4e1504f006cbdb61a787b298d39/topology.png)


## Virtual Machine Sizing
The following table outlines the sizes used to better understand the vCpu and Memory quotas needed to successfully deploy OpenShift on Azure.  Verify your current subscription quotas meet the below requirements.

Instance | Hostname | # |VM Size | vCpu's | Memory  
-------- | -------- | - | ------ | ------ | ----- 
Master Nodes | ocp-master-# | 3 | Standard_D4s_v3 | 4 | 16  
Infra Nodes | ocp-infra-# | 3 | Standard_D4s_v3 | 4 | 16   
App Nodes | ocp-app-# | 3 | Standard_D2S_v3 | 2 | 8  
CNS Nodes | ocp-cns-# | 3 | Standard_D8s_v3 | 8 | 32 
Bastion | bastion | 1 | Standard_D1 | 1 | 3.5
Total | | 13 | | 55 | 219.5Gb 


VM sizes can be configured from defaults by changing the following variables, if the sizes chosen are below minimum OpenShift requirements deployment checks will fail.


| Variable | VM Size
| -- | ---- |
| vm_size_master: | Standard_D4s_v3
| vm_size_infra: | Standard_D4s_v3
| vm_size_node:  | Standard_D2s_v3
| vm_size_bastion: | Standard_D1


>After installing and setting up AWS CLI the following command can be used to show available VM Resources in a location.
```
az vm list-usage --location westus --output table
```

## Pre-Reqs

Reqs
A few Pre-Reqs need to be met and are documented in the Reference Architecture already.  **Ansible 2.5 is required**, the ansible control host running the deployment needs to be registered and subscribed to `rhel-7-server-ansible-2.5-rpms`.  Currently the AWS CLI is setup on the ansible control host running the deployment using the playbook `aws_cli.yml` or by following instructions here, [Azure CLI Setup](https://docs.microsoft.com/en-us/cli/azure/create-an-azure-service-principal-azure-cli?toc=%2Fazure%2Fazure-resource-manager%2Ftoc.json&view=azure-cli-latest).

 1. Ansible control host setup:
    Register the ansible control host used for this deployment with valid RedHat subscription thats able to pull down ansible     2.5 or manually install ansible 2.5 along with atomic-openshift-utils.  To quickly create a VM using Vagrant try out [vagrant-rhel](https://github.com/hornjason/vagrant-rhel).
```
    sudo subscription-manager register --username < username > --password < password >
    sudo subscription-manager attach --pool < pool_id >
    sudo subscription-manager repos --disable=*
    sudo subscription-manager repos \
    --enable="rhel-7-server-rpms" \
    --enable="rhel-7-server-extras-rpms" \
    --enable="rhel-7-server-ose-3.9-rpms" \
    --enable="rhel-7-fast-datapath-rpms" \
    --enable="rhel-7-server-ansible-2.5-rpms"

    sudo yum -y install ansible atomic-openshift-utils git
```

 2. Clone this repository

 ```
 git clone https://github.com/hornjason/ansible-ocp-aws.git; cd ansible-ocp-aws
 ```
 3.  Install AWS CLI,  using playbook included or manually following above directions.
 ```
 ansible-playbook aws-cli.yml
 ```
 4. Authenticate with AWS,  
 6. Copy vars.yml.example to vars.yml
  ```
  cp vars.yml.example vars.yml 
  ```
 7. Fill out required variables below.
 8. Due to bug https://github.com/ansible/ansible/issues/40332 if the ansible control host used to deploy from has LANG set to something other than `en` then you must  `unset LANG`
 9. Due to bug https://github.com/openshift/openshift-ansible/pull/9971, 2 OCS registries will fail to install unless you clone https://github.com/openshift/openshift-ansible.git 
 - cd /usr/share/ansible/; mv openshift-ansible openshift-ansible-rpm; git clone https://github.com/openshift/openshift-ansible.git; cd -

## Required Variables
Most defaults are specified in `role/aws/defaults/main.yml`,  Sensitive information is left out and should be entered in `vars.yml`.  Below are required variables that should be filled in before deploying.
clusterid: "awscluster"
dns_domain: "example.com"
aws_region: "us-east-1"

 - **aws_region**:  - AWS location for deployment ex. `us-east-1`
 - **clusterid**:  - Azure Resource Group ex. `test-rg`
 - **admin_user**: - SSH user that will be created on each VM ex. `cloud-user`
 - **admin_pubkey**: - Copy paste the Public SSH key that will be added to authorized_keys on each VM ex.
 `ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAB`
 - **admin_privkey**: - Path to the private ssh key associated with the public key above.  ex. `'~/.ssh/id_rsa`
 - **rhsm_user**: - If subscribing to RHSM using username / password, fill in username
 - **rhsm_pass**: - If subscribing to RHSM using username / password, fill in passowrd for RHSM 
 - **rhsm_key**: -  If subscribing to RHSM using activation key and orgId fill in activation key here.
 - **rhsm_org**: - If subscribing to RHSM using activation key and orgId fill in orgId here.
 - **rhsm_broker_pool**: - If you have a broker pool id for masters / infra nodes fill it in here.  This will be used to for all masters/infra nodes.  If you only have one pool id to use make this the same as `rhsm_node_pool`.
 - **rhsm_node_pool**: - If you have a application pool id for app nodes fill it in here.  This will be used for all application nodes.  If you only have one pool id to use make this the same as `rhsm_broker_pool`
 - **rhsm_ocs_pool**: - If you have a application pool id for openshit container nodes fill it in here.  This will be used for all storage nodes.  If you only have one pool id to use make this the same as `rhsm_broker_pool`
Number of Nodes
 - **master_nodes**: Defaults to 3 
 - **infra_nodes**:  Defaults to 3 
 - **app_nodes**:    Defaults to 3 

Optional Variables:

 - **vnet_cidr**: - Can customize as needed, ex `"10.0.0.0/16"`
By Default the HTPasswdPasswordIdentityProvider is used but can be customized,  this will be templated out to the ansible hosts file.  By default htpasswd user is added.
- **openshift_master_htpasswd_users**: - Contains the user: < passwd hash generated from htpasswd -n user >
- **deploy_cns**: true
- **deploy_cns_to_infra**: true  - This will deploy CNS on Infra nodes and **NOT** create separate CNS nodes
- **deploy_metrics**: true
- **deploy_logging**: true
- **deploy_prometheus**: true
- **metrics_volume_size**: '20Gi'
- **logging_volume_size**: '100Gi'
- **prometheus_volume_size**: '20Gi'

## Deployment
After all pre-reqs are met and required variables have been filled out the deployment consists of running the following:
`ansible-playbook deploy.yml -e @vars.yml`

The ansible control host running the deployment will be setup to use ssh proxy through the bastion in order to reach all nodes.  The openshift inventory `hosts` file will be templated into the project root directory and used for the Installation.  

## Destroy
`ansible-playbook destroy.yml -e@vars.yml`
