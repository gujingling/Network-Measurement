import networkx as nx
import matplotlib.pyplot as plt
import copy
import time
from itertools import islice
import sys
###################################################
#边类
class Edge():
    def __init__(self,s,t):
        self.s=s
        self.t=t
        self.dire=0 #测量方向
        self.monitor=None
        self.probePath=[]
        self.probecost=0
        self.offer=0
#monitor类
class Monitor():
    def __init__(self,m):
        self.name=m
        self.e=[]
        self.lable=0      #0表示未开放
        self.cost=400   # 60--4；80--3
        self.paths=[]
        self.capacity=400
####################################################
# 创建拓扑
def makeTopo():
    f1=open("topy_0.txt","r")
    topolines=f1.readlines()
    for line in topolines:
        topoline=line.split('\n')[0].split(' ')
        # for i in topoline:
        #     print(i)
        try:
            if topoline[0]=='node':
                node_num =  int(topoline[1])
                # print(node_num)
                for i in range(1, node_num+1):
                    g.add_node(i)
        except:
            pass
        try:
            if topoline[0]=='SDN':
                for i in range(1,len(topoline)):
                    g.add_node(int(topoline[i]),key='SDN')
        except:
            pass
        try:
            if topoline[0]=='INT':
                for i in range(1,len(topoline)):
                    g.add_node(int(topoline[i]),key='INT')
        except:
            pass
        try:
            if topoline[0] != 'node'and topoline[0]!='SDN'and topoline[0]!='INT'and topoline[0]!=' ':
                g.add_edge(int(topoline[0]),int(topoline[1]))
        except:
            pass

    # 打印拓扑
    # pos = nx.spring_layout(g)
    # nx.draw(g, pos=pos, with_labels=True, node_size=30)
    # nx.draw_networkx_edges(g, pos=pos)
    # plt.show()

#随机生成BA、ER拓扑图
# def make_er_topy():
#     g=nx.random_graphs.erdos_renyi_graph()
###############################################################
#寻找任意两节点间的最小代价路径
def find_min_cost(n1,n2):
    try:
        paths=list(islice(nx.shortest_simple_paths(g,n1,n2),5))
    except:
        return -1,[]
    # paths=list(nx.all_simple_paths(g,n1,n2))
    # print(paths)
    pathcost = []
    for path in paths:
        # print(path)
        cost=0
        for i in range(1,len(path)):
            # print(path[i])
            if key[path[i]]=='SDN':
                cost+=1+i
            else:
                cost += 1
        # print("cost:",cost)
        pathcost.append(cost)
    # print(pathcost)
    if n1==n2:
        min_cost=0
        min_path=[]
        min_path.append(n1)
    else:
        min_cost=min(pathcost)
    # print(pathcost.index((min_cost)))
        min_path=paths[pathcost.index(min_cost)]
    return min_cost,min_path

#######################################################
#确定边的测量方向
def probe_direction(m,n1,n2,ll):
    e=(n1,n2)
    find1=find_min_cost(m,n1)
    find2= find_min_cost(m,n2)
    if find1[0]==-1 or find2[0]==-1:
        ll[e]=None
        return
    else:
        if find1[0]+len(find1[1]) <= find2[0]+len(find2[1]): ######
            ll[e].probecost=find1[0]+len(find1[1])+1
            ll[e].probePath = find1[1]
            ll[e].probePath.append(n2)
            ll[e].dire=0
        else:
            ll[e].probecost=find2[0]+len(find2[1])+1
            ll[e].probePath = find2[1]
            ll[e].probePath.append(n1)
            ll[e].dire=1
    #print("{}测量边{}，{}的代价为{}，方向为{}，路径为{}".format(m,n1,n2,ll[e].probecost,ll[e].dire,ll[e].probePath))
        return ll[e]

