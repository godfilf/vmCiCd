Il file di default `Pulumi.yaml` non viene usato. rimane solo per il corretto funzionamento di pulumi.
Ho delegato tutto ai file `Pulumi.dev.yaml` e `Pulumi.resources.yaml`


Nel file `Pulumi.dev.yaml` ci sono solo le credenziali di accesso a openstack

```
# cat Pulumi.dev.yaml 
encryptionsalt: v1:yWF7+6W4oXc=:v1:rD2J54ADngD9djMB:AE7p6Nxhpcp+aMlGOlEPdr73COrx5w==
config:
  openstack:userName: test.cluster-dev.ostack.cosmicnet
  openstack:password: p1pp0123
  openstack:auth_url: http://10.10.10.99:5000
  openstack:tenantName: test.cluster-dev.ostack.cosmicnet
  openstack:region: RegionOne
  network_name: network.test.cluster-dev.ostack.cosmicnet
```

Nel file `Pulimi.resources.yaml` ci sono le risorse che voglio creare

```
resources:
  instance:
    db:                            # Indica il tipo di VM, e può essere un nome qualsiasi
      name: db_pulumi              # questo sarà il vero nome della VM. seguito da `-x` in cui x sarà un numero incrementale che parte da 0
      flavor: m1.tiny              # indica il flavor da usare
      image: debian                # indica l'immagine da usare
      vmCount: 0                   # indica il numero di vm da creare. se è a `0`, elimina tutte le vm in quel vmType
      keyPair: "kollaJump_ecdsa"   # indica quale chiave usare, se da usare
   
    web:
      name: web_pulumi
      flavor: m1.tiny
      image: debian
      vmCount: 0
      keyPair: "kollaJump_ecdsa"

    custom:
      name: custom
      flavor: m1.tiny
      image: debian
      vmCount: 0
      keyPair: "kollaJump_ecdsa"
```




################### appo code
# ID o nome dell'istanza
instance_id = "12345"  # Sostituisci con l'ID reale dell'istanza

# Funzione per riavviare l'istanza
def reboot_instance(ctx):
    server = conn.compute.find_server(instance_id)
    if server:
        conn.compute.reboot_server(server, reboot_type="SOFT")  # SOFT o HARD
    else:
        pulumi.log.error(f"Impossibile trovare l'istanza con ID {instance_id}")

# Esegui la funzione durante il ciclo Pulumi
pulumi.runtime.run_in_stack(reboot_instance)

