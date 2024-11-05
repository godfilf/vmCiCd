import pulumi
import pulumi_openstack as pstack
import yaml

# Carica la configurazione e le variabili di ambiente
config = pulumi.Config()
config_values = pulumi.runtime.get_config_env()

# Stampa tutte le configurazioni per verifica (può essere rimosso in produzione)
for key, value in config_values.items():
    print(f"Key: {key}, Value: {value}")

# Carica le risorse dal file YAML e ottieni le proprietà dell'istanza
with open('Pulumi.resources.yaml', 'r') as yaml_file:
    resources = yaml.safe_load(yaml_file).get('resources', {})
instance_props = resources.get('instance', {})

# Recupera l'ID della rete e della zona DNS
network = pstack.networking.get_network(name=config.require("network_name"))
network_ext = pstack.networking.get_network(name=config.require("external_net"))
tenant_name = config_values.get("openstack:tenantName", "")
zone_name = f"{tenant_name}."
zone = pstack.dns.get_dns_zone(name=zone_name)
router_name = f"router_to_external.{tenant_name}"

# Esporta il nome della zona
pulumi.export(zone_name, zone.name)

# Connessione OpenStack
username=config_values.get("openstack:userName")
password=config_values.get("openstack:password")
tenant=config_values.get("openstack:tenantName")
auth_url=config_values.get("openstack:auth_url")

#auth_details = {
#    "username": config_values.get("openstack:userName"),
#    "password": config_values.get("openstack:password"),
#    "tenant": tenant_name,
#    "auth_url": config_values.get("openstack:auth_url")
#}

