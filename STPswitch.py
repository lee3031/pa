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
        self.forwardingTable = {} # keys = clients, values = port
        self.controlPacketValues = [int(self.addr), 0, int(self.addr), int(self.addr)]  # [root, cost, self, hop]
        self.prevLinkCosts = {}


    def handlePacket(self, port, packet):
        """TODO: process incoming packet"""
        if packet.isData():
            if packet.dstAddr != "X":
                if packet.dstAddr in self.forwardingTable.keys():
                    self.send(self.forwardingTable[packet.dstAddr], packet)
            else:
                if packet not in self.recvdPkts:
                    self.forwardingTable[packet.srcAddr] = port
                    # print("{} from {}".format(packet.srcAddr, port))
                    for p in self.links.keys():
                        if p != port and self.links[p].status == Link.ACTIVE:
                            self.send(p, packet)
        elif packet.isControl():
            content = self.controlPacketContentToValue(packet.content)
            isUpdated = False
            '''
                        if content[2] == self.controlPacketValues[3]:  # Case 1: Advertisement from current next hop to root
                isUpdated = True
                if self.controlPacketValues[0] < content[0]:  # If X has smaller root than Y
                    self.controlPacketValues = [int(self.addr), 0, int(self.addr), int(self.addr)]
                else:
                    self.controlPacketValues[0] = content[0]
                    self.controlPacketValues[1] = content[1] + 1
                    self.controlPacketValues[3] = content[2]
            else:
            '''
            if content[0] < self.controlPacketValues[0]:
                self.controlPacketValues[0] = content[0]
                self.controlPacketValues[1] = content[1] + int(self.links[port].l / 100)
                self.controlPacketValues[3] = content[2]
                isUpdated = True
            elif content[0] == self.controlPacketValues[0] and content[1] < (self.controlPacketValues[1] - int(self.links[port].l / 100)):  # Same root, smaller cost
                self.controlPacketValues[1] = content[1] + int(self.links[port].l / 100)
                self.controlPacketValues[3] = content[2]
                isUpdated = True
            elif content[0] == self.controlPacketValues[0] and content[1] == (self.controlPacketValues[1] - int(self.links[port].l / 100)):
                if content[2] < self.controlPacketValues[3]:
                    self.controlPacketValues[1] = content[1] + int(self.links[port].l / 100)
                    self.controlPacketValues[3] = content[2]
                    isUpdated = True

            if isUpdated:
                controlPacketContent = (self.controlPacketToString(self.controlPacketValues))
                controlPacket = Packet(Packet.CONTROL, self.addr, 'X', controlPacketContent)
                # print(self.addr + " has changed its view to " + controlPacketContent)
                for port in self.links:
                    if (self.links[port].get_e2(self.addr)).isnumeric():
                        self.send(port, controlPacket)


            # MAKE LINK ACTIVE
            self.makeLinkActive(str(self.controlPacketValues[3]))

            # MAKE LINK INACTIVE
            if self.controlPacketValues[3] != content[2] and content[3] != self.controlPacketValues[2]:
                # self.f.write("making link inactive - " + str(content[2]))
                self.makeLinkInactive(str(content[2]))

    def makeLinkActive(self, nextHop):
        for link in self.links.values():
            if link.get_e2(self.addr) == nextHop:
                link.status = Link.ACTIVE
                break

    def makeLinkInactive(self, endpoint2):
        for link in self.links.values():
            if link.get_e2(self.addr) == endpoint2:
                link.status = Link.INACTIVE
                # print("----------INACTIVE")
                break

    def handleNewLink(self, port, endpoint, cost):
        """TODO: handle new link"""
        if port in self.prevLinkCosts and int(endpoint) == self.controlPacketValues[3]:
            self.controlPacketValues[1] = self.controlPacketValues[1] - self.prevLinkCosts[port] + cost
        self.prevLinkCosts[port] = cost


    def handleRemoveLink(self, port, endpoint):
        """TODO: handle removed link"""
        if int(endpoint) == self.controlPacketValues[3]:
            self.controlPacketValues = [int(self.addr), 0, int(self.addr), int(self.addr)]


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
        controlPacket = Packet(Packet.CONTROL, self.addr, 'X', controlPacketContent)
        for port in self.links:
            if (self.links[port].get_e2(self.addr)).isnumeric():
                self.send(port, controlPacket)

    def controlPacketToString(self, controlPacket):
        s = ""
        for i in controlPacket:
            s += str(i) + " "
        return s

    def controlPacketContentToValue(self, content):
        l = content.split()
        l = [int(x) for x in l]
        return l
