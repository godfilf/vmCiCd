from plugin.globals import *
import pulumi

def pre_destroy_check():
    pulumi.log.info("Eseguo il pre-hook prima del destroy.")
    # Logica personalizzata: controlla lo stato delle risorse
    attached_ports = get_router_ports()  # Simulazione: ottieni porte connesse al router
    if attached_ports:
        pulumi.log.warn(f"Il router ha {len(attached_ports)} porte connesse. Blocca o gestisci queste porte.")
        # Ad esempio, proteggi il router
        apply_protection_to_router()

def apply_protection_to_router():
    pulumi.log.info("Protezione del router applicata.")
    # Applica opzioni di protezione al router o ad altre risorse
    router = pulumi.output(get_router())
    router_opts = pulumi.ResourceOptions(protect=True)
    return router_opts

def protect_router(args, opts=None):
    if opts is None:
        opts = pulumi.ResourceOptions()

    if args.resource.__class__.__name__ == "Router" :
        router = import_existing_router(router_name, existing_router, external_network_id)
        existing_subnets = {subnet.id for subnet in conn.network.subnets()}
        router_ports = list(conn.network.ports(device_id=existing_router.id))
        subnet_count = 0 
        for port in router_ports:
           for fixed_ip in port.fixed_ips:
               if fixed_ip["subnet_id"] in existing_subnets:
                   subnet_count += 1
                   break  # Evita di contare più volte la stessa porta
                
        print(f"Numero di porte con subnet esistente: {subnet_count}")
            
        if subnet_count > 0:
            opts.protect = True
    return pulumi.ResourceTransformationResult(args.props, opts)

