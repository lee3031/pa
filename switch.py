# The code is subject to Purdue University copyright policies.
# DO NOT SHARE, DISTRIBUTE, OR POST ONLINE
#

import time
import sys
import _thread
import queue
from link import Link


class Switch():
    """Switch superclass that handles the details of
       packet send/receive and link changes.
       Subclass this class and override the "handle..." methods
       to implement the routing algorithms"""

    def __init__(self, addr, heartbeatTime):
        """Initialize Switch address and threadsafe queue for link changes"""
        self.addr = addr  # address of switch
        self.links = {}  # links indexed by port, i.e., {port:link, ......, port:link}
        self.linkChanges = queue.Queue()
        self.heartbeatTime = heartbeatTime
        self.lastTime = 0
        self.keepRunning = True
        self.f = open("Switch-" + self.addr + ".dump", "w")
        self.recvdPkts = []

    def changeLink(self, change):
        """Add, remove, or change the cost of a link.
           The change argument is a tuple with first element
           'add', or 'remove' """
        self.linkChanges.put(change)

    def addLink(self, port, endpointAddr, link, cost):
        """Add new link to switch"""
        self.links = {p: link for p, link in self.links.items() if p != port}
        self.links[port] = link
        self.handleNewLink(port, endpointAddr, cost)

    def removeLink(self, port):
        """Remove link from switch"""
        endpointAddr = None
        for p, link in self.links.items():
            if p == port:
                endpointAddr = link.get_e2(self.addr)
                break
        self.links = {p: link for p, link in self.links.items() if p != port}
        self.handleRemoveLink(port, endpointAddr)

    def runSwitch(self):
        """Main loop of switch"""
        while self.keepRunning:
            time.sleep(0.1)
            currTimeInMillisecs = int(round(time.time() * 1000))
            try:
                change = self.linkChanges.get_nowait()
                if change[0] == "add":
                    self.addLink(*change[1:])
                elif change[0] == "remove":
                    self.removeLink(*change[1:])
            except queue.Empty:
                pass
            for port in self.links.keys():
                packet = self.links[port].recv(self.addr)
                if packet:
                    self.logRecvdPacket(port, packet)
                    self.handlePacket(port, packet)
            if (currTimeInMillisecs - self.lastTime >= self.heartbeatTime):
                self.lastTime = currTimeInMillisecs
                self.handlePeriodicOps(currTimeInMillisecs)

    def send(self, port, packet):
        """Send a packet out given port"""
        try:
            self.links[port].send(packet, self.addr)
        except KeyError:
            pass

    def logRecvdPacket(self, port, packet):
        """log recvd packets"""
        s = packet.srcAddr + "-" + packet.dstAddr + "-" + packet.content
        if packet.isControl():
            self.f.write(
                "Recvd CONTROL packet (" + packet.srcAddr + "->" + packet.dstAddr + " content=" + packet.content + ") on port " + str(
                    port))
        elif packet.isData():
            self.f.write(
                "Recvd DATA packet (" + packet.srcAddr + "->" + packet.dstAddr + " content=" + packet.content + ") on port " + str(
                    port))
        else:
            self.f.write(
                "Recvd UNKNOWN TYPE packet (" + packet.srcAddr + "->" + packet.dstAddr + " content=" + packet.content + ") on port " + str(
                    port))
        if s in self.recvdPkts:
            self.f.write(" -- DUP PKT!!")
        else:
            self.recvdPkts.append(s)
        self.f.write("\n")

    def handlePacket(self, port, packet):
        """process incoming packet"""
        # default implementation sends packet back out the port it arrived
        self.send(port, packet)

    def handleNewLink(self, port, endpoint, cost):
        """handle new link"""
        pass

    def handleRemoveLink(self, port, endpoint):
        """handle removed link"""
        pass

    def handlePeriodicOps(self, currTimeInMillisecs):
        """handle periodic operations. This method is called every heartbeatTime.
        You can change the value of heartbeatTime in the json file."""
        pass
