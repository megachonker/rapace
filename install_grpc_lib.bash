if [ -z "$1" ]
  then
    apt update
    apt install python3.7-venv virtualenv cargo -y

    runuser p4 curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

    virtualenv venv --python=python3.7
    source venv/bin/activate
    python -m pip install grpcio
    python -m pip install grpcio-tools
fi
source venv/bin/activate
python -m grpc_tools.protoc -I . --python_out=.  --grpc_python_out=. api.proto
protoc --python_out=. api.proto 
echo "protobuf compiled"