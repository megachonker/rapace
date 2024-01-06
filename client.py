import sys
import grpc
import api_pb2
import api_pb2_grpc

def run():
    if len(sys.argv) < 3:
        print("Usage: sudo python client.py <action> <object_id> [additional_args]")
        return

    action = sys.argv[1]
    object_id = sys.argv[2]

    channel = grpc.insecure_channel('localhost:50051')
    stub = api_pb2_grpc.MyServiceStub(channel)

    if action == "stat":
        response = stub.GetStat(api_pb2.StatRequest(object_id=object_id))
        print("Stat response:", response.stat_info)
    elif action == "reset":
        response = stub.Reset(api_pb2.ResetRequest(object_id=object_id))
        print("Reset response:", response.message)
    # Add more cases for other actions as needed.
    else:
        print(f"Unknown action: {action}")

if __name__ == "__main__":
    run()
