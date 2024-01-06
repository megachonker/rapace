import sys
from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI

topo = load_topo('topology.json')
sw_name = "s5"
thrift_port = topo.get_thrift_port(sw_name)
controller = SimpleSwitchThriftAPI(thrift_port)
controller.counter_read('total_packet', 0)
controller.counter_read('filter_hit', 0)
