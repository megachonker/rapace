import grpc
from concurrent import futures
import api_pb2
import api_pb2_grpc

import launch

switchs = launch.init_switch()



class MyService(api_pb2_grpc.MyServiceServicer):

    def Reset(self, request, context):
        switchs[request.object_id].reset()
        return api_pb2.ResetResponse(message=True)

    def GetStat(self, request, context):
        return api_pb2.StatResponse(stat_info=str(switchs[request.object_id].stat()))

    def AddFirewallRule(self, request, context):
        print(f"{request}")
        # Implement logic to add a rule to the firewall
        return api_pb2.AddFirewallRuleResponse(message=True)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    api_pb2_grpc.add_MyServiceServicer_to_server(MyService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    print("switchs loaded")
    print("grpc server listening")
    serve()

