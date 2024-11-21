from plugin.globals import *
from plugin.network_manager import *
from plugin.port_manager import create_port_with_fixed_ip, import_port_with_fixed_ip
from plugin.router_manager import *
import pulumi
import pulumi.runtime

network_ext = pstack.networking.get_network(name=config.require("external_net"))
existing_network = conn.network.find_network(network_name, detailed=True)
external_network_id = get_network_id(auth_url, username, password, tenant, network_ext.name)

if router_exist:
    ports = conn.network.ports()
    port_to_delete = next((port for port in ports if port.name == router_port_name), None)

    if port_to_delete:
        port_to_delete_from_existing_router = conn.network.remove_interface_from_router(existing_router, subnet_id=port_to_delete.fixed_ips[0]["subnet_id"], port_id=port_to_delete.id)
        conn.network.delete_port(port_to_delete)

    if existing_router:
        router = import_existing_router(router_name, existing_router, external_network_id)



        existing_subnets = {subnet.id for subnet in conn.network.subnets()}
        print(f"Subnet esistenti nel progetto: {existing_subnets}")


        router_ports = list(conn.network.ports(device_id=existing_router.id))
        subnet_count = 0
        for port in router_ports:
            for fixed_ip in port.fixed_ips:
                if fixed_ip["subnet_id"] in existing_subnets:
                    subnet_count += 1
                    break  # Evita di contare più volte la stessa porta
        
        print(f"Numero di porte con subnet esistente: {subnet_count}")


        if subnet_count == 0:
            conn.network.delete_router(existing_router)


network = create_network(network_name, tenant_name, vlan_tag, zone_name)
subnet = network.id.apply(lambda id: create_subnet(router_exist, network_name, id, vlan_tag, tenant_name, vlan_cidr))


if not router_exist and (network_ext is not None or not network_ext):
    print(f"Impostato utilizzo di un Virtual Router : router_exist = {router_exist}")
    if not existing_router:
        router_port = create_port_with_fixed_ip(auth_url, username, password, tenant, router_port_name, network, subnet)
        router = create_router(router_name, external_network_id)
    else:
        router_port_exist = conn.network.find_port(router_port_name)
        router_port = import_port_with_fixed_ip(network, subnet) if router_port_exist else create_port_with_fixed_ip(auth_url, username, password, tenant, router_port_name, network, subnet)

    if existing_router:
        router = import_existing_router(router_name, existing_router, external_network_id)

    router_interface = attach_router_to_port(router, router_port)



   

