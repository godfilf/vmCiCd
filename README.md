> NOTA: Ho messo in gitignore :
.pulumi/backups/
.pulumi/history/

1. scaricare Pulumi :
```
root@kollaJump:~# curl -sSL https://get.pulumi.com | sh
=== Installing Pulumi 3.140.0 ===
+ Downloading https://github.com/pulumi/pulumi/releases/download/v3.140.0/pulumi-v3.140.0-linux-x64.tar.gz...
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
  0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0
100  131M  100  131M    0     0  10.6M      0  0:00:12  0:00:12 --:--:-- 11.1M
+ Extracting to /root/.pulumi/bin

=== Pulumi is now installed! 🍹 ===
+ Get started with Pulumi: https://www.pulumi.com/docs/quickstart
```
2. scaricare l'app da git
3. Fare il login locale nella app:
```
root@kollaJump:~/vmCiCd# pulumi login file://.
Logged in to kollaJump as root (file://.)
root@kollaJump:~/vmCiCd# 
```

4. se sono state salvate già delle operazioni, e pushate su git, allora l'app mostra gli aggiornamenti degli stati.
   Altrimenti è necessario effettuare la creazione degli stack "nuovi"

5. Creazione di nuovi stack :
   Voglio creare uno stack di nome `dev`, che userò come ambiente di dev
```
root@kollaJump:~/vmCiCd# ls -l
total 24
-rw-r--r-- 1 root root 4342 Nov 20 10:26 __main__.py
drwxr-xr-x 2 root root 4096 Nov 20 11:55 plugin
-rw-r--r-- 1 root root 3172 Nov 20 11:49 README.md
-rw-r--r-- 1 root root  131 Nov 20 10:26 requirements.txt
drwxr-xr-x 2 root root 4096 Nov 20 11:56 sample_files
root@kollaJump:~/vmCiCd# cp sample_files/Pulumi.yaml.sample Pulumi.yaml
root@kollaJump:~/vmCiCd# cp sample_files/Pulumi.stack.yaml.sample Pulumi.dev.yaml
root@kollaJump:~/vmCiCd# cp sample_files/Pulumi.stack.resources.yaml.sample Pulumi.dev.resources.yaml
root@kollaJump:~/vmCiCd# ls -l
total 36
-rw-r--r-- 1 root root 4342 Nov 20 10:26 __main__.py
drwxr-xr-x 2 root root 4096 Nov 20 11:55 plugin
-rw-r--r-- 1 root root 2167 Nov 20 12:35 Pulumi.dev.resources.yaml
-rw-r--r-- 1 root root 1285 Nov 20 12:34 Pulumi.dev.yaml
-rw-r--r-- 1 root root 1399 Nov 20 12:34 Pulumi.yaml
-rw-r--r-- 1 root root 3840 Nov 20 12:37 README.md
-rw-r--r-- 1 root root  131 Nov 20 10:26 requirements.txt
drwxr-xr-x 2 root root 4096 Nov 20 11:56 sample_files
```
   a questo punto ho due vie. O creo preventivamente lo stack di nome dev, o lo creo in fase di up.
   Io lo ho fatto creare in fase di UP:

