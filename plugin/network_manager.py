import sys
import openstack as os_sdk
import ipaddress
import pulumi_openstack as pstack
from plugin.os_conn import connection
from plugin.globals import *
from types import SimpleNamespace


def get_network_id(auth_url, username, password, tenant, network_name):
    """
    Ottiene l'ID della rete con il nome specificato da OpenStack.

    Args:
        auth_url (str): URL di autenticazione di OpenStack.
        username (str): Nome utente per OpenStack.
        password (str): Password per OpenStack.
        tenant (str): Nome del tenant in OpenStack.
        network_name (str): Nome della rete di cui si vuole ottenere l'ID.
    
    Returns:
        str: ID della rete trovata.
    
    Raises:
        ValueError: Se la rete con il nome specificato non esiste.
    """
    # Connessione a OpenStack
    conn = connection(auth_url, username, password, tenant)

    # Trova la rete con il nome specificato
    net = conn.network.find_network(network_name)
    if net is None:
        # Se la rete non esiste, solleva un errore
        raise ValueError(f"Rete con nome '{network_name}' non trovata.")
    
    # Restituisce l'ID della rete
    return net.id


def manage_network(auth_url, username, password, tenant, network_exist, network_name, vlans_list, vlan_tag, tenant_name, zone_name, config):
    """
    Gestisce la creazione o l'uso di una rete e una subnet in OpenStack.

    Args:
        auth_url (str): URL di autenticazione di OpenStack.
        username (str): Nome utente per OpenStack.
        password (str): Password per OpenStack.
        tenant (str): Nome del tenant in OpenStack.
        network_exist (bool): Se True, verifica se la rete esiste.
        network_name (str): Nome della rete da verificare o creare.
    """
    # Connessione a OpenStack
    conn = connection(auth_url, username, password, tenant)

    # Logica condizionale in base al valore di network_exist
    if network_exist:
        # Controlla se la rete esiste
        network = conn.network.find_network(network_name)
        if network:
            # Usa la rete esistente se trovata
            pulumi.log.info(f"Rete '{network_name}' trovata; utilizzo la rete esistente.")
            network = pstack.networking.get_network(name=network_name)

            # Controlla se la subnet è associata alla rete
            subnets = conn.network.subnets(network_id=network.id)
            if not subnets:
                # Crea una subnet se nessuna esiste per questa rete
                vlan_cidr = next(
                    (vlan["subnet"] for vlan in vlans_list if vlan["id"] == vlan_tag),
                    "10.0.0.1/24"  # Subnet di fallback se non viene trovata la VLAN
                )

                subnet = create_subnet(network, vlan_cidr)
            else:
                subnet = next(iter(subnets), None)
                pulumi.log.info(f"Subnet già esistente per la rete '{network_name}'. Selezionata la prima rete '{subnet.name}'.")

        else:
            # La rete è richiesta ma non esiste
            raise ValueError(f"Rete '{network_name}' non trovata. Imposta `network_exist=False` per crearla.")
    
    else:
        # La rete non esiste, procedi con la creazione
        network = conn.network.find_network(network_name)

        #subnets = conn.network.subnets(network_id=network.id)
        #if subnets:
        #    vlan_cidr = next((vlan["subnet"] for vlan in vlans_list if vlan["id"] == vlan_tag), "10.0.0.1/24")
        #    subnet = next((sn for sn in subnets if sn.cidr == vlan_cidr), None)

        if network:
            pulumi.log.info(f"Rete '{network_name}' già esistente. Imposta `network_exist=True` se desideri usarla.")
            pulumi.runtime.exit_with_error("Operazione interrotta manualmente per mancata condizione.")
        else:
            # Crea la rete e la subnet
            network = create_network(network_name, tenant_name, vlan_tag, zone_name)
            vlan_cidr = next((vlan["subnet"] for vlan in vlans_list if vlan["id"] == vlan_tag), "10.0.0.1/24")
            subnet = create_subnet(network_name, network.id, vlan_tag, tenant_name, vlan_cidr)
            #network = SimpleNamespace(id=network.id, name=network_name)
    
    return network, subnet


def create_network(network_name, tenant, vlan_tag, zone_name):
    """
    Crea una rete in OpenStack usando Pulumi.

    Args:
        network_name (str): Nome della rete da creare.
    
    Returns:
        network: Oggetto rete creato.
    """
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


def create_subnet(network_name, network_id, vlan_tag, tenant_name, cidr="10.0.0.1/24", dns_nameservers=None):
    """
    Crea una subnet associata a una rete esistente.

    Args:
        network: Oggetto rete associato alla subnet.
        cidr (str): CIDR per la subnet (es. "192.168.1.0/24").
        dns_nameservers (list): Lista di DNS per la subnet.
    
    Returns:
        subnet: Oggetto subnet creata.
    """
    subnet_name = f"subnet_vlan_{vlan_tag}.{network_name}" if vlan_tag else f"subnet_vlan_def.{network_name}"

    subnet_cidr = ipaddress.ip_network(cidr)
    
    # Calcola il gateway e gli indirizzi del pool
    gw = str(subnet_cidr.network_address + 2)      # Gateway 10.1.0.2
    pool_start = str(subnet_cidr.network_address + 3)  # Inizio pool 10.1.0.3
    pool_end = str(subnet_cidr.network_address + 253)  # Fine pool 10.1.0.253

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

