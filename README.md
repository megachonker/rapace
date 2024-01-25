# Rapce projet 

Rapace projet is a simulation of a network, with configurable equipement like router, firewall. This network is based on mininet (https://github.com/nsg-ethz/mini_internet_project).  

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Installation

To get the depot, you can download it from git 
```bash
# Example installation commands
git clone https://github.com/yourusername/yourproject.git
```

Before starting, you need to install and compile some elements. Ensure you have Rust, Python 3.7, the gRPC API, and other dependencies installed. To simplify this process, run the `install_dep.bash` script with sudo permission.

## Basic Launch

To launch a simple network, follow these steps:

1. Load the physical topology with:

    ```bash
    sudo python network.py
    ```

2. Launch the logical topology with:

    ```bash
    python grpc_server.py topo_conf/conf_subject.yaml
    ```

    At this point, the network is launched, and you can manage it using the API. To interact with it you can use the Rust client. Build and run it with:

    ```bash
    cd client/
    cargo build
    cargo run
    ```

    Inside the client, you'll find the help command.






