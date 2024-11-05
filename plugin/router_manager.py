import pulumi_openstack as pstack

def create_router(router_name, external_network_id):
    # Crea il router connesso alla rete esterna
    router = pstack.network.Router(
        resource_name=router_name,
        admin_state_up=True,  # Attiva il router
        external_network_id=external_network_id  # ID della rete esterna
    )
    return router

def attach_router_to_port(router, port_id):
    # Connetti il router alla porta specificata
    router_interface = pstack.network.RouterInterface(
        resource_name="router-interface",
        router_id=router.id,
        port_id=port_id  # Usa l'ID della porta creata in precedenza
    )
    return router_interface

