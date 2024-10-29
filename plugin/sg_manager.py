import pulumi_openstack as pstack

def cd(conn, vmCount, instanceName, tenantName):  # cd sta per create delete, ovvero esegue tutte e due le funzioni
    sg = create(vmCount, instanceName, tenantName)
    delete(conn, vmCount, instanceName, tenantName)
    return sg

def create(vmCount, instanceName, tenantName):
    ## Creo il server group 
    if vmCount > 0:
        server_group = pstack.compute.ServerGroup(f"{instanceName}.{tenantName}",
            name=f"{instanceName}.{tenantName}",
            policies="anti-affinity",
            rules={
                "max_server_per_host": 2,
            }
        )
        return server_group
    else:
        return None

def delete(conn, vmCount, instanceName, tenantName):
    server_group_to_remove = conn.compute.find_server_group(f"{instanceName}.{tenantName}")
    if server_group_to_remove is not None and vmCount == 0:
        conn.compute.delete_server_group(server_group_to_remove.id)
