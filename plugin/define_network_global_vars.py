from plugin.globals import *
from plugin.network_manager import *
from plugin.port_manager import create_port_with_fixed_ip
from plugin.router_manager import attach_router_to_port


# ################ CREAZIONE RETE DI PROGETTO

#network, subnet = get_or_create_network()
network = create_network(network_name, tenant_name, vlan_tag, zone_name)
subnet = network.id.apply(lambda id: create_subnet(router_exist, network_name, id, vlan_tag, tenant_name, vlan_cidr))

if not router_exist and (network_ext is not None or not network_ext):
    print(f"Impostato il non utilizzo di un Virtual Router : router_exist = {router_exist}")
    if not existing_router:
        # 2. Crea una porta senza IP fisso
        router_port = create_port_with_fixed_ip(auth_url, username, password, tenant, f"gateway_to_external.{network_name}", network, subnet)
        # 4. Connetti il router alla porta
        router_interface = attach_router_to_port(router, router_port)
        pulumi.export("router_interface_id", router_interface)
        #await router_interface.id
    else:
        print(f"Router '{router_name}' esiste già con ID: {existing_router.id}")




