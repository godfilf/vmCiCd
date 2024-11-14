import pulumi
import pulumi_openstack as pstack

def create_router(router_name, external_network_id):
    # Crea il router connesso alla rete esterna
    router = pstack.networking.Router(
        resource_name=router_name,
        admin_state_up=True,                     # Attiva il router
        external_network_id=external_network_id  # ID della rete esterna
    )
    return router

def attach_router_to_port(router, port):
    # Connetti il router alla porta specificata
    router_interface = pstack.networking.RouterInterface(
        resource_name="router-interface",
        router_id=router.id,
        opts=pulumi.ResourceOptions(depends_on=[router, port]),
        port_id=port.id  # Usa l'ID della porta creata in precedenza
    )
    return router_interface

