# Rapce projet 

Rapace Project is a network simulation that features configurable equipment, including routers and firewalls. The simulation is built upon the [mininet](https://github.com/nsg-ethz/mini_internet_project) framework. This project utilizes the [P4](https://p4.org/p4-spec/docs/P4-16-v1.0.0-spec.html) language for the data-plane and leverages the [P4utils](https://github.com/nsg-ethz/p4-utils) Python libraries for the control-plane.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Files in the Depot](#files-in-the-depot)

## Installation

To get the depot, you can download it from git 
```bash
# Example installation commands
git clone 
```

Before starting, you need to install and compile some elements. Ensure you have Rust, Python 3.7, the gRPC API, and other dependencies installed. To simplify this process, run the `sudo bash grpc_build_install_dep.bash` script with sudo permission.

## Basic Launch

To launch a simple network, follow these steps:

1. Load the physical topology with:

    ```bash
    sudo python network.py
    ```

2. Launch the logical topology with:

    ```bash
    python grpc_server.py [topo_conf/conf_subject.yaml]
    ```

    At this point, the network is launched, and you can manage it using the API. To interact with it you can use the Rust client. Build and run it with:

    ```bash
    cd client/
    cargo run
    ```

    Inside the client, you'll find the help command.

Inside the depot, you can find:

- `client/`: The Rust client for the gRPC API.
- `P4src/`: The data-plane code for the equipment.
- `switch_classes/`: The control-plane logic for the equipment.
- `scripts/`: Python scripts for testing the network.
- `topo_conf/`: Various YAML configurations and their representations.


  




