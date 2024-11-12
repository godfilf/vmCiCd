from plugin.globals import *
import sys
import openstack as os_sdk
import ipaddress
import pulumi_openstack as pstack
from plugin.os_conn import connection
from types import SimpleNamespace

conn = connection(auth_url, username, password, tenant)

def get_network_id(auth_url, username, password, tenant, network_name):

    # Trova la rete con il nome specificato
    net = conn.network.find_network(network_name)
    if net is None:
        # Se la rete non esiste, solleva un errore
        raise ValueError(f"Rete con nome '{network_name}' non trovata.")
    
    # Restituisce l'ID della rete
    return net.id


#def get_or_create_network():
#    existing_network = conn.network.find_network(network_name)
#    
#    if not existing_network:
#        network = create_network(network_name, tenant_name, vlan_tag, zone_name)
#    else:
#        network = pstack.networking.Network.get(network_name, existing_network.id)
#    
#    subnet = network.id.apply(lambda id: get_or_create_subnet(router_exist, network_name, id, vlan_tag, tenant_name))
#
#    return network, subnet
#
#
#def get_or_create_subnet(router_exist, network_name, network_id, vlan_tag, tenant_name):
#    subnets = conn.network.subnets(network_id=network_id)
#    vlan_subnet = next((sn for sn in subnets if sn.cidr == vlan_cidr), None)
#
#    if not vlan_subnet:
#        return create_subnet(router_exist, network_name, network_id, vlan_tag, tenant_name, vlan_cidr)
#    else:
#        existing_subnet = conn.network.find_subnet(vlan_subnet.id)
#        return pstack.networking.Subnet.get(existing_subnet.name, existing_subnet.id)


def create_network(network_name, tenant, vlan_tag, zone_name):
    # Crea una nuova rete
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

    # Crea una nuova subnet associata alla rete
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

