import openstack as os_sdk

# Funzione per stabilire la connessione a OpenStack
def create_connection(auth_url, username, password, tenant):
    return os_sdk.connection.Connection(
        auth={
            'auth_url': auth_url,
            'username': username,
            'password': password,
            'project_name': tenant,
            'user_domain_name': 'Default',
            'project_domain_name': 'Default',
        },
        compute_api_version='2',
        identity_interface='internal',
    )

# Funzione per ottenere i recordset esistenti
def get_existing_recordsets(conn, zone_id):
    return list(conn.dns.recordsets(zone=zone_id))

# Funzione per cancellare i recordset esistenti
def delete_recordsets(conn, recordsets_to_delete):
    for recordset in recordsets_to_delete:
        conn.dns.delete_recordset(recordset)

# Funzione per gestire i recordset
def manage_recordsets(conn, zone_id, instance_props):
    existing_recordsets = get_existing_recordsets(conn, zone_id)

    for vmType in instance_props.keys():
        recordCount = 0
        recIdToRemove = []
        vmCount = instance_props[vmType].get("vmCount")
        instanceName = instance_props[vmType].get("name")

        for recordset in existing_recordsets:
            if instanceName in recordset.name:
                recordCount += 1

        for i in range(1, recordCount + 1):
            if i >= vmCount:
                for recLst in existing_recordsets:
                    if f"{instanceName}-{i}" in recLst.name:
                        delete_recordsets(conn, [recLst])  # Passa la connessione e il recordset da eliminare

