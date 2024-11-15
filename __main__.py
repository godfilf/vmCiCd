"""A Python Pulumi program"""

import pulumi
import pulumi.runtime
import pulumi_openstack as pstack
import openstack as os_sdk
import sys

# importo tutte le var che ho creato, perchè il __main__.py era diventato illeggibile
from plugin.globals import *
from plugin.define_network_global_vars import *

# importo dei moduli custom per la gestione di alcuni componenti openstack, i quali non sono tracciati da pulumi 
import plugin.dns_manager as dns
import plugin.server_groups_manager as sg
import plugin.volumes_manager as vols

# importo le funzioni per il router

from plugin.instance_manager import create_instance

# Funzione per ottenere una proprietà configurata
def get_config_property(vmType, prop_name, default_value):
    try:
        return instance_props[vmType].get(prop_name) or config.require(prop_name)
    except pulumi.ConfigMissingError as e:
        if prop_name in {"keyPair", "volumes"}: return None
        print(f"Errore: La configurazione '{prop_name}' è mancante o errata per '{vmType}'. {e}")
        sys.exit(1)  # Termina il programma con un codice di uscita diverso da 0


# Connessione e configurazione
dns.manage_recordsets(conn, zone.id, instance_props)

#if not router_exist:
#if not router_exist and (network_ext is not None or not network_ext):
#    print(f"Impostato il non utilizzo di un Virtual Router : router_exist = {router_exist}")
#    if not existing_router:
#        print(f"Non esiste un router to external. Lo creo: router_to_external = {router_name}")
#        # 2. Crea una porta senza IP fisso
#        router_port = create_port_with_fixed_ip(auth_url, username, password, tenant, f"gateway_to_external.{network_name}", network, subnet)
#        # 4. Connetti il router alla porta
#        router_interface = attach_router_to_port(router, router_port)
#        pulumi.export("router_interface_id", router_interface)
#        #await router_interface.id
#    
#    else:
#        print(f"Router '{router_name}' esiste già con ID: {existing_router.id}")

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
    instances = [create_instance(instanceName, flavor, image, network, server_group, optional_args, i) for i in range(vmCount)]

    
    #pulumi.export("instances", instances)
    #pulumi.export("network", network)
    #pulumi.export("subnet", subnet)
    #pulumi.export("router", router)

