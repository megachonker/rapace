from p4utils.mininetlib.network_API import NetworkAPI

net = NetworkAPI()

def stop():
    """ Stop the network """
    print(net.net is None)
    
    net.net.stop()


def main(Cli=True):
    """ Start the physical network, it is a clique of 8 switchs with one host per switchs
        l2 strategy 
        Cli=True to have a Cli (!!! does not return in this case) """

    # Network general options
    net.setLogLevel('info')
    # net.disableArpTables()

    # Network definition
    net.addP4Switch('s1')
    net.addP4Switch('s2')
    net.addP4Switch('s3')
    net.addP4Switch('s4')
    net.addP4Switch('s5')
    net.addP4Switch('s6')
    net.addP4Switch('s7')

    net.addHost('h1')
    net.addHost('h2')
    net.addHost('h3')
    net.addHost('h4')
    net.addHost('h5')
    net.addHost('h6')
    net.addHost('h7')


    net.addLink('s1','s2')
    net.addLink('s1','s3')
    net.addLink('s1','s4')
    net.addLink('s1','s5')
    net.addLink('s1','s6')
    net.addLink('s1','s7')
    net.addLink('s2','s3')
    net.addLink('s2','s4')
    net.addLink('s2','s5')
    net.addLink('s2','s6')
    net.addLink('s2','s7')
    net.addLink('s3','s4')
    net.addLink('s3','s5')
    net.addLink('s3','s6')
    net.addLink('s3','s7')
    net.addLink('s4','s5')
    net.addLink('s4','s6')
    net.addLink('s4','s7')
    net.addLink('s5','s6')
    net.addLink('s5','s7')
    net.addLink('s6','s7')


    net.addLink('h1','s1')
    net.addLink('h2','s2')
    net.addLink('h3','s3')
    net.addLink('h4','s4')
    net.addLink('h5','s5')
    net.addLink('h6','s6')
    net.addLink('h7','s7')





    # Assignment strategy
    net.l2()

    # Nodes general options
    net.enablePcapDumpAll()
    net.enableLogAll()
    if not Cli :
        net.disableCli()
    net.startNetwork()
    
    
if __name__ == '__main__':
    main(Cli=True)