import grpc
from concurrent import futures
import api_pb2
import api_pb2_grpc
from switch_classes.firewall import Flow

from MegaController import MegaController


# choose if we want to lunch a specific topology
import sys 
if len(sys.argv) >1:
    mega_controller = MegaController(conf_path=sys.argv[1])
else:
    mega_controller = MegaController()

import functools
import logging

# used to have more cleaner log
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

# main grpc definition
# each definition are a function defined in the proto file
class MyService(api_pb2_grpc.MyServiceServicer):
    @grpc_error_handler
    def Reset(self, request, context):
        # we select the specific node from the mega controler
        mega_controller.switchs[request.node].reset()
        return api_pb2.ResetResponse(message=True)

    @grpc_error_handler
    def GetStat(self, request, context):
        stat = mega_controller.switchs[request.node].stat()
        if len(stat) > 1:
            res = f"Packet received {stat[0]}\n{stat[1]}"
        else:
            res = f"Packet received {stat[0]}"
        return api_pb2.StatResponse(stat_info=res)

    @grpc_error_handler
    def AddFirewallRule(self, request, context):
        #association table used to translate from str to hex
        translate = {
            'TCP':6,
            'UDP':17,
            'ICMP':1,
        }
        rule = Flow(request.source_ip, request.dest_ip,  translate.get(request.protocol), request.source_port, request.dest_port)
        print(f"try append firewall rule at {rule}")
        mega_controller.switchs[request.node].add_drop_rule(rule)
        return api_pb2.AddFirewallRuleResponse(message=True)
    
    @grpc_error_handler
    def Change_rate(self, request, context):
        return api_pb2.ChangeRateResponse(result=str(mega_controller.switchs[request.node].set_rates_lb(request.rate)))
   
    @grpc_error_handler
    def set_encap(self, request, context):
        return api_pb2.SetEncapResponce(answer=str(mega_controller.switchs[request.node].add_encap(request.ip_address,request.nodedst)))

    @grpc_error_handler
    def set_encap_link(self, request, context):
        return api_pb2.SetEncapResponce(answer=str(mega_controller.switchs[request.node].add_encap_link(request.ip_address,request.nodedstA,request.nodedstB)))
        
    @grpc_error_handler
    def show_topo(self, request, context):
        return api_pb2.Json(mon_json=str(mega_controller.save_topo()))

    @grpc_error_handler
    def add_link(self, request, context):
        rep=mega_controller.add_link(request.nodeA,request.nodeB)
        return api_pb2.ChangeLinkResponce(status=f"add_link {request.nodeA} et {request.nodeB} => {rep}")
    
    @grpc_error_handler
    def remove_Link(self, request, context):
        rep=mega_controller.remove_link(request.nodeA,request.nodeB)
        return api_pb2.ChangeLinkResponce(status=f"rm_link {request.nodeA} et {request.nodeB} => {rep}")
    
    @grpc_error_handler
    def swap_controler(self, request, context):
        rep = str(mega_controller.swap(node=request.target.node,role=request.mode,connect=request.argument ))
        return api_pb2.SwapResponse(status=f"swap {rep}")

    @grpc_error_handler
    def change_weight(self, request, context):
        rep = str(mega_controller.change_weight(weight=request.weight,link=(request.lien.nodeA,request.lien.nodeB) ))
        return api_pb2.ChangeLinkResponce(status=f"change_weight {rep} {request.lien} et {request.weight}")
        
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    api_pb2_grpc.add_MyServiceServicer_to_server(MyService(), server)
    # normaly grpc can be used 
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Switches loaded. gRPC server listening on port 50051.")
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()
