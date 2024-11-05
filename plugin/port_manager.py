import pulumi_openstack as pstack

def create_port_without_fixed_ip(port_name, network_id):
    # Crea una porta senza IP fisso (fixed_ip)
    return pstack.network.Port(
        resource_name=port_name,
        network_id=network_id,  # Specifica la rete a cui la porta si connette
        admin_state_up=True,  # Attiva la porta
        fixed_ips=[],  # Nessun IP fisso specificato
    )

