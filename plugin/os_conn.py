import openstack as os_sdk

def connection(auth_url, username, password, tenant):
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
