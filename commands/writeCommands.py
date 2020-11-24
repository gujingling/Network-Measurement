import json
import time
import copy
import socket
import sys
class table:
    def __init__(self,links,path,switches,monitor):
        self.Links=links
        self.link_flag=dict()  ### 记录待测链路是否进行了多播返回操作
        self.n_switches=switches
        self.monitor=monitor
        self.sip="10.0.0.1"
        self.dip="10.0.0.2"
        self.multi_flag={}
        self.paths=path
        self.multi_p=[]
        self.multi_n={}
        self.edges_port={}
        self.json_dict={}
        # self.act={"action 1":{},"action 2":{}}
    ################################################
    #根据待测链路修剪paths
    def cut_paths(self):
        cut=[]
        for path in self.paths:
            for i in range(len(path)-1,-1,-1):
                if (path[i],path[i-1]) in self.Links or (path[i-1],path[i]) in self.Links:
                    break
                path.pop()
            if len(path)<=2:
                cut.append(path)
        for path in cut:
            self.paths.remove(path)
        cut_p = []
        for i in range(len(self.paths) - 1, -1, -1):
            for j in range(len(self.paths) - 1, -1, -1):
                if i == j:
                    continue
                cut_index = len(self.paths[i])
                for n in range(len(self.paths[i]) - 1, 0, -1):
                    if self.paths[i][n] in self.paths[j]:
                        index1 = self.paths[j].index(self.paths[i][n])
                        if self.paths[i][n - 1] in self.paths[j]:
                            index2 = self.paths[j].index(self.paths[i][n - 1])
                            if abs(index1 - index2) == 1:
                                # print(self.paths[i], "的", (self.paths[i][n], self.paths[i][n - 1]), "在{}中".format(self.paths[j]))
                                cut_index = n
                        else:
                            break
                    else:
                        break
                self.paths[i] = self.paths[i][:cut_index]
        # print("修剪后的：", self.paths)
        for p in self.paths:
            if len(p) > 2:
                cut_p.append(p)
        self.paths= cut_p
        # print(paths)
        # print(len(paths))
        cut = []
        for path in self.paths:
            for i in range(len(path) - 1, -1, -1):
                if (path[i], path[i - 1]) in self.Links or (path[i - 1], path[i]) in self.Links:
                    break
                path.pop()
            if len(path) <= 2:
                cut.append(path)
        for path in cut:
            self.paths.remove(path)
        print(self.recieve_num())

    ################################################
    # 多播的交换机id,以及多播下一跳
    def compute_muiti(self,l):
        multi_nodes={}
        multi_list=[]
        # x=0
        for i in range(len(l)):## 对于每一条path来说
            for j in range(i+1,len(l)):   ###对于其他路径来说
                for n in range(min(len(l[i]),len(l[j]))):    #获得两条路径的最短长度
                    if l[i][n]==l[j][n]:
                        continue
                    if l[i][:n] not in multi_list:
                        multi_list.append(l[i][:n])
                        x = len(multi_list)
                        multi_nodes[x] = []
                        multi_nodes[x].append(l[i][n])
                        multi_nodes[x].append(l[j][n])
                    else:
                        index = multi_list.index(l[i][:n]) + 1
                        if l[i][n] not in multi_nodes[index]:
                            # print(l[i][:n], "already in multi_p", "add:", l[i][n])
                            multi_nodes[index].append(l[i][n])
                        elif l[j][n] not in multi_nodes[index]:
                            # print(l[i][:n], "already in multi_p", "add:", l[j][n])
                            multi_nodes[index].append(l[j][n])
                    break
        return multi_list,multi_nodes
    #############################################
    # 交换机连接对应端口情况  如s1,s2: 1,2   s1端口1连接s2端口2
    def read_port(self):
        # paths = [[[2, 13, 14, 3], [2, 4, 16, 5], [2, 4, 16, 9], [2, 12, 10, 3]],
        #       [[4, 2, 7], [4, 16, 5, 8], [4, 16, 9, 8], [4, 2, 23, 17], [4, 2, 18, 21], [4, 2, 12, 22, 20]],
        #      [[7, 1, 3], [7, 1, 16], [7, 21, 3], [7, 6, 19]],
        #       [[17, 10, 3, 11], [17, 20, 15, 9], [17, 7, 19], [17, 10, 11], [17, 10, 16], [17, 10, 12, 22], [17, 13, 19]]]
        f=open("Geant.txt",'r')
        topolines = f.readlines()
        node_degree = {n: 0 for n in range(self.n_switches+1)}
        # node_degree[self.monitor]=1
        edges_port={}
        for topoline in topolines:
            line=topoline.split('\n')[0].split(' ')
            for i in line:
                node_degree[int(i)]+=1
            edges_port[(int(line[0]),int(line[1]))]=(node_degree[int(line[0])],node_degree[int(line[1])])
        # print(edges_port)
        return edges_port
        # print(node_degree) n
    # read_port()
    ############################################
    #读取topy_0
    def read_topy(self):
        port = {}
        port_edges=[]
        with open('../../../topoInfo/topo0.json', 'r') as f:
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
        port[(0, self.monitor)] = (1, 1)
        return port
    ############################################
    ##根据两个相邻节点找到端口
    def get_port(self,n,m):
        if (n,m) in self.edges_port.keys():
            return self.edges_port[(n,m)][0]
        elif (m,n) in self.edges_port.keys():
            return  self.edges_port[(m,n)][1]
        return -1
    #############################################
    # 交换机的端口数
    def read_degree(self):
        topy=open("Geant.txt",'r')
        node_degree = {n: 0 for n in range(1, self.n_switches+1)}
        #######################
        node_degree[self.monitor]=1
        ######################
        topolines = topy.readlines()
        for topoline in topolines:
            line = topoline.split('\n')[0].split(' ')
            for i in line:
                node_degree[int(i)] += 1
        return node_degree
    #############################################
    '''
    # 交换机各个端口对应的mac
    def getMAC(self,n_switches):
        start = 11
        degree = read_degree(n_switches,monitor)
        print(degree)
        mac_dic = {n:{} for n in range(1, n_switches+1)}
        add = 0
        for i in range(1, n_switches + 1):
            for j in range(start + add, start + add + degree[i]):
               mac_dic[i][j -start-add+1]="aa:bb:cc:dd:ee:%d" % j
            add += degree[i]
        return mac_dic
    # mac_dicmac=getMAC()
    # for i in range(1,24):
    #     print("s{}:{}".format(i,mac_dicmac[i]))'''
    ###########################################
    #结果汇总
    def make_res(self):
        self.cut_paths()
        print(self.paths)
        self.multi_p, self.multi_n = self.compute_muiti(self.paths)
        # print("multi_p",self.multi_p,'\n',"multi_n",self.multi_n)
        # self.edges_port=self.read_port()
        self.edges_port=self.read_topy()
        print(self.edges_port)
        self.is_probelink()
        print("multi_p", self.multi_p, '\n', "multi_n", self.multi_n)
        # print(self.multi_n)
        # print(len(self.multi_n))
        self.IPV4forward()
        self.last_forward()
        self.multi_forward()
        print(self.json_dict)
        print(len(self.json_dict['23']))
        with open('commmands.json','w') as f:
            # data=json.dumps(self.json_dict)
            # try:
            #     s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            #     s.connect(("localhost",6666))
            # except socket.error as msg:
            #     print(msg)
            #     sys.exit(1)
            # # print(len(data))
            # data_b=str.encode(data)
            # data_b+="*"
            # s.sendall(data_b)
            json.dump(self.json_dict,f)
            # json.dump(self.edges_port,f)
            print("done!")
    ###########################################
    #判断是否是待测链路    探测链路两端节点都要返回数据包（只处理了一端节点 另一端节点未处理#）
    # def probeLink(self):
    #     for i in self.Links:
    def is_probelink(self):
        for x in self.Links:
            self.link_flag[x]=0
        for path in self.paths:
            p_list = []
            for i in range(len(path)-1):##判断待测链路节点是否已经是多播节点 不是则新建多播组 是则加入多播组,尾节点会直接返回
                flag=0
                p_list.append(path[i])
                if (path[i],path[i+1]) in self.Links:
                    flag=1
                elif (path[i+1],path[i]) in self.Links:
                    flag=2
                if flag ==1  and self.link_flag[(path[i],path[i+1])]==0:
                    ##处理节点1
                    self.add_multi(p_list,path,i)
                    ##处理节点2
                    if path[i+1]==path[-1]:  #如果尾节点是路径最后一跳 则不进行尾节点的操作
                        continue
                    p_next_list = copy.deepcopy(p_list)
                    p_next_list.append(path[i + 1])
                    self.add_multi(p_next_list,path,i+1)
                    # p_list.pop()
                    self.link_flag[(path[i], path[i + 1])] =1
                elif flag==2 and self.link_flag[(path[i+1],path[i])]==0:
                    # print("flag==2")
                    # p_list.append(path[i])
                    self.add_multi(p_list, path, i)
                    ##处理节点2
                    if path[i + 1] == path[-1]:  # 如果尾节点是路径最后一跳 则不进行尾节点的操作
                        continue
                    p_next_list=copy.deepcopy(p_list)
                    p_next_list.append(path[i + 1])
                    # time.sleep(1)
                    self.add_multi(p_next_list, path, i + 1)
                    # p_list.pop()
                    self.link_flag[(path[i+1], path[i])] = 1


    def add_multi(self,p_list,path,i):      #####path[i] 不仅返回给上一跳 还要发送到下一跳
        if p_list in self.multi_p:
            index_p = self.multi_p.index(p_list) + 1
            if path[i+1] not in self.multi_n[index_p]:
                self.multi_n[index_p].append(path[i+1])
                # print(p_list, "is in multi_p,在{}处添加多播节点i+1=>{}".format(index_p,path[i+1]))
            if path[i-1] not in self.multi_n[index_p]:
                self.multi_n[index_p].append(path[i-1])
                # print(p_list, "is in multi_p,在{}处添加多播节点i-1=>{}".format(index_p, path[i - 1]))
        else:
            self.multi_p.append(p_list)
            n_list = [path[i-1], path[i+1]]
            self.multi_n[len(self.multi_p)] = n_list
            # print(p_list, "is not in multi_p,添加多播节点=>{}".format(n_list),"multi_p 长度：",len(self.multi_p))
            # print(self.multi_p)


    def recieve_num(self):
        num = 0
        if len(self.paths[0]) > 2:
            for n in range(1, len(self.paths[0])):
                if (self.paths[0][n],self.paths[0][n-1]) in self.Links:
                    print((self.paths[0][n],self.paths[0][n-1]))
                    num=num+1
                elif (self.paths[0][n - 1], self.paths[0][n]) in self.Links:
                    print((self.paths[0][n-1], self.paths[0][n]))
                    num = num + 1
        print(num)
        for i in range(1, len(self.paths)):
            max_flag = 0
            if len(self.paths[i]) > 2:
                for j in range(0, i):
                    flag = 0
                    length = min(len(self.paths[i]), len(self.paths[j]))
                    for n in range(0, length):
                        if self.paths[j][n] == self.paths[i][n]:
                            flag += 1
                        else:
                            break
                    max_flag = max(max_flag, flag)
                # print(max_flag)
                for j in range(max_flag, len(self.paths[i])):
                    print("(n,n-1):",((self.paths[i][j], self.paths[i][j - 1])))
                    if (self.paths[i][j], self.paths[i][j - 1]) in self.Links or (self.paths[i][j - 1], self.paths[i][j]) in self.Links:
                        print((self.paths[i][j], self.paths[i][j - 1]))
                        num = num + 1
        return num
    ###########################################
    #中间转发节点
    def IPV4forward(self):
        for path in self.paths:
            # print("path ",path)
            p_list=[0]
            last_node = path[-1]
            for i in range(1,len(path)-1):
                # print("i:",i)
                multi_flag=1
                f = open("commands/commands{}.txt".format(path[i]), 'a')
                p_list.append(path[i])
                if p_list in self.multi_p:
                    n_index=self.multi_p.index(p_list)+1
                    if path[i+1] not in self.multi_n[n_index]:
                        multi_flag=0
                elif p_list not in self.multi_p:
                    multi_flag=0
                if multi_flag ==0:
                    # print((path[i],path[i+1]),'=>',self.get_port(path[i], path[i+1]))
                    temp = {}
                    outport=[]
                    outport.append(self.get_port(path[i], path[i+1]))
                    temp['outport'] = outport
                    act={}
                    act['action1']=temp
                    # act['action 2']={}
                    table = {}
                    table['10.0.0.1,{}'.format(self.get_port(path[i],path[i-1]))] = act
                    if '{}'.format(path[i]) not in self.json_dict.keys():
                        self.json_dict['{}'.format(path[i])] = table
                    elif '10.0.0.1,{}'.format(self.get_port(path[i],path[i-1])) in self.json_dict['{}'.format(path[i])].keys():
                        self.json_dict['{}'.format(path[i])][
                            '10.0.0.1,{}'.format(self.get_port(path[i], path[i-1]))]['action1']['outport'] = outport
                    elif '10.0.0.1,{}'.format(self.get_port(path[i],path[i-1])) not in self.json_dict['{}'.format(path[i])].keys():
                        self.json_dict['{}'.format(path[i])]['10.0.0.1,{}'.format(self.get_port(path[i],path[i-1]))]=act

                    # f.write("setoutport 10.0.0.1 i{} => {}".format(self.get_port(path[i],path[i-1]),self.get_port(path[i],path[i+1]))+'\n')
                    '''
                    if (path[i],path[i+1]) in self.edges_port.keys():
                        if (path[i-1],path[i]) in self.edges_port.keys():
                            # f = open("commands{}.txt".format(path[i]), 'a')
                            f.write("setoutport 10.0.0.1 {} => {}".format(self.edges_port[(path[i-1],path[i])][1],self.edges_port[(path[i],path[i+1])][0]))
                            # f.close()
                        elif (path[i],path[i-1]) in self.edges_port.keys():
                            # f = open("commands{}.txt".format(path[i]), 'a')
                            f.write("setoutport 10.0.0.1 {} => {}".format(self.edges_port[(path[i], path[i-1])][0],
                                                                          self.edges_port[(path[i], path[i+1])][0]))
                        f.write("\n")
                           # f.close()
                    elif (path[i+1],path[i]) in self.edges_port.keys():
                        if (path[i-1],path[i]) in self.edges_port.keys():
                            # f = open("commands{}.txt".format(path[i]), 'a')
                            f.write("setoutport 10.0.0.1 {} => {}".format(self.edges_port[(path[i-1],path[i])][1],self.edges_port[(path[i+1],path[i])][1]))
                            # f.close()
                        elif (path[i],path[i-1]) in self.edges_port.keys():
                            # f = open("commands{}.txt".format(path[i]), 'a')
                            f.write("setoutport 10.0.0.1 {} => {}".format(self.edges_port[(path[i], path[i-1])][0],
                                                                          self.edges_port[(path[i+1], path[i])][1]))
                        f.write("\n")
                            # f.close()
                    '''
                #返回数据包的处理
                # if path[i]!=last_node:  #中间节点的返回处理       (src,inport)  action1: outport:
                outport = []
                outport.append(self.get_port(path[i], path[i - 1]))
                for j in range(i+1,len(path)):
                    temp={}
                    act={}
                    temp['outport'] = outport
                    act['action1']=temp
                    # self.act['action 2']={}
                    table = {}
                    table['10.0.1.{},{}'.format(path[j],self.get_port(path[i], path[i+1]))] = act
                    if '{}'.format(path[i]) not in self.json_dict.keys():
                        # print('{}'.format(path[i]),"not in elf.json_dict.keys()","self.json_dict['{}'] ={}".format(path[i],table))
                        self.json_dict['{}'.format(path[i])] = table
                    elif '10.0.1.{},{}'.format(path[j],self.get_port(path[i], path[i+1])) in self.json_dict['{}'.format(path[i])].keys():
                        # print('{}'.format(path[i]),('10.0.1.{},{}'.format(path[j],self.get_port(path[i], path[i+1]))),"in json list","['action1']['outport'] = ",self.get_port(path[i], path[i-1]))
                        self.json_dict['{}'.format(path[i])][
                            '10.0.1.{},{}'.format(path[j], self.get_port(path[i], path[i + 1]))]['action1']['outport'] = outport
                    elif ('10.0.1.{}'.format(path[j]), self.get_port(path[i], path[i+1])) not in self.json_dict['{}'.format(path[i])].keys():
                        # print('{}'.format(path[i]),('10.0.1.{}'.format(path[j]), self.get_port(path[i], path[i + 1])), "not in json list",
                        #       '10.0.1.{},{}'.format(path[j], self.get_port(path[i], path[i + 1])),"=",act)
                        self.json_dict['{}'.format(path[i])]['10.0.1.{},{}'.format(path[j],self.get_port(path[i], path[i+1]))]=act



                    # f.write("setoutport 10.0.1.{} {} => {}".format(path[i],self.get_port(path[i], path[i + 1]),self.get_port(path[i],path[i-1]))+'\n')

                    '''
                    if (path[i],path[i+1]) in self.edges_port.keys():
                        if (path[i-1],path[i]) in self.edges_port.keys():
                            f.write("setoutport 10.0.1.{} {} => {}".format(path[i],
                                                                          self.edges_port[(path[i], path[i + 1])][0],self.edges_port[(path[i-1],path[i])][1]))
                        elif (path[i], path[i-1]) in self.edges_port.keys():
                            f.write("setoutport 10.0.1.{} {} => {}".format(path[i],
                                                                           self.edges_port[(path[i], path[i + 1])][0],
                                                                           self.edges_port[(path[i], path[i-1])][0]))

                    elif (path[i+1],path[i]) in self.edges_port.keys():
                        # print("(path[{}],path[{}]):{}".format(i+1,i,(path[i+1],path[i])))
                        if (path[i-1],path[i]) in self.edges_port.keys():
                            f.write("setoutport 10.0.1.{} {} => {}".format(path[i],
                                                                          self.edges_port[(path[i+1], path[i])][1],self.edges_port[(path[i-1],path[i])][1]))
                        elif (path[i], path[i-1]) in self.edges_port.keys():
                            f.write("setoutport 10.0.1.{} {} => {}".format(path[i],
                                                                           self.edges_port[(path[i+1], path[i])][1],
                                                                          self.edges_port[(path[i], path[i-1])][0]))                                              '''
                # f.write("\n")
                # f.close()



    ###########################################
    #路径最后一跳 返回探测包  修改srcip 、 dstip
    def last_forward(self):
        for path in self.paths:
            f = open("commands/commands{}.txt".format(path[ - 1]), 'a')
            f.write("setoutport 10.0.0.1 {} => {}".format(self.get_port(path[- 1],path[- 2]),self.get_port(path[- 1],path[- 2]))+'\n')
            ####json
            temp={}
            # temp['outport']=self.get_port(path[- 1],path[- 2])
            temp['src']='10.0.1.{}'.format(path[-1])
            temp['dst']='10.0.0.1'
            # temp['vlan']=self.get_port(path[- 1],path[- 2])
            act={}
            act['action2']=temp
            table={}
            table['10.0.0.1,{}'.format(self.get_port(path[- 1],path[- 2]))]=act
            if '{}'.format(path[-1]) not in self.json_dict.keys():
                self.json_dict['{}'.format(path[-1])] = table
            elif '10.0.0.1,{}'.format(self.get_port(path[- 1],path[- 2])) in self.json_dict[
                '{}'.format(path[-1])].keys():
                self.json_dict['{}'.format(path[-1])][
                    '10.0.0.1,{}'.format(self.get_port(path[- 1], path[- 2]))]['action2']=temp
            elif '10.0.0.1,{}'.format(self.get_port(path[- 1],path[- 2])) not in self.json_dict[
                '{}'.format(path[-1])].keys():
                self.json_dict['{}'.format(path[-1])][
                    '10.0.0.1,{}'.format(self.get_port(path[- 1], path[- 2]))] = act

            f.write("setforwordip 10.0.0.1 {} =>10.0.1.{} 10.0.0.1".format(self.get_port(path[- 1],path[- 2]), path[-1])+'\n')
            '''
            if (path[-2], path[-1]) in self.edges_port.keys():
                f.write("setoutport 10.0.0.1 {} => {}".format(self.edges_port[(path[-2], path[-1])][1],
                                                              self.edges_port[(path[-2], path[-1])][1]))
                f.write("\n")
                f.write("setforwordip 10.0.0.1 {} =>10.0.1.{} 10.0.0.1".format(
                    self.edges_port[(path[- 2], path[- 1])][1], path[- 1]))
                f.write("\n")
            elif (path[-1], path[-2]) in self.edges_port.keys():
                f.write("setoutport 10.0.0.1 {} => {}".format(self.edges_port[(path[-1], path[-2])][0],
                                                              self.edges_port[(path[-1], path[-2])][0]))
                f.write("\n")
                f.write("setforwordip 10.0.0.1 {} =>10.0.1.{} 10.0.0.1".format(
                    self.edges_port[(path[-1], path[-2])][0], path[- 1]))
                f.write("\n")'''
            f.close()
    ###########################################
    #####处理多播转发 多播组与端口的绑定以及多播后srcip、dstip的修改
    def multi_forward(self):
        for i in self.multi_n.keys():
            # egress_rid=0
            n_list=self.multi_p[i-1]
            # print("n_list:",n_list,"multi_n:",self.multi_n[i])
            outport=[]
            for m in self.multi_n[i]:
                if m!=n_list[-2]:
                    # print(n_list[-1],"=>",m,"outport:",self.get_port(n_list[-1], m))
                    outport.append(self.get_port(n_list[-1], m))
                else:
                    # print(n_list,"=>",m,"修改src、dst","outport=",self.get_port(n_list[-1],n_list[-2]))
                    temp = {}
                    # temp['outport'] = self.get_port(n_list[-1],n_list[-2])
                    temp['src'] = '10.0.1.{}'.format(n_list[-1])
                    temp['dst'] = '10.0.0.1'
                    # temp['vlan'] = self.get_port(n_list[-1],n_list[-2])
                    act = {}
                    act['action2'] = temp
                    table = {}
                    table['10.0.0.1,{}'.format(self.get_port(n_list[-1],n_list[-2]))] = act
                    if '{}'.format(n_list[-1]) not in self.json_dict.keys():
                        self.json_dict['{}'.format(n_list[-1])] = table
                    elif '10.0.0.1,{}'.format(self.get_port(n_list[-1],n_list[-2])) in self.json_dict[
                        '{}'.format(n_list[-1])].keys():
                        self.json_dict['{}'.format(n_list[-1])][
                            '10.0.0.1,{}'.format(self.get_port(n_list[-1], n_list[-2]))]['action2'] = temp
                    elif '10.0.0.1,{}'.format(self.get_port(n_list[-1],n_list[-2])) not in self.json_dict[
                        '{}'.format(n_list[-1])].keys():
                        self.json_dict['{}'.format(n_list[-1])][
                            '10.0.0.1,{}'.format(self.get_port(n_list[-1], n_list[-2]))] =act
            # print("outport:",outport)
            temp = {}
            temp['outport'] = outport
            act = {}
            act['action1'] = temp
            table = {}
            table['10.0.0.1,{}'.format(self.get_port(n_list[-1],n_list[-2]))] = act
            if '{}'.format(n_list[-1]) not in self.json_dict.keys():
                self.json_dict['{}'.format(n_list[-1])] = table
            elif '10.0.0.1,{}'.format(self.get_port(n_list[-1],n_list[-2])) in self.json_dict[
                '{}'.format(n_list[-1])].keys():
                self.json_dict['{}'.format(n_list[-1])][
                    '10.0.0.1,{}'.format(self.get_port(n_list[-1], n_list[-2]))]['action1'] = temp
            elif '10.0.0.1,{}'.format(self.get_port(n_list[-1],n_list[-2])) not in self.json_dict[
                '{}'.format(n_list[-1])].keys():
                self.json_dict['{}'.format(n_list[-1])][
                    '10.0.0.1,{}'.format(self.get_port(n_list[-1], n_list[-2]))] = act

            f = open("commands/commands{}.txt".format(n_list[-1]), 'a')
            f.write("multicast 10.0.0.1 {} => outport {}".format(self.get_port(n_list[-1],n_list[-2]),' '.join(str(p) for p in outport))+'\n')
            '''
            for n in self.multi_n[i]:  ####端口号和egress_rid的绑定
                if (n_list[-1], n) in self.edges_port.keys():
                    f.write("egress_rid {} {}".format(egress_rid,self.edges_port[(n_list[-1],n)][0]))
                    f.write("\n")
                elif (n,n_list[-1]) in self.edges_port.keys():
                    f.write("egress_rid {} {}".format(egress_rid, self.edges_port[(n,n_list[-1])][1]))
                    f.write("\n")
                elif n==0:
                    f.write("egress_rid {} {}".format(egress_rid, 1))
                    f.write("\n")
            '''
                #####修改多播后的源目的ip  下一跳是host以及下一跳是上一跳，则原路返回

                # if n ==0 or n==n_list[len(n_list)-2]:
                #     f.write("setmultiip 1 {} => 10.0.1.{} 10.0.0.1".format(egress_rid,n_list[-1]))
                #     f.write("\n")
                # else:
                #     f.write("setmultiip 1 {} => 10.0.0.1 10.0.0.2".format(egress_rid))
                #     f.write("\n")
                # egress_rid +=1
            f.close()

