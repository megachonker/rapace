#!/bin/bash

#If argument are specifyed bypass installation
if [ -z "$1" ]
  then
    apt update
    apt install python3.7-venv virtualenv graphviz geeqie -y

    #installation of rust toolchain
    runuser -u p4 "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"

    #we whant to run on specific 3.7
    virtualenv venv --python=python3.7
    
    #enable virt env
    source venv/bin/activate

    #install grpc tool on the virt env
    python -m pip install grpcio
    python -m pip install grpcio-tools
fi

#link the proto to the rs project
#normaly use ln but it not work everywere
#wee need to copy the proto file to the rust folder
cp api.proto client/protofile/

#activate the env
source venv/bin/activate

#build the grpc definition
python -m grpc_tools.protoc -I . --python_out=.  --grpc_python_out=. api.proto

#overide grpc definition for service
protoc --python_out=. api.proto 

echo "python protobuf compiled"