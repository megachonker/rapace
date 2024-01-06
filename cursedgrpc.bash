if [ -z "$1" ]
  then
    virtualenv venv --python=python3.7
    source venv/bin/activate
    python -m pip install grpcio
    python -m pip install grpcio-tools
fi
source venv/bin/activate
python -m grpc_tools.protoc -I . --python_out=.  --grpc_python_out=. api.proto
protoc --python_out=. api.proto 
echo "protobuf compiled"