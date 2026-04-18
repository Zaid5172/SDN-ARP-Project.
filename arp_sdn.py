from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.packet import ethernet, arp
import time

log = core.getLogger()


class ARPController(object):

    def __init__(self, connection):
        self.connection = connection
        self.mac_to_port = {}
        self.arp_table = {}
        self.packet_count = 0
        self.arp_count = 0

        connection.addListeners(self)

    def _handle_PacketIn(self, event):
        packet = event.parsed
        in_port = event.port

        if not packet.parsed:
            return

        eth = packet
        self.packet_count += 1

        # ---------------- MAC LEARNING ----------------
        self.mac_to_port[eth.src] = in_port
        log.info("MAC LEARNED: %s → port %s", eth.src, in_port)

        log.info("MAC TABLE:")
        for mac, port in self.mac_to_port.items():
            log.info("  %s → %s", mac, port)

        # ---------------- ARP HANDLING ----------------
        if eth.type == ethernet.ARP_TYPE:
            self.arp_count += 1

            arp_pkt = packet.payload
            src_ip = arp_pkt.protosrc
            dst_ip = arp_pkt.protodst
            src_mac = arp_pkt.hwsrc

            # ARP spoof detection
            if src_ip in self.arp_table and self.arp_table[src_ip] != src_mac:
                log.warning("ARP SPOOF DETECTED: %s", src_ip)
                return

            # Learn ARP
            self.arp_table[src_ip] = src_mac
            log.info("ARP LEARNED: %s → %s", src_ip, src_mac)

            log.info("ARP TABLE:")
            for ip, mac in self.arp_table.items():
                log.info("  %s → %s", ip, mac)

            # If destination known → reply
            if dst_ip in self.arp_table:
                log.info("ARP REPLY: %s known", dst_ip)

                dst_mac = self.arp_table[dst_ip]

                arp_reply = arp()
                arp_reply.opcode = arp.REPLY
                arp_reply.hwsrc = dst_mac
                arp_reply.hwdst = src_mac
                arp_reply.protosrc = dst_ip
                arp_reply.protodst = src_ip

                ether = ethernet()
                ether.type = ethernet.ARP_TYPE
                ether.src = dst_mac
                ether.dst = src_mac
                ether.payload = arp_reply

                msg = of.ofp_packet_out()
                msg.data = ether.pack()
                msg.actions.append(of.ofp_action_output(port=in_port))
                self.connection.send(msg)

            else:
                log.info("ARP FLOOD: %s unknown", dst_ip)

                msg = of.ofp_packet_out()
                msg.data = event.ofp
                msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
                msg.in_port = in_port
                self.connection.send(msg)

        # ---------------- NORMAL PACKET FORWARDING ----------------
        else:
            dst = eth.dst

            if dst in self.mac_to_port:
                out_port = self.mac_to_port[dst]
                log.info("FORWARD: %s → port %s", dst, out_port)

                # Install flow rule with timeout
                fm = of.ofp_flow_mod()
                fm.match = of.ofp_match.from_packet(packet, in_port)
                fm.idle_timeout = 10
                fm.hard_timeout = 30
                fm.actions.append(of.ofp_action_output(port=out_port))
                self.connection.send(fm)

                # Send packet
                msg = of.ofp_packet_out()
                msg.data = event.ofp
                msg.actions.append(of.ofp_action_output(port=out_port))
                msg.in_port = in_port
                self.connection.send(msg)

            else:
                log.info("FLOOD: %s unknown", dst)

                msg = of.ofp_packet_out()
                msg.data = event.ofp
                msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
                msg.in_port = in_port
                self.connection.send(msg)

        # ---------------- STATS ----------------
        log.info("TOTAL PACKETS: %s | ARP PACKETS: %s",
                 self.packet_count, self.arp_count)


def launch():
    def start_switch(event):
        log.info("Switch connected")
        ARPController(event.connection)

    core.openflow.addListenerByName("ConnectionUp", start_switch)
