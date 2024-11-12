from plugin.globals import *
from plugin.network_manager import *


# ################ CREAZIONE RETE DI PROGETTO

#network, subnet = get_or_create_network()
network = create_network(network_name, tenant_name, vlan_tag, zone_name)
subnet = network.id.apply(lambda id: create_subnet(router_exist, network_name, id, vlan_tag, tenant_name, vlan_cidr))

network_ext = pstack.networking.get_network(name=config.require("external_net"))


