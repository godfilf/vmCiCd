import pulumi_openstack as pstack
from plugin.os_conn import connection
from plugin.globals import *
from plugin.network_manager import create_subnet


def create_port_with_fixed_ip(auth_url, username, password, tenant, port_name, network, subnet):

    cidr = next((vlan["subnet"] for vlan in vlans_list if vlan["id"] == vlan_tag), "10.0.0.0/24")
    
    # Ottieni il prefisso dell'indirizzo IP della subnet
    ip_address = cidr.split('/')[0]
    ip_prefix = '.'.join(ip_address.split('.')[:3])
    desired_ip = f"{ip_prefix}.2"  # Imposta l'IP desiderato come xxx.yyy.zzz.2

    # Crea una porta con un IP fisso specificato
    return pstack.networking.Port(
        resource_name=port_name,
        name=port_name,
        network_id=network.id,
        admin_state_up=True,
        fixed_ips=[{"subnet_id": subnet.id, "ip_address": desired_ip}],  # Imposta l'IP fisso specifico
        tags=["pulumi_port_res"],
        no_security_groups=True,
        port_security_enabled=False
    )


def create_port_without_fixed_ip(port_name, network_id, subnet_id):
    return pstack.networking.Port(
        resource_name=port_name,
        name=port_name,
        network_id=network_id,  # Specifica la rete a cui la porta si connette
        fixed_ips=[{"subnet_id": subnet_id, "ip_address": None}],
        admin_state_up=True,  # Attiva la porta
        tags=["pulumi_port_res"],
        no_security_groups=True,
        port_security_enabled=False
    )

def import_port_with_fixed_ip(network, subnet):

    cidr = next((vlan["subnet"] for vlan in vlans_list if vlan["id"] == vlan_tag), "10.0.0.0/24")
    
    # Ottieni il prefisso dell'indirizzo IP della subnet
    ip_address = cidr.split('/')[0]
    ip_prefix = '.'.join(ip_address.split('.')[:3])
    desired_ip = f"{ip_prefix}.2"  # Imposta l'IP desiderato come xxx.yyy.zzz.2

    existing_router_port = pstack.networking.get_port(name=router_port_name)
    return pstack.networking.Port(
        resource_name=router_port_name,
        name=router_port_name,
        network_id=network.id,
        admin_state_up=True,
        no_security_groups=True,
        fixed_ips=[{"subnet_id": subnet.id, "ip_address": desired_ip}],
        opts=pulumi.ResourceOptions(import_=existing_router_port.id),
        tags=["pulumi_port_res"],
        port_security_enabled=False 
    )

