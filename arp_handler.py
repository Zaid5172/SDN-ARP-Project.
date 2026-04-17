from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ether_types, arp


class Arp(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(Arp, self).__init__(*args, **kwargs)
        self.arp_table = {}

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch()
        actions = [
            parser.OFPActionOutput(
                ofproto.OFPP_CONTROLLER,
                ofproto.OFPCML_NO_BUFFER
            )
        ]

        inst = [parser.OFPInstructionActions(
            ofproto.OFPIT_APPLY_ACTIONS, actions)]

        mod = parser.OFPFlowMod(
            datapath=datapath,
            priority=0,
            match=match,
            instructions=inst
        )

        datapath.send_msg(mod)
        self.logger.info("Switch connected. Table-miss rule sent.")

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        # Only handle ARP
        if eth.ethertype != ether_types.ETH_TYPE_ARP:
            return

        arp_pkt = pkt.get_protocol(arp.arp)

        src_ip = arp_pkt.src_ip
        dst_ip = arp_pkt.dst_ip
        src_mac = arp_pkt.src_mac

        # Learn ARP
        self.arp_table[src_ip] = src_mac
        self.logger.info("LEARNED: %s -> %s", src_ip, src_mac)

        # If destination known → reply
        if dst_ip in self.arp_table:
            self.logger.info("FOUND: %s. Sending ARP reply.", dst_ip)

            dst_mac = self.arp_table[dst_ip]

            p = packet.Packet()
            p.add_protocol(ethernet.ethernet(
                ethertype=ether_types.ETH_TYPE_ARP,
                dst=src_mac,
                src=dst_mac
            ))

            p.add_protocol(arp.arp(
                opcode=arp.ARP_REPLY,
                src_mac=dst_mac,
                src_ip=dst_ip,
                dst_mac=src_mac,
                dst_ip=src_ip
            ))

            p.serialize()

            actions = [
                parser.OFPActionOutput(ofproto.OFPP_IN_PORT)
            ]

            out = parser.OFPPacketOut(
                datapath=datapath,
                buffer_id=ofproto.OFP_NO_BUFFER,
                in_port=ofproto.OFPP_CONTROLLER,
                actions=actions,
                data=p.data
            )

            datapath.send_msg(out)

        else:
            self.logger.info("MISS: %s not in ARP table", dst_ip)
