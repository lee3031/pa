# The code is subject to Purdue University copyright policies.
# DO NOT SHARE, DISTRIBUTE, OR POST ONLINE
#

import time
import sys
import queue
from packet import Packet


class Client:
    """Client class sends periodic DATA packets."""

    def __init__(self, addr, allClients, sendRate, updateFunction):
        """Inititaliza parameters"""
        self.addr = addr
        self.allClients = allClients
        self.sendRate = sendRate
        self.lastTime = 0
        self.link = None
        self.updateFunction = updateFunction
        self.sending = True
        self.linkChanges = queue.Queue()
        self.keepRunning = True
        self.counter = 0
        self.f = open("Client-" + self.addr + ".dump", "w")
        self.recvdPkts = []

    def changeLink(self, change):
        """Add a link to the client.
           The change argument should be a tuple ('add', link)"""
        self.linkChanges.put(change)

    def handleRecvdPacket(self, packet):
        """log recvd packets.
           If it's a DATA packet, update the network object with it's
           route"""
        if packet.kind == Packet.DATA:
            if packet.dstAddr != "X":
                self.updateFunction(packet.srcAddr, packet.dstAddr, packet.route, int(packet.content))
            else:
                self.updateFunction(packet.srcAddr, self.addr, packet.route, int(packet.content))

        s = packet.srcAddr + "-" + packet.dstAddr + "-" + packet.content
        if packet.isControl():
            self.f.write(
                "Recvd CONTROL packet (" + packet.srcAddr + "->" + packet.dstAddr + " content=" + packet.content + ")")
        elif packet.isData():
            self.f.write(
                "Recvd DATA packet (" + packet.srcAddr + "->" + packet.dstAddr + " content=" + packet.content + ")")
        else:
            self.f.write(
                "Recvd UNKNOWN TYPE packet (" + packet.srcAddr + "->" + packet.dstAddr + " content=" + packet.content + ")")
        if packet.dstAddr != "X" and packet.dstAddr != self.addr:
            self.f.write(" -- WRONG DST!!")
        if s in self.recvdPkts:
            self.f.write(" -- DUP PKT!!")
        else:
            self.recvdPkts.append(s)
        self.f.write("\n")

    def sendDataPackets(self):
        """Send DATA packets to every other client in the network and one broadcast
        packet"""
        self.counter += 1
        for dstClient in self.allClients:
            packet = Packet(Packet.DATA, self.addr, dstClient, str(self.counter))
            if self.link:
                self.link.send(packet, self.addr)
        packet = Packet(Packet.DATA, self.addr, "X", str(self.counter))  # broadcast packet
        if self.link:
            self.link.send(packet, self.addr)

    def handleTime(self, timeMillisecs):
        """Send DATA packets regularly"""
        if self.sending and (timeMillisecs - self.lastTime > self.sendRate):
            self.sendDataPackets()
            self.lastTime = timeMillisecs

    def runClient(self):
        """Main loop of client"""
        while self.keepRunning:
            time.sleep(0.1)
            timeMillisecs = int(round(time.time() * 1000))
            try:
                change = self.linkChanges.get_nowait()
                if change[0] == "add":
                    self.link = change[1]
            except queue.Empty:
                pass
            if self.link:
                packet = self.link.recv(self.addr)
                if packet:
                    self.handleRecvdPacket(packet)
            self.handleTime(timeMillisecs)

    def lastSend(self):
        """Send one final batch of DATA packets"""
        self.sending = False
        self.sendDataPackets()
