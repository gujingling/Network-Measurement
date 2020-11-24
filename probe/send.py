from scapy.all import *
from scapy.layers.inet import IP,UDP
from scapy.layers.l2 import Ether,Dot1Q
import struct
import time
import json

class Packet:
    def __init__(self, port, sent_addr,packet_num,links):
        self.dport = port
        self.sent_addr = sent_addr
        self.links=links
        self.edge_port={}
        self.recv_data = []
        self.recv_time = {}
        self.swicth_msg={}
        self.link_rtt = {}
        self.packet_num=packet_num

    def send_recvp(self):
        global send_time
        # while True:
        # f1 = open("time_data", 'w')
        # data_bytes = struct.pack("i", self.data[0])
        print("sniffing:")
        packets = AsyncSniffer(iface="h22-eth0", filter="udp and port 8888", prn=lambda x: self.handle_pkt(x),
                               count=self.packet_num)
        packets.start()
        p=Ether()/Dot1Q(vlan=0)/IP(src=self.sent_addr,dst="10.0.0.2")/UDP(dport=self.dport)
        sendp(p,iface="h22-eth0")
        send_time=time.time()
        # self.packet_num -= 1
        print("send ok!")
        print("prepar receive packet:")
        time.sleep(0.1)




        # t1 = time.time()
        self.recv_data.extend(packets)#p=[p1,p2]  p1.time=recv_time
    def compute(self):
        self.edge_port=self.read_topy()
        for u,v in self.links:
            t1=None
            t2=None
            x,y,z=self.find_port(u,v)
            if (y,z) in self.edge_port.keys():
                if (x,y) in self.edge_port.keys():
                    t1=self.swicth_msg["10.0.1.{}".format(z)][self.edge_port[(y,z)][1]]
                    t2=self.swicth_msg["10.0.1.{}".format(y)][self.edge_port[(x,y)][1]]
                elif (y,x) in self.edge_port.keys():
                    t1 = self.swicth_msg["10.0.1.{}".format(z)][self.edge_port[(y,z)][1]]
                    t2 = self.swicth_msg["10.0.1.{}".format(y)][self.edge_port[(y,x)][0]]
                self.link_rtt[(u,v)] = abs(t1 - t2) * 1000
                print("link {}'s rtt => {}  ----  1 ".format((u, v), abs(t1 - t2) * 1000))
            elif (z,y) in self.edge_port.keys():
                if (x, y) in self.edge_port.keys():
                    t1 = self.swicth_msg["10.0.1.{}".format(z)][self.edge_port[(z,y)[0]]]
                    t2 = self.swicth_msg["10.0.1.{}".format(y)][self.edge_port[(x,y)][1]]
                elif (y,x) in self.edge_port.keys():
                    t1 = self.swicth_msg["10.0.1.{}".format(z)][self.edge_port[(z, y)[0]]]
                    t2 = self.swicth_msg["10.0.1.{}".format(y)][self.edge_port[(y, x)][0]]
                self.link_rtt[(u,v)]=abs(t1-t2)*1000
                print("link {}'s rtt => {} ".format((u, v), abs(t1 - t2) * 1000))
            else:
                print("error,{} has no port msg".format((u,v)))
        print(len(self.link_rtt))

    def handle_pkt(self,pkt):
        pkt.sprintf("{IP:%IP.src%}")
        t = pkt.time
        port = int(pkt[Dot1Q].vlan)
        src = str(pkt[IP].src)
        if src in self.swicth_msg.keys():
            if port in self.swicth_msg[src].keys():
                print("error, {} already in items".format(port))
                return
            self.swicth_msg[src][port] = t
        else:
            temp = {}
            temp[port] = t
            self.swicth_msg[src] = temp

    def read_topy(self):
        port = {}
        port_edges = []
        with open('../../topoInfo/topo0.json', 'r') as f:
            topy = json.load(f)["0"]
        # print(topy)
        for links in topy:
            for k in links.keys():
                # print(k)
                temp = k.split("--->")
                link = (int(temp[0]) + 1, int(temp[1]) + 1)
                # print(link)
                port[link] = int(links[k])
        # print(port)
        # for (u, v) in port.keys():
        #     port[(u, v)] = (port[(u, v)], port[(v, u)])
        for (u, v) in port.keys():
            if (v, u) not in port_edges:
                port[(u, v)] = (port[(u, v)], port[(v, u)])
                port_edges.append((u, v))
        for (u, v) in port_edges:
            del port[(v, u)]
        # port[(0, self.monitor)] = (1, 1)
        return port

    def find_port(self,u,v):
        for path in paths:
            for i in range(1,len(path)-1):
                if path[i]==u and path[i+1]==v:
                    return path[i-1],u,v
                elif path[i] == v and path[i + 1] == u:
                    return path[i-1],v,u


    # self._close_()