```
root@kollaJump:~/vmCiCd# PULUMI_CONFIG_PASSPHRASE="" pulumi up
Please choose a stack, or create a new one: <create a new stack>
Please enter your desired stack name: dev 
Created stack 'dev'
Previewing update (dev):
     Type                              Name                                                    Plan       Info
 +   pulumi:pulumi:Stack               NewApp-dev                                              create     22 messages
 +   ├─ openstack:compute:ServerGroup  db_pulumi_dev.test.cluster-dev.ostack.cosmicnet         create     
 +   ├─ openstack:networking:Network   network_vlan_101.test.cluster-dev.ostack.cosmicnet      create     
 +   ├─ openstack:networking:Port      db_pulumi-port-0-dev.test.cluster-dev.ostack.cosmicnet  create     
 +   └─ openstack:compute:Instance     db_pulumi-0_dev                                         create     

Diagnostics:
  pulumi:pulumi:Stack (NewApp-dev):
    Key                  : Value
    ------------------------------
    NewApp:external_net  : external.cluster-dev.ostack.cosmicnet
    NewApp:network_name  : network
    NewApp:router_exist  : true
    NewApp:vlan_tag      : 101
    NewApp:vlans         : [{"id":1,"subnet":"10.0.0.0/24"},{"id":100,"subnet":"10.1.0.0/24"},{"id":101,"subnet":"10.2.0.0/24"},{"id":102,"subnet":"10.3.0.0/24"},{"id":103,"subnet":"10.4.0.0/24"},{"id":104,"subnet":"10.5.0.0/24"}]
    openstack:auth_url   : http://10.10.10.99:5000
    openstack:password   : p1pp0123
    openstack:region     : RegionOne
    openstack:tenantName : test.cluster-dev.ostack.cosmicnet
    openstack:userName   : test.cluster-dev.ostack.cosmicnet
    pulumi:tags          : {"pulumi:template":"python"}
    -------------------------
    VLAN ID    : Subnet
    -------------------------
    1          : 10.0.0.0/24
    100        : 10.1.0.0/24
    101        : 10.2.0.0/24
    102        : 10.3.0.0/24
    103        : 10.4.0.0/24
    104        : 10.5.0.0/24

Resources:
    + 5 to create

Do you want to perform this update? yes
Updating (dev):
     Type                              Name                                                                Status              Info
 +   pulumi:pulumi:Stack               NewApp-dev                                                          created (165s)      22 messages
 +   ├─ openstack:compute:ServerGroup  db_pulumi_dev.test.cluster-dev.ostack.cosmicnet                     created (0.44s)     
 +   ├─ openstack:networking:Network   network_vlan_101.test.cluster-dev.ostack.cosmicnet                  created (5s)        
 +   ├─ openstack:networking:Subnet    subnet_vlan_101.network_vlan_101.test.cluster-dev.ostack.cosmicnet  created (8s)        
 +   ├─ openstack:networking:Port      db_pulumi-port-0-dev.test.cluster-dev.ostack.cosmicnet              created (7s)        
 +   └─ openstack:compute:Instance     db_pulumi-0_dev                                                     created (139s)      

Diagnostics:
  pulumi:pulumi:Stack (NewApp-dev):
    Key                  : Value
    ------------------------------
    NewApp:external_net  : external.cluster-dev.ostack.cosmicnet
    NewApp:network_name  : network
    NewApp:router_exist  : true
    NewApp:vlan_tag      : 101
    NewApp:vlans         : [{"id":1,"subnet":"10.0.0.0/24"},{"id":100,"subnet":"10.1.0.0/24"},{"id":101,"subnet":"10.2.0.0/24"},{"id":102,"subnet":"10.3.0.0/24"},{"id":103,"subnet":"10.4.0.0/24"},{"id":104,"subnet":"10.5.0.0/24"}]
    openstack:auth_url   : http://10.10.10.99:5000
    openstack:password   : p1pp0123
    openstack:region     : RegionOne
    openstack:tenantName : test.cluster-dev.ostack.cosmicnet
    openstack:userName   : test.cluster-dev.ostack.cosmicnet
    pulumi:tags          : {"pulumi:template":"python"}
    -------------------------
    VLAN ID    : Subnet
    -------------------------
    1          : 10.0.0.0/24
    100        : 10.1.0.0/24
    101        : 10.2.0.0/24
    102        : 10.3.0.0/24
    103        : 10.4.0.0/24
    104        : 10.5.0.0/24

Resources:
    + 6 created

Duration: 2m46s

root@kollaJump:~/vmCiCd# 
```

6. A questo punto creo un altro stack. Così ho diversi progetti deployati nello stesso tenant di openstack.
   non avendo creato manualmente lo stack , non è stato settato come default, dunque utilizzo la medesima procedura per la creazione del nuovo progetto.
   L'unico file che non copierò è `Pulumi.yaml` che è uguale per tuti i progetti:

