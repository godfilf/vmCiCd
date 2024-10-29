"""A Python Pulumi program"""

import pulumi
import pulumi.runtime
import pulumi_openstack as pstack
import openstack as os_sdk
import yaml
import os

os.environ["PULUMI_CONFIG_PASSPHRASE"] = ""

# importo un modulo custom che ho creato per la gestione dei recordset, i quali non sono tracciati da pulumi (li gestisce nova)
#from plugin.dns_manager import create_connection, manage_recordsets  # Importa le funzioni dal modulo
import plugin.dns_manager as dns

# importo tutte le var che ho creato da parte, perchè il __main__.py era diventato illeggibile
from plugin.globals import *

#import plugin.port_manager

conn = dns.create_connection(auth_url, username, password, tenant)

dns.manage_recordsets(conn, zone.id, instance_props)

pulumi.export(f"{tenantName}", tenantName)

# Recuperare i valori della configurazione definiti in Pulumi.dev.yaml
for vmType in instance_props.keys():
    vmCount = instance_props[vmType].get("vmCount")
    instanceName = instance_props[vmType].get("name")

    try:
        flavor = instance_props[vmType].get("flavor") if instance_props[vmType].get("flavor") else config.require("flavor")
    except NameError:
        flavor = config.require("flavor")
    
    try:
        image = instance_props[vmType].get("image") if instance_props[vmType].get("image") else config.require("image")
    except NameError:
        image = config.require("image")
    
    ## Creo il server group 
    if vmCount > 0:
        server_group = pstack.compute.ServerGroup(f"{instanceName}.{tenantName}",
            name=f"{instanceName}.{tenantName}",
            policies="anti-affinity",
            rules={
                "max_server_per_host": 2,
            }
        )

    server_group_to_remove = conn.compute.find_server_group(f"{instanceName}.{tenantName}")
    if server_group_to_remove is not None and vmCount == 0:
        conn.compute.delete_server_group(server_group_to_remove.id)

    
    # Creazione della risorsa OpenStack Instance da YAML
    if 'instance' in resources:
        #instance_props = resources['instance']['properties']
        #instance_props.get('name'),
    
        instances = []
        for i in range(vmCount):
            port = pstack.networking.Port(f"{instanceName}-{i}.port.{network.name}",
                name=f"{instanceName}.port.{network.name}",
                network_id=network.id,
                admin_state_up=True,
                no_security_groups=True,
                port_security_enabled=False
            )

            instance = pstack.compute.Instance(
                f"{instanceName}-{i}",
                name=f"{instanceName}-{i}",
                flavor_name=flavor,
                image_name=image,
                networks=[{
                    'uuid': network.id, 
                    'name': network.name,
                    'port': port.id
                }],
                key_pair="kollaJump_ecdsa",
                scheduler_hints=[{
                    "group": server_group.id,
                }],
                opts=pulumi.ResourceOptions(
                    depends_on=[
                        server_group,
                        port
                    ]
                )
            )
            instances.append(instance)
    
    for idx, instance in enumerate(instances):
        pulumi.export(f"{instanceName}-{idx}", instance)