if __name__ == '__main__':
    HOST1_IP = "10.0.0.1"
    # HOST2_IP = "10.0.0.2"
    # link_delay = 5
    # l1=0
    packet_num=103
    # send_time=0
    links = [(38, 39), (4, 5), (62, 61), (28, 17), (61, 50), (2, 1), (36, 35), (29, 28), (14, 15), (39, 40), (5, 6),
             (54, 55), (44, 43), (43, 42), (52, 51), (61, 60), (29, 18), (12, 1), (44, 34), (60, 49), (20, 19),
             (37, 36), (30, 29), (3, 2), (13, 12), (46, 47), (22, 21), (53, 54), (23, 24), (40, 41), (45, 46), (6, 7),
             (24, 25), (60, 59), (51, 50), (59, 58), (30, 19), (13, 2), (38, 27), (38, 37), (21, 20), (4, 3), (62, 63),
             (7, 8), (50, 49), (39, 28), (44, 33), (14, 13), (31, 30), (52, 53), (18, 19), (27, 28), (57, 56), (42, 41),
             (64, 63), (12, 22), (35, 46), (55, 45), (66, 56), (34, 35), (10, 11), (58, 57), (17, 16), (25, 26),
             (1, 11), (63, 52), (18, 17), (27, 26), (9, 10), (27, 16), (45, 34), (62, 51), (18, 7), (24, 13), (31, 32),
             (57, 46), (47, 48), (24, 35), (40, 51), (6, 17), (19, 8), (15, 16), (56, 45), (23, 33), (41, 52), (50, 39),
             (32, 33), (55, 66), (29, 40), (11, 22), (12, 23), (55, 44), (49, 38), (30, 41), (8, 9), (49, 48), (65, 64),
             (34, 23), (66, 65), (33, 22), (16, 5)]
    host1 = Packet(8888, HOST1_IP,packet_num,links)
    paths = [[23, 12, 13, 14, 15], [23, 12, 22], [23, 34, 35, 46],
             [23, 34, 35, 36, 37], [23, 34, 44, 43, 42], [23, 34, 44, 55], [23, 12, 1, 11, 10, 9],
             [23, 24, 13, 14, 15, 16], [23, 33, 32, 31, 30, 19], [23, 33, 32, 31, 30, 41], [23, 24, 35, 36, 37, 38],
             [23, 24, 35, 46, 47, 48], [23, 24, 13, 2, 3, 4, 5], [23, 12, 1, 2, 3, 4, 5, 6],
             [23, 24, 25, 26, 27, 28, 17, 6], [23, 33, 22, 21, 20, 19, 8, 7], [23, 33, 32, 31, 30, 29, 18, 7],
             [23, 33, 22, 11, 10, 9, 8], [23, 24, 25, 26, 27, 16, 17], [23, 24, 25, 26, 27, 28, 17, 18],
             [23, 33, 22, 21, 20, 19, 18], [23, 24, 25, 26, 27, 28, 29], [23, 24, 25, 26, 27, 28, 39],
             [23, 33, 32, 31, 30, 29, 40], [23, 24, 25, 26, 27, 38, 39, 40], [23, 24, 25, 26, 27, 38, 39, 50],
             [23, 33, 44, 43, 42, 41, 40, 51], [23, 34, 45, 46, 47, 48, 49], [23, 33, 44, 43, 42, 41, 52, 51],
             [23, 34, 45, 55, 54, 53, 52], [23, 24, 35, 46, 57, 58, 59], [23, 34, 45, 56, 57, 58, 59, 60],
             [23, 34, 45, 56, 66, 65, 64, 63], [23, 33, 44, 55, 66, 65, 64], [23, 24, 25, 26, 27, 16, 5, 6, 7],
             [23, 24, 25, 26, 27, 38, 49, 50, 51], [23, 33, 44, 55, 54, 53, 52, 51, 62],
             [23, 24, 25, 26, 27, 38, 49, 60, 61], [23, 33, 44, 43, 42, 41, 52, 63, 62],
             [23, 24, 25, 26, 27, 38, 49, 50, 61, 62]]
    host1.send_p()
    #print(l1/packet_num)