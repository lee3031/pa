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
        self.controlPacketValues = [int(self.addr), 0, int(self.addr), int(self.addr)]  # [root, cost, self, hop]

    def handlePacket(self, port, packet):
        """TODO: process incoming packet"""
        # default implementation sends packet back out the port it arrived
        if packet.isData():
            if packet.dstAddr != "X":
                pass
            else:
                for p in self.links.keys():
                    if p != port and self.links[p].status == Link.ACTIVE:
                        self.send(p, packet)
        elif packet.isControl():
            content = self.controlPacketContentToValue(packet.content)
            isUpdated = False
            if content[2] == self.controlPacketValues[3]:  # Case 1: Advertisement from current next hop to root
                pass
                isUpdated = True
                if self.controlPacketValues[0] < content[0]:  # If X has smaller root than Y
                    self.controlPacketValues = [int(self.addr), 0, int(self.addr), int(self.addr)]
                else:
                    self.controlPacketValues[0] = content[0]
                    self.controlPacketValues[1] = content[1] + 1
                    self.controlPacketValues[3] = content[2]
            else:  # Case 2: Advertisement not from current next hop to root
                if content[0] < self.controlPacketValues[0]:
                    self.controlPacketValues[0] = content[0]
                    self.controlPacketValues[1] = content[1] + 1
                    self.controlPacketValues[3] = content[2]
                    isUpdated = True
                elif content[0] == self.controlPacketValues[0] and content[2] < self.controlPacketValues[2]:  # Same root, smaller cost
                    self.controlPacketValues[1] = content[1] + 1
                    self.controlPacketValues[3] = content[2]
                    isUpdated = True
                elif content[0] == self.controlPacketValues[0] and content[2] == (self.controlPacketValues[2] - 1):
                    if content[2] < self.controlPacketValues[3]:
                        self.controlPacketValues[1] = content[1] + 1
                        self.controlPacketValues[3] = content[2]
                        isUpdated = True
            if isUpdated:
                controlPacketContent = (self.controlPacketToString(self.controlPacketValues))
                controlPacket = Packet(Packet.CONTROL, self.addr, 'X', controlPacketContent)
                for port in self.links:
                    if type(self.links[port].get_e2(self.addr)) != 'Client':
                        self.send(port, controlPacket)

            # MAKE LINK INACTIVE
            if self.controlPacketValues[3] != content[2] and content[3] != self.controlPacketValues[2]:
                self.makeLinkInactive(content[2])
        # self.send(port, packet)

    def makeLinkInactive(self, endpoint2):
        for port in self.links:
            if self.links[port].get_e2(self.addr) == endpoint2:
                self.links[port].status = Link.INACTIVE
                break

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
        print("hi its me, " + self.addr + ", and my links are " + str(self.links))
        for i in range(10000000):
            pass
        print("hi its me again, " + self.addr + ", and my links are " + str(self.links))

        controlPacketContent = (self.controlPacketToString(self.controlPacketValues))
        controlPacket = Packet(Packet.CONTROL, self.addr, 'X', controlPacketContent)
        for port in self.links:
            if (self.links[port].get_e2(self.addr)).isnumeric():
                self.send(port, controlPacket)

        pass

    def controlPacketToString(self, controlPacket):
        s = ""
        for i in controlPacket:
            s += str(i)
        return s

    def controlPacketContentToValue(self, content):
        l = []
        for character in content:
            l.append(int(character))
        return l
