import sys
import grpc
import api_pb2
import api_pb2_grpc

def run():
    if len(sys.argv) < 3:
        print("Usage: sudo python client.py <action> <node> [additional_args]")
        return

    action = sys.argv[1]
    node = sys.argv[2]

    try:
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = api_pb2_grpc.MyServiceStub(channel)

            if action == "stat":
                response = stub.GetStat(api_pb2.Node(node=node))
                print("Stat response:", response.stat_info)
            elif action == "reset":
                response = stub.Reset(api_pb2.Node(node=node))
                print("Reset response:", response.message)
            elif action == "fw":
                response = stub.AddFirewallRule(api_pb2.AddFirewallRuleRequest(node=node,source_ip="10.0.0.6",dest_ip="10.0.0.5",protocol="ICMP",source_port=0,dest_port=0))
                print("add fw rull response:", response.message)
            elif action == "rate":
                rate = sys.argv[3]
                response = stub.Change_rate(api_pb2.RateRequest(node=node,rate=float(rate)))
                print("rate rull response:", response.result)
            # Add more cases for other actions as needed.
            else:
                print(f"Unknown action: {action}")
    except grpc.RpcError as e:
        print(f"An error occurred: {e.details()}")

if __name__ == "__main__":
    run()
