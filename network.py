from p4utils.mininetlib.network_API import NetworkAPI

net = NetworkAPI()

# Network general options
net.setLogLevel('info')
net.disableArpTables()

# Network definition
net.addP4Switch('s0')
net.addP4Switch('s1')
net.addP4Switch('s2')
net.addP4Switch('s3')
net.addP4Switch('s4')
net.addP4Switch('s5')
net.addP4Switch('s6')
net.addP4Switch('s7')

net.addHost('h1')


net.addLink('s0','s1')
net.addLink('s0','s2')
net.addLink('s0','s3')
net.addLink('s0','s4')
net.addLink('s0','s5')
net.addLink('s0','s6')
net.addLink('s0','s7')
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



net.addLink('h1','s7')





# Assignment strategy
net.l2()

# Nodes general options
net.enablePcapDumpAll()
net.enableLogAll()
net.enableCli()
net.startNetwork()