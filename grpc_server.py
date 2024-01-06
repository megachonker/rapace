import grpc
from concurrent import futures
import api_pb2
import api_pb2_grpc

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
        switchs[request.object_id].reset()
        return api_pb2.ResetResponse(message=True)

    @grpc_error_handler
    def GetStat(self, request, context):
        return api_pb2.StatResponse(stat_info=str(switchs[request.object_id].stat()))

    @grpc_error_handler
    def AddFirewallRule(self, request, context):
        # Implement logic to add a rule to the firewall
        return api_pb2.AddFirewallRuleResponse(message=True)


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