##########################################################
#biding 算法
class Biding:
    def __init__(self):
        self.open=[]
        self.ue=list(copy.deepcopy(g.edges))   #ue:仍未确定由哪个monitor测量的边集合
        #self.able=[1,2,3,4,5,6,7,8]
    def remove_e_from_ue(self,e):
        if e in self.ue:
            self.ue.remove(e)

    def biding_strategy(self):
        print(111111111111111)
        um=[]   #  um 为所有monitor集合
        edgelist=dict()
        # print(self.ue)
        for ii in g.edges:
            edgelist[ii] = Edge(ii[0],ii[1])
        #################################
        # for i in g.nodes:
        #     um.append(i)
        #################################
        # fat-tree

        # for i in self.able:
        #     um.append(i)
        for i in g.nodes:
            um.append(i)
        for i in range(len(um)):
            um[i]=Monitor(um[i])
        m_probecost,m_probepath= self.make_cost(edgelist)
        print("原始m_probecost:",m_probecost)
        print("原始m_probepath:", m_probepath)
            # print(um[i].e)
        # for ii in range(len(g.edges)):
        #     for m in self.um:
        #         for u, v in self.ue:
        #             probe_direction(m, u, v)
        while len(self.ue):
            print("未确定link长度",len(self.ue))
            for e in self.ue:
                edgelist[e].offer += 1
                print("{}的offer为：{}".format((edgelist[e].s,edgelist[e].t),edgelist[e].offer))
                # self.cal_e(u, v).offer+=1        #####################################################
                # print(self.cal_e(u, v).offer)
            for i in range(len(um)):
                if um[i].lable==0:
                    m_r,u_e= self.cal_ro(um[i],edgelist,m_probecost)##################################################
                    # u_e = self.calcu_ro(um[i])[1]
                    print("i:{0},m_r:{1}".format(um[i].name,m_r))
                    if m_r >= um[i].cost:
                        um[i].lable=1
                        self.open.append(um[i].name)
                        if len(u_e)<=um[i].capacity:# 如果没超出容量，直接将链路添加到m.e
                            um[i].e=copy.deepcopy(u_e)
                            print("开放{}，---111----测量链路：{}".format(um[i].name, um[i].e))
                            for u, v in u_e:
                                if um[i].capacity:
                                    self.remove_e_from_ue((u,v))
                                    # print("处理{}---------1",(u,v))
                                    um[i].capacity -=1
                                    um[i].paths.append(m_probepath[(um[i].name, u, v)])
                                    self.remove_path_e(m_probepath[(um[i].name, u, v)],um[i])
                                else:
                                    break
                        # 超出容量，选择贡献最大的链路
                        else:
                            choice_link = dict()
                            for e in u_e:
                                choice_link[e] = edgelist[e].offer - m_probecost[um[i].name, e[0], e[1]]
                            choice_link = sorted(choice_link.items(), key=lambda item: item[1], reverse=True)
                            for c in range(len(choice_link)):
                                # um[i].paths.append(m_probepath[(um[i].name,choice_link[c][0][0],choice_link[c][0][1])])
                                # print("ue和选择的link:",self.ue,choice_link[c][0])
                                #####################################开放link后删除m测量link路径上的边
                                if um[i].capacity > 0:
                                    if choice_link[c][0] in self.ue:
                                        self.remove_e_from_ue(choice_link[c][0])
                                        um[i].e.append(choice_link[c][0])
                                        um[i].capacity -= 1
                                        um[i].paths.append(
                                            m_probepath[(um[i].name, choice_link[c][0][0], choice_link[c][0][1])])
                                        self.remove_path_e(
                                            m_probepath[(um[i].name, choice_link[c][0][0], choice_link[c][0][1])],
                                            um[i])
                                else:
                                    break
                            print("{}的容量为：{}-----------11111111".format(um[i].name, um[i].capacity))
                            um[i].capacity = 0
                            print("开放{}，---222---测量链路：{}".format(um[i].name, um[i].e))
                        '''
                        else:  #超出容量，则选择最适合在m测量的链路，（选择不在m上测量时最小代价最大的链路）
                            choice_link=dict()
                            for e in u_e:
                                max_cost=999        ##########初始设置无限大的数
                                for m in um:
                                    if m.name!=um[i].name and m.capacity!=0:
                                        choice_link[e]=min(max_cost,m_probecost[m.name,e[0],e[1]])
                            choice_link=sorted(choice_link.items(),key=lambda item:item[1],reverse=True)
                            for c in range(len(choice_link)):
                                # um[i].paths.append(m_probepath[(um[i].name,choice_link[c][0][0],choice_link[c][0][1])])
                                # print("ue和选择的link:",self.ue,choice_link[c][0])
                                #####################################开放link后删除m测量link路径上的边
                                if um[i].capacity > 0:
                                    if choice_link[c][0] in self.ue:
                                        self.remove_e_from_ue(choice_link[c][0])
                                        um[i].e.append(choice_link[c][0])
                                        um[i].capacity -=1
                                        um[i].paths.append(
                                                m_probepath[(um[i].name, choice_link[c][0][0], choice_link[c][0][1])])
                                        self.remove_path_e( m_probepath[(um[i].name, choice_link[c][0][0], choice_link[c][0][1])],um[i])
                                else:
                                    break
                            print("{}的容量为：{}-----------11111111".format(um[i].name,um[i].capacity))
                            um[i].capacity=0
                            print("开放{}，---222---测量链路：{}".format(um[i].name, um[i].e))
                         '''


                        # print(um[i].name,um[i].capacity,len(self.ue))
                        ##查看剩余链路长度
                        print("ue长为-----------1111：",len(self.ue))
                       #######################   修改cost，再次判断是否有需要加入的链路  ################
                        time.sleep(0.1)
                        if um[i].capacity>0 and len(self.ue)>0:
                            print(111111111111111111111111111)
                            sys.stdout.flush()
                            m_probecost = self.update_cost(um[i],u_e, m_probecost, m_probepath,edgelist)
                            print("update_cost111//m_probecost:", m_probecost)
                            offer_e=[]
                            for e in self.ue:
                                if edgelist[e].offer>=m_probecost[um[i].name,e[0],e[1]]:
                                    offer_e.append((edgelist[e].s,edgelist[e].t))
                            if len(offer_e)<=um[i].capacity and len(offer_e)>0: #容量足够
                                # print("{}测量的paths:{}".format(um[i].name, um[i].paths))
                                print("已经开放的{}添加测量链路----------111111：{}".format(um[i].name, offer_e))
                                for s,t in offer_e:
                                    if um[i].capacity>0:
                                        print("add------>",(s,t))
                                        um[i].e.append((s,t))
                                        um[i].capacity -=1
                                        self.remove_e_from_ue((s,t))
                                        um[i].paths.append(m_probepath[(um[i].name,s,t)])
                                        self.remove_path_e(m_probepath[(um[i].name,s,t)],um[i])
                                        print("add {} finish".format((s,t)))
                                    else:
                                        break
                                m_probecost = self.update_cost(um[i],offer_e, m_probecost, m_probepath,edgelist)
                                print("update_cost2222//m_probecost:", m_probecost)
                                time.sleep(0.1)
                            elif len(offer_e)>um[i].capacity and len(offer_e)>0:   #容量不足够
                                print("容量不够了------------1111111111")
                                choice_link = dict()
                                for e in offer_e:
                                    max_cost = 999
                                    for m in um:
                                        if m.name != um[i].name and m.capacity != 0:
                                            choice_link[e] = min(max_cost, m_probecost[m.name, e[0], e[1]])
                                choice_link=sorted(choice_link.items(), key=lambda item: item[1], reverse=True)
                                print("choice_link:{},um[{}].capacity:{}".format(choice_link,i,um[i].capacity))
                                for c in range(len(choice_link)):
                                    if um[i].capacity > 0:
                                        if choice_link[c][0] in self.ue:
                                            self.remove_e_from_ue(choice_link[c][0])
                                            um[i].e.append(choice_link[c][0])
                                            um[i].capacity -=1
                                            um[i].paths.append(
                                                m_probepath[(um[i].name, choice_link[c][0][0], choice_link[c][0][1])])
                                            # um[i].paths.append(
                                            #     m_probepath[(um[i].name, choice_link[c][0][0], choice_link[c][0][1])])
                                            self.remove_path_e(
                                                m_probepath[(um[i].name, choice_link[c][0][0], choice_link[c][0][1])],
                                                um[i])
                                        print("已经开放的{}添加测量链路----------2222222：{}".format(um[i].name, choice_link[c][0]))
                                    else:
                                        break
                                um[i].capacity = 0

                elif um[i].lable==1 and um[i].capacity>0 and len(self.ue)>0:
                    offer_e = []
                    for u,v in self.ue:
                        if edgelist[(u,v)].offer>=m_probecost[um[i].name,u,v]:
                            offer_e.append((u,v))
                    if len(offer_e)<=um[i].capacity and len(offer_e)>0: #容量足够
                        print("已经开放的{}添加测量链路----------333333：{}".format(um[i].name, offer_e))
                        for s, t in offer_e:
                            if um[i].capacity>0:
                                print("去除{}".format((s,t)))
                                um[i].e.append((s, t))
                                self.remove_e_from_ue((s, t))
                                um[i].paths.append(m_probepath[(um[i].name, s, t)])
                                self.remove_path_e(m_probepath[(um[i].name, s, t)],um[i])
                                # print("um[i].paths-------2:", um[i].paths)
                                # print("m_probepath[(um[i].name, s, t)]---------2:",m_probepath[(um[i].name, s, t)])
                            else:
                                break
                        m_probecost = self.update_cost(um[i],offer_e, m_probecost, m_probepath,edgelist)
                        print("update_cost3333//m_probecost:", m_probecost)
                        time.sleep(0.1)
                    elif len(offer_e)> um[i].capacity and len(offer_e)>0:   #容量不足够
                        print("容量不够了----------------222222222")
                        choice_link = dict()
                        for e in offer_e:
                            max_cost = 999
                            for m in um:
                                if m.name != um[i].name and m.capacity != 0:
                                    choice_link[e] = min(max_cost, m_probecost[m.name, e[0], e[1]])
                        choice_link=sorted(choice_link.items(), key=lambda item: item[1], reverse=True)
                        print("choice_link:",choice_link)
                        for c in range(um[i].capacity):
                            if um[i].capacity > 0:
                                if choice_link[c][0] in self.ue:
                                    self.remove_e_from_ue(choice_link[c][0])
                                    um[i].e.append(choice_link[c][0])
                                    um[i].capacity -=1
                                    um[i].paths.append(
                                            m_probepath[(um[i].name, choice_link[c][0][0], choice_link[c][0][1])])
                                    self.remove_path_e( m_probepath[(um[i].name, choice_link[c][0][0], choice_link[c][0][1])],um[i])
                                # um[i].e.append(choice_link[c][0])
                                # self.remove_e_from_ue(choice_link[c][0])
                                print("已经开放的{}添加测量链路----------44444：{}".format(um[i].name, choice_link[c][0]))
                            else:
                                break
                        um[i].capacity = 0
        send_pack = 0
        recv_pack = 0
        all_cost=0
        all_um=[]
        for m in range(len(um)):
            if um[m].lable==1:
                all_um.append(um[m].name)
                # print("计算{}的探测路径{}".format(m,um[m].paths))
                um[m].paths=self.compute_num(um[m].paths)
                # send= self.send_num(um[m].paths)
                # recv= self.recieve_num(um[m].paths)
                cost=self.probe_cost(um[m].paths)
                print("{}开放,测量边集合：{};测量路径：{}".format(um[m].name,um[m].e,um[m].paths))
                # print("{}发包：{}；------------收包：{}".format(um[m].name,send,recv))
                print("探测代价：--------------",cost)
                # send_pack+=send
                # recv_pack+=recv
                all_cost +=cost
        print("总发包：{}----------------总收包数量：{},开放{}个：{},总探测代价：{}".format(send_pack,recv_pack,len(all_um),all_um,all_cost))
                # for u,v in um[m].e:
                 #   print("{}测量边{},{}路径：{}".format(um[m].name,u,v,edgelist[self.find_edge(list(g.edges),u,v)].probePath))

    # def find_edge(self,l,u,v):
    #     d=l.index((u,v))
    #     return d

    # def cal_e(self,u,v):
    #     e=Edge(u,v)
    #     # e.offer+=1
    #     return e
    def make_cost(self,ll):
        l=[]
        for d in g.nodes:
            for u,v in g.edges:
                l.append((d,u,v))
        probe_cost={}.fromkeys(l)
        probe_path={}.fromkeys(l)
        for m in g.nodes:
            for u,v in g.edges:
                probe_cost[(m,u,v)]= probe_direction(m,u,v,ll).probecost
                probe_path[(m,u,v)] = probe_direction(m,u,v,ll).probePath
        return probe_cost,probe_path

    def cal_ro(self,m,ll,cost):
        ro= 0
        me=[]
        for u,v in self.ue:
            # print(u,v)
            # print(i)
            # print(self.ue)
            #x=probe_direction(m.name,u,v,ll)
            # time.sleep(0.01)
            if ll[(u,v)].offer-cost[(m.name,u,v)]>0: #################################
                me.append((u,v))# 对m有贡献的边集合
                ro=ro+ ll[(u,v)].offer-cost[(m.name,u,v)]#贡献量
        return ro,me

    def update_cost(self,m,add_e,x,path,ll):
        before_me=[]
        for e in m.e:
            if e not in add_e:
                before_me.append(e)
        m_node_list=[]
        e_node_list=[]
        for u,v in before_me:
            if u not in m_node_list:
                m_node_list.append(u)
            if v not in m_node_list:
                m_node_list.append(v)
        for u,v in add_e:
            if u not in e_node_list:
                e_node_list.append(u)
            if v not in e_node_list:
                e_node_list.append(v)
        add_node_list=[]
        for n in e_node_list:
            if n not in m_node_list:
                add_node_list.append(n)
        # x=self.make_cost()
        for u,v in self.ue:
            # path[(m.name,u,v)].reverse()
            # print("path[({})的反路径-------》{}".format((m.name,u,v),path[(m.name,u,v)]))
            for n in path[(m.name,u,v)]:
                if n!=m.name:
                    if n in add_node_list and key[n]=="SDN":
                        print("由于{}已经在测量链路的节点集合{}里，更新cost".format(n, m.e))
                        print("{}是SDN节点，x[{}]由{}------>{}".format(n, (m.name, u, v), x[(m.name, u, v)],
                                                                x[(m.name, u, v)] - find_min_cost(m.name, n)[0]))
                        x[(m.name,u,v)] =probe_direction(m.name,u,v,ll).probecost-find_min_cost(m.name,n)[0]
                        break
                    if n in add_node_list and key[n]=="INT":
                        print("由于{}已经在测量链路的节点集合{}里，更新cost".format(n, m.e))
                        print("{}是int节点，x[{}]由{}------>{}".format(n, (m.name, u, v), x[(m.name, u, v)],
                                                                  probe_direction(m.name, u, v, ll).probecost -
                                                                  find_min_cost(m.name, n)[0]))
                        x[(m.name,u,v)] = probe_direction(m.name,u,v,ll).probecost- find_min_cost(m.name,n)[0]
                        break
        return x

    def compute_num(self,paths):
        ll = copy.deepcopy(paths)
        for j in range(len(paths)):
            for n in range(j + 1, len(paths)):
                # print("j:{},n:{}".format(j,n))
                length = min(len(paths[n]), len(paths[j]))
                flag = 1
                for l in range(length):
                    if paths[n][l] != paths[j][l]:
                        flag = 0
                        break
                if flag == 1:
                    if length == len(paths[n]):
                        # print("删去{}上的path:{}".format(n,paths[n]))
                        if paths[n] in ll:
                            ll.remove(paths[n])
                        # print("删除{}成功".format(paths[n]))
                    else:
                        # print("删去", paths[j])
                        if paths[j] in ll:
                            ll.remove(paths[j])
                        # print("删除{}成功".format(paths[j]))
        return ll
    def remove_path_e(self,path,m):
        for i in range(len(path)-2):
            if (path[i],path[i+1]) in self.ue and (path[i],path[i+1]) not in m.e:
                self.remove_e_from_ue((path[i],path[i+1]))
                print("{}添加测量链路----------xxxxxx：{}".format(m.name, (path[i],path[i+1])))
                m.e.append((path[i],path[i+1]))
                m.capacity-=1
                # print("done!")
            elif (path[i+1],path[i]) in self.ue and (path[i+1],path[i]) not in m.e:
                self.remove_e_from_ue((path[i+1],path[i]))
                print("{}添加测量链路----------xxxxxx：{}".format(m.name, (path[i+1], path[i])))
                m.e.append((path[i], path[i + 1]))
                m.capacity-=1
                # print("done!")
