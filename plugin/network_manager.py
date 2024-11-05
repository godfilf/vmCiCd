import openstack as os_sdk
from plugin.os_conn import connection

def get_external_network_id(auth_url, username, password, tenant, external_network_name):
    conn = connection(auth_url, username, password, tenant)
    external_network = conn.network.find_network(external_network_name)
    if external_network is None:
        raise ValueError(f"Rete con nome '{external_network_name}' non trovata")
    return external_network.id