if __name__ == '__main__':
    # links=[(2,3),(1,6),(3,4)]
    # paths=[[0,5, 2, 1], [0,5, 6, 1], [0,5, 2, 3], [0,5, 3, 4], [0,5, 7, 4], [0,5, 6, 7]]
    paths=[[23, 12, 13, 14, 15],[23, 12, 22],[23, 24, 13, 14, 15, 16]]
    links=[(23,12),(16,15),(14,15)]
    # # print(len(paths))
    # paths = [[23, 12, 13, 14, 15], [23, 12, 22], [23, 34, 35, 46],
    #          [23, 34, 35, 36, 37], [23, 34, 44, 43, 42], [23, 34, 44, 55], [23, 12, 1, 11, 10, 9],
    #          [23, 24, 13, 14, 15, 16], [23, 33, 32, 31, 30, 19], [23, 33, 32, 31, 30, 41], [23, 24, 35, 36, 37, 38],
    #          [23, 24, 35, 46, 47, 48], [23, 24, 13, 2, 3, 4, 5], [23, 12, 1, 2, 3, 4, 5, 6],
    #          [23, 24, 25, 26, 27, 28, 17, 6], [23, 33, 22, 21, 20, 19, 8, 7], [23, 33, 32, 31, 30, 29, 18, 7],
    #          [23, 33, 22, 11, 10, 9, 8], [23, 24, 25, 26, 27, 16, 17], [23, 24, 25, 26, 27, 28, 17, 18],
    #          [23, 33, 22, 21, 20, 19, 18], [23, 24, 25, 26, 27, 28, 29], [23, 24, 25, 26, 27, 28, 39],
    #          [23, 33, 32, 31, 30, 29, 40], [23, 24, 25, 26, 27, 38, 39, 40], [23, 24, 25, 26, 27, 38, 39, 50],
    #          [23, 33, 44, 43, 42, 41, 40, 51], [23, 34, 45, 46, 47, 48, 49], [23, 33, 44, 43, 42, 41, 52, 51],
    #          [23, 34, 45, 55, 54, 53, 52], [23, 24, 35, 46, 57, 58, 59], [23, 34, 45, 56, 57, 58, 59, 60],
    #          [23, 34, 45, 56, 66, 65, 64, 63], [23, 33, 44, 55, 66, 65, 64], [23, 24, 25, 26, 27, 16, 5, 6, 7],
    #          [23, 24, 25, 26, 27, 38, 49, 50, 51], [23, 33, 44, 55, 54, 53, 52, 51, 62],
    #          [23, 24, 25, 26, 27, 38, 49, 60, 61], [23, 33, 44, 43, 42, 41, 52, 63, 62],
    #          [23, 24, 25, 26, 27, 38, 49, 50, 61, 62]]
    # links = [(38, 39), (4, 5), (62, 61), (28, 17), (61, 50), (2, 1), (36, 35), (29, 28), (14, 15), (39, 40), (5, 6),
    #          (54, 55), (44, 43), (43, 42), (52, 51), (61, 60), (29, 18), (12, 1), (44, 34), (60, 49), (20, 19),
    #          (37, 36), (30, 29), (3, 2), (13, 12), (46, 47), (22, 21), (53, 54), (23, 24), (40, 41), (45, 46), (6, 7),
    #          (24, 25), (60, 59), (51, 50), (59, 58), (30, 19), (13, 2), (38, 27), (38, 37), (21, 20), (4, 3), (62, 63),
    #          (7, 8), (50, 49), (39, 28), (44, 33), (14, 13), (31, 30), (52, 53), (18, 19), (27, 28), (57, 56), (42, 41),
    #          (64, 63), (12, 22), (35, 46), (55, 45), (66, 56), (34, 35), (10, 11), (58, 57), (17, 16), (25, 26),
    #          (1, 11), (63, 52), (18, 17), (27, 26), (9, 10), (27, 16), (45, 34), (62, 51), (18, 7), (24, 13), (31, 32),
    #          (57, 46), (47, 48), (24, 35), (40, 51), (6, 17), (19, 8), (15, 16), (56, 45), (23, 33), (41, 52), (50, 39),
    #          (32, 33), (55, 66), (29, 40), (11, 22), (12, 23), (55, 44), (49, 38), (30, 41), (8, 9), (49, 48), (65, 64),
    #          (34, 23), (66, 65), (33, 22), (16, 5)]

    for path in paths:
        path.insert(0, 0)
    switches=66
    monitor=23
    t=table(links,paths,switches,monitor)
    t.make_res()