###################发包与收包的代价####################
    def send_num(self,l):
        flag = set()
        for ll in l:
            flag.add(ll[1])
        return len(flag)

    def recieve_num(self,l):
        num = 0
        if len(l[0]) > 2:
            for n in range(1, len(l[0]) - 1):
                if key[l[0][n]]=='INT':
                    continue
                else:
                    num = num + 1
        num += 1
        for i in range(1, len(l)):
            max_flag = 0
            if len(l[i]) > 2:
                for j in range(0, i):
                    flag = 0
                    length = min(len(l[i]), len(l[j]))
                    for n in range(0, length):
                        if l[j][n] == l[i][n]:
                            flag += 1
                        else:
                            break
                    max_flag = max(max_flag, flag)
                for j in range(max_flag, len(l[i]) - 1):
                    if key[l[i][j]] =='INT':
                        continue
                    else:
                        num = num + 1
            num = num + 1
        return num
####################探测代价########################
    def probe_cost(self,paths):
        cost = 0
        if len(paths[0]) > 2:
            for n in range(1, len(paths[0]) - 1):
                if key[paths[0][n]]=='INT':
                    cost += 1
                else:
                    cost += 1 + n
        cost += len(paths[0])
        # print("cost0:", cost)
        for i in range(1, len(paths)):
            max_flag = 0
            if len(paths[i]) > 2:
                for j in range(0, i):
                    flag = 0
                    length = min(len(paths[i]), len(paths[j]))
                    for n in range(0, length):
                        if paths[j][n] == paths[i][n]:
                            flag += 1
                        else:
                            break
                    max_flag = max(max_flag, flag)
                for j in range(max_flag, len(paths[i]) - 1):
                    if key[paths[i][j]]=='INT':
                        cost += 1
                    else:
                        cost += 1 + j
            cost += len(paths[i])
        return cost

if __name__=='__main__':
    # f1=open("Asnet_topy",'r')
    g = nx.Graph()
    makeTopo()
    # nx.draw(g)
    # plt.show()
    print("拓扑节点集：",g.nodes)
    print("拓扑边集：")
    #print(type(g.edges))
    print(list(g.edges)[:len(g.edges)//2])
    print(list(g.edges)[len(g.edges)//2:])
    # for i in range(0,5):
    #     print(g.edges(i),end=" ")
    # print("\n")
    # for i in range(5,10):
    #     print(g.edges(i),end=" ")
    # print("节点类型：",key)
    key=nx.get_node_attributes(g,'key')
    # print(key)
    # print(find_min_cost(2,4))
    # print(probe_direction(1,3,5,list(g.edges)).probePath)
    # print(e.dire,e.probecost,e.probePath)
    location=Biding()
    location.biding_strategy()

