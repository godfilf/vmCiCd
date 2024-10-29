import pulumi
import pulumi_openstack as pstack
import yaml

# Caricare la configurazione specifica dello stack
config = pulumi.Config()

# Recupera tutte le configurazioni per lo stack corrente
config_values = pulumi.runtime.get_config_env()

# Stampa tutte le chiavi e i valori di configurazione
for key, value in config_values.items():
    print(f"Key: {key}, Value: {value}")

# Carica le risorse dal file YAML
with open('Pulumi.resources.yaml', 'r') as yaml_file:
    yaml_content = yaml.safe_load(yaml_file)

# Estrai le informazioni sulle risorse dal file YAML
resources = yaml_content.get('resources', {})

instance_props = resources['instance']

# Recupera l'ID della rete esistente
networkName = config.require("network_name")
network = pstack.networking.get_network(name=networkName)


tenantName = config_values.get("openstack:tenantName")
zoneName = f"{tenantName}."
zone = pstack.dns.get_dns_zone(name=zoneName)
pulumi.export(zoneName, zone.name)
    
username=config_values.get("openstack:userName")
password=config_values.get("openstack:password")
tenant=config_values.get("openstack:tenantName")
auth_url=config_values.get("openstack:auth_url")

