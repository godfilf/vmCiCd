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
import plugin.server_groups_manager as sg
import plugin.volumes_manager as vols

# importo tutte le var che ho creato, perchè il __main__.py era diventato illeggibile
from plugin.globals import *

#import plugin.port_manager

# Connessione e configurazione
conn = os_conn.connection(auth_url, username, password, tenant)
dns.manage_recordsets(conn, zone.id, instance_props)
pulumi.export(f"{tenant_name}", tenant_name)

# Funzione per ottenere una proprietà configurata
def get_config_property(vmType, prop_name, default_value):
    try:
        return instance_props[vmType].get(prop_name) or config.require(prop_name)
    except pulumi.ConfigMissingError as e:
        if prop_name in {"keyPair", "volumes"}: return None
        print(f"Errore: La configurazione '{prop_name}' è mancante o errata per '{vmType}'. {e}")
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
    volumes_data = get_config_property(vmType, "volumes", []) 
    volumes = vols.volume_create({f"{instanceName}.vol-{i}.{tenant_name}": vol_data for i, vol_data in enumerate(volumes_data)}, image) if volumes_data else {}

    # Configura i dispositivi per l'istanza
    block_devices = []
    boot_index_counter = 1  
    for i, vol in enumerate(volumes.values()):
        # Trova il vol_data corrispondente in volumes_data
        vol_data_dict = volumes_data[i]
        
        # Determina se il volume corrente è bootable
        is_bootable = vol_data_dict.get("bootable", False)

        # Calcola il boot_index
        if is_bootable:
            boot_index = 0  # Solo un volume deve essere bootable
        else:
            boot_index = boot_index_counter
            boot_index_counter += 1  # Incrementa il contatore per i volumi non bootable
    

        # Verifica se il volume è esistente usando l'UUID
        if not hasattr(vol, 'name'):
            block_devices.append(
                pstack.compute.InstanceBlockDeviceArgs(
                    source_type="volume",
                    #boot_index=0 if is_bootable else i + 1,
                    boot_index=boot_index,
                    delete_on_termination=False,
                    destination_type="volume",
                    uuid=vol["id"]  # Utilizza l'UUID del volume esistente
                )
            )
        else:
            block_devices.append(
                pstack.compute.InstanceBlockDeviceArgs(
                    source_type="volume",
                    boot_index=boot_index,
                    delete_on_termination=False,
                    destination_type="volume",
                    uuid=vol.id,
                    volume_size=vol.size,
                )
            )
    # Debug: stampa il contenuto di block_devices
    for bd in block_devices:
        print(f"Block Device: UUID={bd.uuid}, Boot Index={bd.boot_index}")

    optional_components = {
        "key_pair": key_pair_name,
        "block_devices": block_devices
    }

    # Aggiunge solo i componenti non None a optional_args
    for key, value in optional_components.items():
        if value is not None:
            optional_args[key] = value
    
    server_group = sg.cd(conn, vmCount, instanceName, tenant_name)
    instances = [create_instance(instanceName, flavor, image, network, server_group, i) for i in range(vmCount)]


