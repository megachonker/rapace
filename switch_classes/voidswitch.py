from LogicTopo import LogicTopo
from switch_classes.P4switch import P4switch,NodeInfo

class VoidSwitch(P4switch):
    def __init__(self, name: str, topo) :
        # super().__init__(name, [], topo)
        self.role = "void"
        self.connect =[]
        self.name = name