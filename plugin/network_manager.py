#from plugin.globals import *
import sys
import openstack as os_sdk
import ipaddress
import pulumi
import pulumi_openstack as pstack
from plugin.os_conn import connection
from plugin.globals import auth_url, username, password, tenant

def get_network_id(auth_url, username, password, tenant, network_name):
    conn = connection(auth_url, username, password, tenant)

    net = conn.network.find_network(network_name)
    if net is None:
        raise ValueError(f"Rete con nome '{network_name}' non trovata.")
    
    return net.id

def import_existing_network(network_name, tenant, vlan_tag, zone_name, network):
    network = pstack.networking.Network(
        resource_name=f"{network_name}",
        name=network_name,
        segments=[{
            "network_type": "vlan",
            "physical_network": "physnet1",
            "segmentation_id": vlan_tag,
        }],
        opts=pulumi.ResourceOptions(import_=network.id),
    )
    return network

def create_network(network_name, tenant, vlan_tag, zone_name):
    # Crea una nuova rete con opzioni di rilevamento modifiche
    network = pstack.networking.Network(
        resource_name=f"{network_name}",
        name=network_name,
        dns_domain=zone_name,
        segments=[{
            "network_type": "vlan",
            "physical_network": "physnet1",
            "segmentation_id": vlan_tag,
        }],
        admin_state_up=True,
        tags=[f'managed-by-pulumi']  # Aggiungi un tag di gestione
    )
    return network


def create_subnet(router_exist, network_name, network_id, vlan_tag, tenant_name, cidr="10.0.0.0/24", dns_nameservers=None):

    subnet_name = f"subnet_vlan_{vlan_tag}.{network_name}" if vlan_tag else f"subnet_vlan_def.{network_name}"

    subnet_cidr = ipaddress.ip_network(cidr)
    
    # Calcola il gateway e gli indirizzi del pool
    if router_exist:
        gw = str(subnet_cidr.network_address + 1)      
        pool_start = str(subnet_cidr.network_address + 2)
    else:
        gw = str(subnet_cidr.network_address + 2)
        pool_start = str(subnet_cidr.network_address + 3)

    pool_end = str(subnet_cidr.network_address + 253)

    subnet = pstack.networking.Subnet(
        resource_name=subnet_name,
        name=subnet_name,
        network_id=network_id,
        cidr=cidr,
        ip_version=4,
        enable_dhcp=True,
        dns_publish_fixed_ip=True,
        gateway_ip=gw,
        allocation_pools=[{
            "end": pool_end,
            "start": pool_start,
        }],
#        opts=pulumi.ResourceOptions(depends_on=[network]),
        dns_nameservers=dns_nameservers if dns_nameservers else ["8.8.8.8", "1.1.1.1"]
    )
    return subnet

