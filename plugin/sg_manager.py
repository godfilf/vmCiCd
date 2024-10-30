import pulumi_openstack as pstack

def cd(conn, vmCount, instanceName, tenantName):
    """Crea o elimina il server group in base al valore di vmCount."""
    server_group_name = f"{instanceName}.{tenantName}"
    
    # Crea o elimina il server group in base al valore di vmCount
    if vmCount > 0:
        return create(server_group_name)
    delete(conn, server_group_name)
    return None

def create(server_group_name):
    """Crea un ServerGroup con politiche di anti-affinity."""
    return pstack.compute.ServerGroup(
        resource_name=server_group_name,
        name=server_group_name,
        policies="anti-affinity",
        rules={"max_server_per_host": 2}
    )

def delete(conn, server_group_name):
    """Elimina un ServerGroup specificato se esiste."""
    server_group = conn.compute.find_server_group(server_group_name)
    if server_group:
        conn.compute.delete_server_group(server_group.id)

