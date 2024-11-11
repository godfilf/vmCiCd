import sys
import openstack as os_sdk
import ipaddress
import pulumi_openstack as pstack
from plugin.os_conn import connection
from plugin.globals import *
from types import SimpleNamespace


def get_network_id(auth_url, username, password, tenant, network_name):
    # Connessione a OpenStack
    conn = connection(auth_url, username, password, tenant)

    # Trova la rete con il nome specificato
    net = conn.network.find_network(network_name)
    if net is None:
        # Se la rete non esiste, solleva un errore
        raise ValueError(f"Rete con nome '{network_name}' non trovata.")
    
    # Restituisce l'ID della rete
    return net.id


def manage_network(auth_url, username, password, tenant, router_exist, network_name, vlans_list, vlan_tag, tenant_name, zone_name, config):
    # Connessione a OpenStack
    conn = connection(auth_url, username, password, tenant)

    # Logica condizionale in base al valore di network_exist
    network = conn.network.find_network(network_name)
    if not network :
        # Crea la rete e la subnet
        network = create_network(network_name, tenant_name, vlan_tag, zone_name)
        vlan_cidr = next((vlan["subnet"] for vlan in vlans_list if vlan["id"] == vlan_tag), "10.0.0.0/24")
        subnet = create_subnet(router_exist, network_name, network.id, vlan_tag, tenant_name, vlan_cidr)
    else:
        # Usa la rete esistente se trovata
        pulumi.log.info(f"Rete '{network_name}' trovata; utilizzo la rete esistente.")
        network = pstack.networking.get_network(name=network_name)
        #network = pstack.networking.Network.get("network_resource", network.id)
        print(f"Var Network = {type(network)}")

        vlan_cidr = "10.0.0.0/24"  # Valore di default
        if vlan_tag and vlans_list:
            # Cerca vlan_cidr corrispondente al vlan_tag
            vlan_cidr = next((vlan["subnet"] for vlan in vlans_list if vlan["id"] == vlan_tag), vlan_cidr)
    
        # Ottieni le subnet associate alla rete
        subnets = conn.network.subnets(network_id=network.id)
        
        # Controlla se la subnet esiste già, altrimenti crea una nuova subnet
        subnet = next((sn for sn in subnets if sn.cidr == vlan_cidr), None)
        
        if not subnet:
            # Crea la subnet se non esiste
            subnet = create_subnet(router_exist, network_name, network.id, vlan_tag, tenant_name, vlan_cidr)
    
    return network, subnet


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


def create_subnet(router_exist, network_name, network_id, vlan_tag, tenant_name, cidr="10.0.0.1/24", dns_nameservers=None):

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
        dns_nameservers=dns_nameservers if dns_nameservers else ["8.8.8.8", "1.1.1.1"]
    )
    return subnet

