import grpc
from concurrent import futures
import api_pb2
import api_pb2_grpc
from switch_classes.firewall import Flow

import launch

switchs = launch.init_switch()

import functools
import logging

def grpc_error_handler(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            # Find the context in args
            context = next((arg for arg in args if isinstance(arg, grpc.ServicerContext)), None)
            if context is not None:
                logging.error(f"Error in {f.__name__}: {e}, Request: {args[0]}")
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Error in {f.__name__}: {e}")
            else:
                logging.error(f"Error in {f.__name__} but context not found: {e}")
            return None  # Or return a default instance of the expected response type
    return wrapper

class MyService(api_pb2_grpc.MyServiceServicer):
    @grpc_error_handler
    def Reset(self, request, context):
        switchs[request.node].reset()
        return api_pb2.ResetResponse(message=True)

    @grpc_error_handler
    def GetStat(self, request, context):
        return api_pb2.StatResponse(stat_info=str(switchs[request.node].stat()))

    @grpc_error_handler
    def AddFirewallRule(self, request, context):
        # print(f"fw debug {request}")
        #association table 
        translate = {
            'TCP':6,
            'UDP':17,
            'ICMP':1,
        }
        rule = Flow(request.source_ip, request.dest_ip,  translate.get(request.protocol), request.source_port, request.dest_port)
        print(f"try append firewall rule at {rule}")
        switchs[request.node].add_drop_rule(rule)
        return api_pb2.AddFirewallRuleResponse(message=True)
    
    @grpc_error_handler
    def Change_rate(self, request, context):
        return api_pb2.ChangeRateResponse(result=str(switchs[request.node].set_rates_lb(request.rate)))
   
    @grpc_error_handler
    def set_encap(self, request, context):
        print("non implémenter")
        return api_pb2.SetEncapResponce(stat_info=str(switchs[request.node].add_encap(request.ip_address,request.nodedst)))
    
    @grpc_error_handler
    def show_topo(self, request, context):
        return api_pb2.Json("non implémenter doit envoyer la topo en json degeux")

    @grpc_error_handler
    def add_link(self, request, context):
        return api_pb2.ChangeLinkResponce(f"add_link unimplementer {request.nodeA} et {request.nodeB}")
    
    @grpc_error_handler
    def remove_Link(self, request, context):
        return api_pb2.ChangeLinkResponce(f"rm_link unimplementer {request.nodeA} et {request.nodeB}")
    
    @grpc_error_handler
    def change_weight(self, request, context):
        return api_pb2.ChangeLinkResponce(f"changer poid unimplementer {request.lien} et {request.weight}")
    

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    api_pb2_grpc.add_MyServiceServicer_to_server(MyService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Switches loaded. gRPC server listening on port 50051.")
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()
