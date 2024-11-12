import pulumi
import pulumi_openstack as pstack
from plugin.globals import *
from plugin.define_network_global_vars import *
from plugin.port_manager import create_port_without_fixed_ip

# Funzione per creare un'istanza
def create_instance(instanceName, flavor, image, network, server_group, optional_args, i):
    instance_port = create_port_without_fixed_ip(f"{instanceName}-port-{i}.{tenant_name}", network.id, subnet.id)

    return pstack.compute.Instance(
        f"{instanceName}-{i}",
        name=f"{instanceName}-{i}",
        flavor_name=flavor,
        image_name=image,
        networks=[{'uuid': network.id, 'name': network.name, 'port': instance_port.id}],
        #networks=[{'uuid': network.id, 'name': network.name}],
        scheduler_hints=[{"group": server_group.id}],
        #opts=pulumi.ResourceOptions(depends_on=[server_group]),
        opts=pulumi.ResourceOptions(depends_on=[network, server_group, instance_port]),
        **optional_args
    )

