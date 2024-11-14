from plugin.globals import *
import pulumi_openstack as pstack
import plugin.os_conn as os_conn


def get_image_id(image_name):
    image = conn.compute.find_image(image_name)
    if image:
        return image.id
    else:
        #raise ValueError(f"Immagine '{image_name}' non trovata")
        return None


def volume_create(volumes, image_name=None):
    created_volumes = {}

    for i, (volume_key, volume_props) in enumerate(volumes.items()):
        if "uuid" in volume_props:
            created_volumes[volume_key] = {"id": volume_props["uuid"]}
        else:
            created_volumes[volume_key] = pstack.blockstorage.Volume(
                resource_name=volume_key,
                region="RegionOne",
                name=volume_key,
                description=volume_props["description"],
                size=volume_props["size"],
                volume_type=volume_props.get("type", None),  # Usa 'ceph' come tipo predefinito se non specificato
                image_id= get_image_id(image_name) #if i == 0 else None
            )
    return created_volumes

