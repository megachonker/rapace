from p4utils.mininetlib.network_API import NetworkAPI

net = NetworkAPI()

def stop():
    """ Stop the network """
    print(net.net is None)
    
    net.net.stop()


def main(Cli=True,nb_switch=10):
    """ Start the physical network, it is a clique of 8 switchs with one host per switchs
        l2 strategy 
        Cli=True to have a Cli (!!! does not return in this case) """

    # Network general options
    net.setLogLevel('info')
    # net.disableArpTables()
    
    switchs = []
    for i in range(1,nb_switch+1):
        switch_name = "s"+str(i)
        switchs.append(switch_name)
        net.addP4Switch(switch_name)
        net.addHost("h"+str(i))
        
    
    for i,s in enumerate(switchs):
        net.addLink(s,"h"+str(i+1))
        for next_sw in switchs[i+1::]:
            net.addLink(s,next_sw)





    # Assignment strategy
    net.l3()

    # Nodes general options
    net.enablePcapDumpAll()
    net.enableLogAll()
    if not Cli :
        net.disableCli()
    net.startNetwork()
    
    
if __name__ == '__main__':
    import sys
    if len(sys.argv)>1:
        try:
            nb_switch = int(sys.argv[1])
        except Exception as e:
            print("Error passing argument ",e)
            quit()
        main(Cli=True,nb_switch=nb_switch)
            
    else:
        main(Cli=True)