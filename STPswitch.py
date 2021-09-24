# The code is subject to Purdue University copyright policies.
# DO NOT SHARE, DISTRIBUTE, OR POST ONLINE
#

import sys
import time
from switch import Switch
from link import Link
from client import Client
from packet import Packet


class STPswitch(Switch):
    """MAC learning and forwarding implementation."""

    def __init__(self, addr, heartbeatTime):
        Switch.__init__(self, addr, heartbeatTime)  # initialize superclass - don't remove
        """TODO: add your own class fields and initialization code here"""
        self.forwardingTable = {}
        self.controlPacketValues = [self.addr, 0, self.addr, self.addr]

    def handlePacket(self, port, packet):
        """TODO: process incoming packet"""
        # default implementation sends packet back out the port it arrived
        if packet.isData():
            if packet.dstAddr != "X":
                pass
            else:
                print("Broadcast packet recvd on port {} on switch {}".format(port, self.addr))
                for p in self.links.keys():
                    if p != port:
                        print("Broadcast packet sent on port {}".format(p))
                        self.send(p, packet)
        elif packet.isControl():
            content = self.controlPacketContentToValue(packet.content)
            if content[0] < self.controlPacketValues[0]:
                self.controlPacketValues[0] = content[0]
                self.controlPacketValues[1] = content[1] + 1
                self.controlPacketValues[3] = content[2]

        self.send(port, packet)

    def handleNewLink(self, port, endpoint, cost):
        """TODO: handle new link"""
        pass

    def handleRemoveLink(self, port, endpoint):
        """TODO: handle removed link"""
        pass

    def handlePeriodicOps(self, currTimeInMillisecs):
        """TODO: handle periodic operations. This method is called every heartbeatTime.
        You can change the value of heartbeatTime in the json file."""
        '''
        TREE GOES HERE!!!
                                  ^
                                /   \
                               /     \
                              /_______\
                                |___|
                            
        '''

        controlPacketContent = (self.controlPacketToString(self.controlPacketValues))
        controlPacket = Packet(2, self.addr, 'X', controlPacketContent)
        for port in self.links:
            if type(self.links[port].e2) != 'Client':
                self.send(port, controlPacket)

        pass

    def controlPacketToString(self, controlPacket):
        s = ""
        for i in self.controlPacketValues:
            s += str(i)
        return s

    def controlPacketContentToValue(self, content):
        l = []
        for character in content:
            l.append(int(character))
        return l
