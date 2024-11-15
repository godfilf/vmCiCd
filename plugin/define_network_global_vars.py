from plugin.globals import *
from plugin.network_manager import *
from plugin.port_manager import create_port_with_fixed_ip, import_port_with_fixed_ip
from plugin.router_manager import *
import pulumi
import pulumi.runtime

# ################ CREAZIONE RETE DI PROGETTO

if router_exist:
    ports = conn.network.ports()
    port_to_delete = next((port for port in ports if port.name == router_port_name), None)

    if port_to_delete:
        router = conn.network.remove_interface_from_router(existing_router, subnet_id=port_to_delete.fixed_ips[0]["subnet_id"], port_id=port_to_delete.id)
        conn.network.delete_port(port_to_delete)

    if existing_router:
        conn.network.delete_router(existing_router)


network = create_network(network_name, tenant_name, vlan_tag, zone_name)
subnet = network.id.apply(lambda id: create_subnet(router_exist, network_name, id, vlan_tag, tenant_name, vlan_cidr))

if not router_exist and (network_ext is not None or not network_ext):
    print(f"Impostato utilizzo di un Virtual Router : router_exist = {router_exist}")
    if not existing_router:
        router_port = create_port_with_fixed_ip(auth_url, username, password, tenant, router_port_name, network, subnet)
        router = create_router(router_name, external_network_id)
    else:
        router_port = import_port_with_fixed_ip(network, subnet)

    if existing_router:
        router = import_existing_router(router_name, existing_router, external_network_id)

    router_interface = attach_router_to_port(router, router_port)



   

