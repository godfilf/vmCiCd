"""A Python Pulumi program"""

import pulumi
import pulumi.runtime
import pulumi_openstack as pstack
import openstack as os_sdk
import yaml
import sys

# importo dei moduli custom per la gestione di alcuni componenti openstack, i quali non sono tracciati da pulumi 
import plugin.dns_manager as dns
import plugin.os_conn as os_conn
import plugin.sg_manager as sg

# importo tutte le var che ho creato, perchè il __main__.py era diventato illeggibile
from plugin.globals import *

#import plugin.port_manager

# Var globali
conn = os_conn.connection(auth_url, username, password, tenant)
dns.manage_recordsets(conn, zone.id, instance_props)
pulumi.export(f"{tenant_name}", tenant_name)

# Connessione e configurazione
conn = os_conn.connection(auth_url, username, password, tenant)
dns.manage_recordsets(conn, zone.id, instance_props)
pulumi.export(f"{tenant_name}", tenant_name)

# Funzione per ottenere una proprietà configurata
def get_config_property(vmType, prop_name, default_value):
    try:
        return instance_props[vmType].get(prop_name) or config.require(prop_name)
    except pulumi.ConfigMissingError as e:
        if prop_name == "keyPair": return None
        print(f"Errore: La configurazione '{prop_name}' è mancante per '{vmType}'. {e}")
        sys.exit(1)  # Termina il programma con un codice di uscita diverso da 0


# Funzione per creare un'istanza
def create_instance(instanceName, flavor, image, network, server_group, i):
    port = pstack.networking.Port(
        f"{instanceName}-{i}.port.{network.name}",
        name=f"{instanceName}.port.{network.name}",
        network_id=network.id,
        admin_state_up=True,
        no_security_groups=True,
        port_security_enabled=False
    )

    return pstack.compute.Instance(
        f"{instanceName}-{i}",
        name=f"{instanceName}-{i}",
        flavor_name=flavor,
        image_name=image,
        networks=[{'uuid': network.id, 'name': network.name, 'port': port.id}],
        scheduler_hints=[{"group": server_group.id}],
        opts=pulumi.ResourceOptions(depends_on=[server_group, port]),
        **optional_args
    )

# Creazione delle istanze
for vmType, props in instance_props.items():
    vmCount = props.get("vmCount", 0)
    instanceName = props.get("name", f"default-{vmType}")
    flavor = get_config_property(vmType, "flavor", "default-flavor")
    image = get_config_property(vmType, "image", "default-image")
    key_pair_name = get_config_property(vmType, "keyPair", "default-keypair") if get_config_property(vmType, "keyPair", "default-keypair") else None

    # Crea un dizionario di argomenti opzionali
    optional_args = {}
    if key_pair_name:
        optional_args["key_pair"] = key_pair_name
    
    server_group = sg.cd(conn, vmCount, instanceName, tenant_name)
    instances = [create_instance(instanceName, flavor, image, network, server_group, i) for i in range(vmCount)]


