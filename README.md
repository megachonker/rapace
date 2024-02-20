# Rapce projet 

Rapace Project is a network simulation that features configurable equipment, including routers and firewalls. The simulation is built upon the [mininet](https://github.com/nsg-ethz/mini_internet_project) framework. This project utilizes the [P4](https://p4.org/p4-spec/docs/P4-16-v1.0.0-spec.html) language for the data-plane and leverages the [P4utils](https://github.com/nsg-ethz/p4-utils) Python libraries for the control-plane.

the idea is to make a controle plane that drive the dataplane, that allow a user to quickly reconfigure a SDN.

# Table of Contents

- [QuickStart](#QuickStart)
    - [Installation](#installation)
    - [Usage](#launch)
- [Features](#features)
    - [meta-controleur](#meta-controleur)
    - [controlers](#controlers)
    - [CLI](#cli)
- [Files in the Depot](#repostructure)



# QuickStart
## Installation

- To get the depot, you can download it from git be sure to have proper right for clone it.
- having a working P4 vm with Thrift patch enabled

```bash
git clone

#Before starting, you need to install and compile some elements. Ensure you have Rust, Python 3.7, the gRPC API, and other dependencies installed. 

#To simplify this process, run the script with sudo.
sudo bash grpc_build_install_dep.bash

#after that we are on same page
```



## Launch
To launch a simple network, follow these steps:

1. Load the physical topology with:

    ```bash
    sudo python network.py [number_of_node]
    ```
    you can lunch command inside it like `h1 ping h4`.

    if you have issue here maybe you need to check if you have the thrift patch working

    *the physical topology are verry strong if somthing wrong it is not from here it support manny server restart*

2. Launch the logical topology with:

    ```bash
    python grpc_server.py [topo_conf/conf_subject.yaml]
    ```

    At this point, the network is launched, and you can manage it using the API. 

3. connect the client
    #### To interact with it you can use the Rust client:
    - it made for being lunched outside the vm, for that specify the ip of your vm
    - if you run it on the vm you need too ensure that you have ssh forwarding activated with ssh -X *you need to log in and out one time (x forwarding bug)*
    - be sure having all dependancy installed and having the protofile on the right place(all is done thanks to the install script), you can watch the installation script if you want to do it manualy
    ```bash
    ip a|grep enp1|grep inet #to get your vm ip
    cd client/
    cargo run [VM IP]
    ```

    Inside the client, you'll find the help command.

3.  enjoy you have help, you can try show topo


# Features:
## meta-controleur
*Know all network, can launch controller on switchs*

- [x] network knowlege
- [x] lunch controler
- [x] add link
- [x] remove link
- [x] show topo
- [x] swap
- [x] status

## controlers
*The instantiation of a controller will therefore start with the opening of a Thrift connection, resetting the current states of the switch, and uploading the new compiled data-plane. compiled.*

- [x] router
- [x] load-balancer
- [x] firewall
- [x] repeter



### Firewall
- has 2 ports IN => OUT.
- add_fw_rule <flow>
- counts filtered and received packets

### Load balancer

- 1:N one entry many output
- outflux random (but respect the flow), use a hash function
- limite ``set_rate_lb <pkt/s> (voir choise)``
- counts received packets

### Router:
- segment routing ``add_encap_node <flow> <node or link>``
- counts received and encaplulated packets 

*flow => IP source, IP dst, protocole, port source, port destination*

## CLI
enable user to modulate the network
- [x] show topology
- [x] modify topology
- [x] interactive shell
- [x] remote access


# RepoStructure:
### Runable
- `grpc_server.py`: lunch server and lunch topo given on argument
- `grpc_build_install_dep.bash`: install dep and used to compile python grpc
- `network.py`: lunch with sudo build up the mininet physical network

### source code directory 
- `client/`: The Rust client for the gRPC API.
- `P4src/`: The data-plane P4 code for the equipment.
- `switch_classes/`: The control-plane logic for the equipment.
- `topo_conf/`: Various YAML configurations and their representations.
- `api.proto`: Main definition of the API grpc


### DebugFile
***port number** are same that port displayed by the **grpc client command show***
- `log/`: inside it you have log of all switch 
- `pcap/`: capture of all port of all switch
