import pulumi_openstack as pstack
from plugin.os_conn import connection
from plugin.globals import *
from plugin.network_manager import create_subnet


def create_port_with_fixed_ip(auth_url, username, password, tenant, port_name, network, subnet):
    # Crea una connessione
    conn = connection(auth_url, username, password, tenant)
    cidr = next((vlan["subnet"] for vlan in vlans_list if vlan["id"] == vlan_tag), "10.0.0.1/24")
    
    if network_exist:
        # Recupera tutte le subnet e trova quella associata al network_id specificato
        subnets = list(conn.network.subnets())  # Ottiene tutte le subnet disponibili
        subnet = next((s for s in subnets if s.network_id == network.id), None)

    # Se non c'è una subnet associata e `network_exist` è True, crea la subnet
    if subnet is None:
        subnet = create_subnet(network_name, network.id, vlan_tag, tenant_name, cidr)
        subnets = list(conn.network.subnets())  # Ottiene tutte le subnet disponibili
        subnet = next((s for s in subnets if s.network_id == network.id), None)

    # Ottieni il prefisso dell'indirizzo IP della subnet
    ip_address = cidr.split('/')[0]
    ip_prefix = '.'.join(ip_address.split('.')[:3])
    #ip_prefix = cidr.rsplit('.', 1)[0]  # Prende il prefisso fino al terzo ottetto
    desired_ip = f"{ip_prefix}.2"  # Imposta l'IP desiderato come xxx.yyy.zzz.2

    # Crea una porta con un IP fisso specificato
    return pstack.networking.Port(
        resource_name=port_name,
        name=port_name,
        network_id=network.id,
        admin_state_up=True,
        fixed_ips=[{"subnet_id": subnet.id, "ip_address": desired_ip}],  # Imposta l'IP fisso specifico
        no_security_groups=True,
        port_security_enabled=False
    )


def create_port_without_fixed_ip(port_name, network_id):
    # Crea una porta senza IP fisso (fixed_ip)
    return pstack.networking.Port(
        resource_name=port_name,
        name=port_name,
        network_id=network_id,  # Specifica la rete a cui la porta si connette
        admin_state_up=True,  # Attiva la porta
        fixed_ips=[],  # Nessun IP fisso specificato
        no_security_groups=True,
        port_security_enabled=False
    )
