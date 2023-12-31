# The goal of this script is just to connect 
#h0-s0-s1-h1 with simple repeater, and fill there tables with the topologie.



from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
from p4utils.utils.compiler import * 

# Load the topology in a networkx graph
topo = load_topo("topology.json")

# Get thrift_port to initiate connection with s1 switch
thrift_port_s0 = topo.get_thrift_port('s0')
thrift_port_s1 = topo.get_thrift_port('s1')
api_s0 = SimpleSwitchThriftAPI(thrift_port_s0)
api_s1 = SimpleSwitchThriftAPI(thrift_port_s1)



# Compile the P4 program
print("Compiling the repeater code ...")
source = P4C("P4src/repeater_with_table.p4", "/usr/local/bin/p4c")
source.compile()


print("Pushing to switchs")
api_s0.load_new_config_file("P4src/repeater_with_table.json")
api_s0.swap_configs()
api_s1.load_new_config_file("P4src/repeater_with_table.json")
api_s1.swap_configs()






print("Fill the table")

api_s0.table_set_default("repeater","drop",[])
api_s1.table_set_default("repeater","drop",[])



#find each port for s0 and s1

port_s0h0 = topo.node_to_node_port_num("s0","h0")
port_s0s1 = topo.node_to_node_port_num("s0","s1")

port_s1h1 = topo.node_to_node_port_num("s1","h1")
port_s1s0 = topo.node_to_node_port_num("s1","s0")

api_s0.table_add("repeater","forward",[str(port_s0h0)],[str(port_s0s1)])
api_s0.table_add("repeater","forward",[str(port_s0s1)],[str(port_s0h0)])



api_s1.table_add("repeater","forward",[str(port_s1s0)],[str(port_s1h1)])
api_s1.table_add("repeater","forward",[str(port_s1h1)],[str(port_s1s0)])


api_s0.switch_info.load_json_config(api_s0.client)
api_s0.table_entries_match_to_handle = api_s0.create_match_to_handle_dict()
api_s0.load_table_entries_match_to_handle()
api_s1.switch_info.load_json_config(api_s1.client)
api_s1.table_entries_match_to_handle = api_s1.create_match_to_handle_dict()
api_s1.load_table_entries_match_to_handle()