```
root@kollaJump:~/vmCiCd# cp sample_files/Pulumi.stack.yaml.sample Pulumi.stg.yaml 
root@kollaJump:~/vmCiCd# cp sample_files/Pulumi.stack.resources.yaml.sample Pulumi.stg.resources.yaml 
root@kollaJump:~/vmCiCd# ls -l
total 60
-rw-r--r-- 1 root root 4342 Nov 20 10:26 __main__.py
drwxr-xr-x 3 root root 4096 Nov 20 12:40 plugin
-rw-r--r-- 1 root root 2167 Nov 20 12:35 Pulumi.dev.resources.yaml
-rw-r--r-- 1 root root 1285 Nov 20 12:42 Pulumi.dev.yaml
-rw-r--r-- 1 root root 2167 Nov 20 13:09 Pulumi.stg.resources.yaml
-rw-r--r-- 1 root root 1285 Nov 20 13:09 Pulumi.stg.yaml
-rw-r--r-- 1 root root 1399 Nov 20 12:34 Pulumi.yaml
drwxr-xr-x 2 root root 4096 Nov 20 12:40 __pycache__
-rw-r--r-- 1 root root 8831 Nov 20 13:07 README.md
-rw-r--r-- 1 root root  131 Nov 20 10:26 requirements.txt
drwxr-xr-x 2 root root 4096 Nov 20 11:56 sample_files
drwxr-xr-x 5 root root 4096 Nov 20 12:44 venv
(venv) root@kollaJump:~/IaC_tools/PulumiApp/NewApp_2/vmCiCd# PULUMI_CONFIG_PASSPHRASE="" pulumi up
Please choose a stack, or create a new one: <create a new stack>
Please enter your desired stack name: stg 
Created stack 'stg'
Previewing update (stg):
     Type                                     Name                                                                    Plan       Info
 +   pulumi:pulumi:Stack                      NewApp-stg                                                              create     23 messages
 +   ├─ openstack:networking:Network          network_vlan_100.test.cluster-dev.ostack.cosmicnet                      create     
 +   ├─ openstack:networking:Router           router_to_external_vlan_100.test.cluster-dev.ostack.cosmicnet           create     
 +   ├─ openstack:compute:ServerGroup         web_stg.test.cluster-dev.ostack.cosmicnet                               create     
 +   ├─ openstack:networking:Port             web-port-0-stg.test.cluster-dev.ostack.cosmicnet                        create     
 +   ├─ openstack:networking:Port             gateway_to_external.network_vlan_100.test.cluster-dev.ostack.cosmicnet  create     
 +   ├─ openstack:networking:RouterInterface  router-interface                                                        create     
 +   └─ openstack:compute:Instance            web-0_stg                                                               create     

Diagnostics:
  pulumi:pulumi:Stack (NewApp-stg):
    Key                  : Value
    ------------------------------
    NewApp:external_net  : external.cluster-dev.ostack.cosmicnet
    NewApp:network_name  : network
    NewApp:router_exist  : false
    NewApp:vlan_tag      : 100
    NewApp:vlans         : [{"id":1,"subnet":"10.0.0.0/24"},{"id":100,"subnet":"10.1.0.0/24"},{"id":101,"subnet":"10.2.0.0/24"},{"id":102,"subnet":"10.3.0.0/24"},{"id":103,"subnet":"10.4.0.0/24"},{"id":104,"subnet":"10.5.0.0/24"}]
    openstack:auth_url   : http://10.10.10.99:5000
    openstack:password   : p1pp0123
    openstack:region     : RegionOne
    openstack:tenantName : test.cluster-dev.ostack.cosmicnet
    openstack:userName   : test.cluster-dev.ostack.cosmicnet
    pulumi:tags          : {"pulumi:template":"python"}
    -------------------------
    VLAN ID    : Subnet
    -------------------------
    1          : 10.0.0.0/24
    100        : 10.1.0.0/24
    101        : 10.2.0.0/24
    102        : 10.3.0.0/24
    103        : 10.4.0.0/24
    104        : 10.5.0.0/24
    Impostato utilizzo di un Virtual Router : router_exist = False

Resources:
    + 8 to create

Do you want to perform this update? yes
Updating (stg):
     Type                                     Name                                                                    Status              Info
 +   pulumi:pulumi:Stack                      NewApp-stg                                                              created (67s)       23 messages
 +   ├─ openstack:networking:Network          network_vlan_100.test.cluster-dev.ostack.cosmicnet                      created (6s)        
 +   ├─ openstack:networking:Router           router_to_external_vlan_100.test.cluster-dev.ostack.cosmicnet           created (10s)       
 +   ├─ openstack:compute:ServerGroup         web_stg.test.cluster-dev.ostack.cosmicnet                               created (0.27s)     
 +   ├─ openstack:networking:Subnet           subnet_vlan_100.network_vlan_100.test.cluster-dev.ostack.cosmicnet      created (6s)        
 +   ├─ openstack:networking:Port             gateway_to_external.network_vlan_100.test.cluster-dev.ostack.cosmicnet  created (9s)        
 +   ├─ openstack:networking:Port             web-port-0-stg.test.cluster-dev.ostack.cosmicnet                        created (7s)        
 +   ├─ openstack:compute:Instance            web-0_stg                                                               created (43s)       
 +   └─ openstack:networking:RouterInterface  router-interface                                                        created (16s)       

Diagnostics:
  pulumi:pulumi:Stack (NewApp-stg):
    Key                  : Value
    ------------------------------
    NewApp:external_net  : external.cluster-dev.ostack.cosmicnet
    NewApp:network_name  : network
    NewApp:router_exist  : false
    NewApp:vlan_tag      : 100
    NewApp:vlans         : [{"id":1,"subnet":"10.0.0.0/24"},{"id":100,"subnet":"10.1.0.0/24"},{"id":101,"subnet":"10.2.0.0/24"},{"id":102,"subnet":"10.3.0.0/24"},{"id":103,"subnet":"10.4.0.0/24"},{"id":104,"subnet":"10.5.0.0/24"}]
    openstack:auth_url   : http://10.10.10.99:5000
    openstack:password   : p1pp0123
    openstack:region     : RegionOne
    openstack:tenantName : test.cluster-dev.ostack.cosmicnet
    openstack:userName   : test.cluster-dev.ostack.cosmicnet
    pulumi:tags          : {"pulumi:template":"python"}
    -------------------------
    VLAN ID    : Subnet
    -------------------------
    1          : 10.0.0.0/24
    100        : 10.1.0.0/24
    101        : 10.2.0.0/24
    102        : 10.3.0.0/24
    103        : 10.4.0.0/24
    104        : 10.5.0.0/24
    Impostato utilizzo di un Virtual Router : router_exist = False

Resources:
    + 9 created

Duration: 1m12s


```



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

