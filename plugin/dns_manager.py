import openstack as os_sdk
import plugin.os_conn as os_conn

# Ottiene tutti i recordset in una zona
def get_recordsets(conn, zone_id):
    return list(conn.dns.recordsets(zone=zone_id))

# Cancella i recordset specificati
def delete_recordsets(conn, recordsets):
    for recordset in recordsets:
        conn.dns.delete_recordset(recordset)

# Gestisce i recordset per ogni tipo di VM
def manage_recordsets(conn, zone_id, instance_props):
    existing_recordsets = get_recordsets(conn, zone_id)

    for vmType, props in instance_props.items():
        vm_count = props.get("vmCount", 0)
        instance_name = props.get("name")

        # Filtra i recordset che corrispondono al nome dell'istanza
        matching_recordsets = [r for r in existing_recordsets if instance_name in r.name]

        # Trova i recordset in eccesso e cancellali
        excess_recordsets = [r for i, r in enumerate(matching_recordsets, start=1) if i > vm_count]
        delete_recordsets(conn, excess_recordsets)
