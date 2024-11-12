import yaml
import pulumi
import pulumi_openstack as pstack
from plugin.network_manager import *
from plugin.os_conn import connection

# ######################### BLOCCO CARICAMENTO CONFIGURAZIONI
# Carica la configurazione e le variabili di ambiente
config = pulumi.Config()
config_values = pulumi.runtime.get_config_env()




# ######################### BLOCCO di importazione delle variabili statiche
# Connessione OpenStack
username=config_values.get("openstack:userName")
password=config_values.get("openstack:password")
tenant=config_values.get("openstack:tenantName")
auth_url=config_values.get("openstack:auth_url")

# Carica le risorse dal file YAML e ottieni le proprietà dell'istanza
with open('Pulumi.resources.yaml', 'r') as yaml_file:
    resources = yaml.safe_load(yaml_file).get('resources', {})
instance_props = resources.get('instance', {})

tenant_name = config_values.get("openstack:tenantName", "")
zone_name = f"{tenant_name}."
zone = pstack.dns.get_dns_zone(name=zone_name)

router_name = f"router_to_external.{tenant_name}"




# ######################### BLOCCO USO / CREAZIONE RETE
vlan_tag = int(config.get("vlan_tag", 1))

# Estrai il valore di vlans dalla configurazione
vlans_list = config.get_object("vlans")

vlans = [f"VLAN_ID: {vlan['id']} - Subnet: {vlan['subnet']}" for vlan in vlans_list] if vlans_list else ["No VLANs configured"]
#network_exist = config_values.get("network_exist", "False")
router_exist = config.get_bool("router_exist")

#network = pstack.networking.get_network(name=config.require("network_name"))
network_name = config.require("network_name")




# ################ CREAZIONE RETE DI PROGETTO
conn = connection(auth_url, username, password, tenant)
# Default VLAN CIDR
vlan_cidr = "10.0.0.0/24"

if vlan_tag and vlans_list:
    # Cerca vlan_cidr corrispondente al vlan_tag
    vlan_cidr = next((vlan["subnet"] for vlan in vlans_list if vlan["id"] == vlan_tag), vlan_cidr)

existing_network = conn.network.find_network(network_name)

if not existing_network:
    network = create_network(network_name, tenant_name, vlan_tag, zone_name)
else:
    network = pstack.networking.Network.get(network_name, existing_network.id)


def get_or_create_subnet(network_id):
    subnets = conn.network.subnets(network_id=network_id)
    vlan_subnet = next((sn for sn in subnets if sn.cidr == vlan_cidr), None)

    if not vlan_subnet:
        return create_subnet(router_exist, network_name, network_id, vlan_tag, tenant_name, vlan_cidr)
    else:
        existing_subnet = conn.network.find_subnet(vlan_subnet.id)
        return pstack.networking.Subnet.get(existing_subnet.name, existing_subnet.id)

#if isinstance(network.id, pulumi.Output):
subnet = network.id.apply(lambda id: get_or_create_subnet(id))
#else:
#    subnet = get_or_create_subnet(existing_network.id)


network_ext = pstack.networking.get_network(name=config.require("external_net"))





# ######################### BLOCCO STAMPA VARIABILI 
# Calcola la larghezza massima delle chiavi per una formattazione uniforme
max_key_length = max(len(key) for key in config_values.keys())

# Stampa le intestazioni di colonna
print(f"{'Key'.ljust(max_key_length)} : Value")
print("-" * (max_key_length + 10))  # linea di separazione

# Stampa le chiavi e i valori tabulati
for key, value in config_values.items():
    print(f"{key.ljust(max_key_length)} : {value}")

# Stampa l'intestazione
print("  ")
print("-" * 25)
print(f"{'VLAN ID'.ljust(10)} : Subnet")
print("-" * 25)

# Stampa ogni VLAN con ID e Subnet allineati
for vlan in vlans_list:
    vlan_id = str(vlan.get("id", "N/A"))
    subnets = vlan.get("subnet", "N/A")
    print(f"{vlan_id.ljust(10)} : {subnets}")




## APPUNTI
#
#auth_details = {
#    "username": config_values.get("openstack:userName"),
#    "password": config_values.get("openstack:password"),
#    "tenant": tenant_name,
#    "auth_url": config_values.get("openstack:auth_url")
#}

