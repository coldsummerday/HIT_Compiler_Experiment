#!usr/bin/env pythpn
#! -*- coding:utf-8 -*-

class NFANode(object):
    def __init__(self,name = None,_type =0):
        super(NFANode,self).__init__()
        self.name = name 
        self._type = _type
        self.edge = {}
    def add_edge(self,alpha,target):
        if alpha not in self.edge:
            targets = set()
            targets.add(target)
            self.edge[alpha] = targets
        else:
            self.edge[alpha].add(target)

class NFA(object):
    def __init__(self,alphabets):
        super(NFA,self).__init__()
        self.status = {}
        self.alphabets = alphabets

    def get_target(self,cur_status,alpha):
        if cur_status in self.status:
            if alpha in self.status[cur_status]:
                return self.status[cur_status][alpha]
        return None
class DFANode(object):
    def __init__(self,name,_type = None):
        super(DFANode,self).__init__()
        self.name = name 
        self._type = _type
        self.edge = {}
        
    def add_edge(self,alpha,target):
        if alpha not in self.edge:
            targets = set()
            targets.add(target)
            self.edge[alpha] = targets
        else:
            self.edge[alpha].add(target)


class LRDFANode(object):
    def __init__(self,set_id):
        self.set_id = set_id
        self.object_set = set()
        self.edge = {}
    def add_object_set(self,id,left,right,index,tail):
        tmp = (id,left,right,index,tail)
        if tmp not in self.object_set:
            self.object_set.add(tmp)
    def add_object_set_by_set(self,object_set):
        self.object_set |= object_set##相交

class DFA(object):
    def __init__(self, alphabets):
        super(DFA,self).__init__()
        self.status ={}
        self.alphabets = alphabets

    def get_target(self,cur_status,alpha):
        if cur_status in self.status:
            if alpha in self.status[cur_status]:
                return self.status[cur_status][alpha]
class syntree_Node(object):
    def __init__(self,name,token = None,line_num = 0):
        super(syntree_Node,self).__init__()
        self.name = name
        self.parent = None
        self.children = []
        self.level =None
        self.flag = False
        self.value = token
        self.line_num = line_num
        self.typeflag = False
        self.widthflag = False
        self.arithmetic = False
        self.arithmetic_list = []
        self.dim = []
        self.four_list = None

    ##改变保存规约算式表达式的时候缺少一个操作值时候两个值的状态
    def addArithmetic(self,op,value,width):
        if self.arithmetic:
            self.arithmetic_list.append(Arithmetic(op,value,width))
        else:
            self.typeflag = True
            self.arithmetic = True
            self.arithmetic_list = []
            self.arithmetic_list.append(Arithmetic(op,value,width))
            self.type = 'arithmetic'
    def mergerArrayDimList(self,dim_list):
        self.dim.extend(dim_list)
    def mergeArithmetic(self,arithmetic_list):
        self.arithmetic_list.extend(arithmetic_list)
    def changeNodeType(self,type):
        self.typeflag =True
        self.type = type
    def changeNodeWidth(self,width):
        self.widthflag = True
        self.width = width
    def addchildNode(self,childNode):
        if childNode in self.children:
            return
        else:
            childNode.parent = self
            self.children.append(childNode)
    
    def __str__(self):
        nodeStr = '@'+self.name+':'
        for child in self.children:
            nodeStr+='~%s.' % (child.name+child.__str__())
        nodeStr += '$'
        return nodeStr
    def __repr__(self):
        nodeStr = '@'+self.name+':'
        for child in self.children:
            nodeStr+='~%s.' % (child.name+child.__repr__())
        nodeStr +='$'
        return nodeStr

class Four(object):
    def __init__(self,order,op,value1,value2,value3):
        super(Four,self).__init__()
        self.op = op
        self.order = order
        self.value1 = value1
        self.value2 = value2
        self.value3 = value3

    def __str__(self):
        return '(%d,%s,%s,%s,%s)' %(int(self.order),str(self.op),str(self.value1),str(self.value2),str(self.value3))

    def __repr__(self):
        return '(%d,%s,%s,%s,%s)' %(int(self.order),str(self.op),str(self.value1),str(self.value2),str(self.value3))
    
#存储代码段信息
class Four_list(object):
    def __init__(self):
        self.four_list = []
        self.tchains = []
        self.fchains = []
        self.offset = 0
        self.jump_list = []

    ##tchain 是要跳转到代码段头的四元式,fchain是跳转到四元式尾的四元式
    def addfour(self,four,flag = 'n'):
        four.order = self.offset
        self.offset+=1
        self.four_list.append(four)
        if flag == 't':
            self.tchains.append(four)
        elif flag == 'f':
            self.fchains.append(four)
    def isTchain(self):
        if len(self.tchains)>0:
            return True
        else:
            return False
    def isFchain(self):
        if len(self.fchains)>0:
            return True
        else:
            return False
    def backpatch(self,jorder,flag):
        if flag == 't':
            aimlist = self.tchains
        elif flag == 'f':
            aimlist =self.fchains
        else:
            return
        for four in aimlist:
            four.value3 = jorder
    def mergeAddOrder(self,offset):
        for four in self.four_list:
            four.order += offset
        for four in self.jumplist:
            four.value3 += offset

    def __str__(self):
        four_str = ''
        for four in self.four_list:
            four_str += '%s\n' %(str(four))
        return four_str 

    def __repr__(self):
        four_str = ''
        for four in self.four_list:
            four_str += '%s\n' %(str(four))
        return four_str 

    
            
class Symbole(object):
    def __init__(self,identifier,type,width,offset):
        self.identifier = identifier
        self.type = type
        self.width = width
        self.offset = offset
        self.arrayflag = False
        self.dim = []
    def getDepth(self):
        return len(self.dim)
    
class Arithmetic(object):
    def __init__(self,op,value,width):
        self.op = op
        self.value = value
        self.width = width

    def __str__(self):
        return '(%s,%s,%s)' %(self.op,str(self.value),str(self.width))

    def __repr__(self):
        return '(%s,%s,%s)' %(self.op,str(self.value),str(self.width))
    

class TempVariable(object):
    def __init__(self,id,offset,width):
        self.id = id 
        self.offset = offset
        self.width = width
    
    def addValue(self,value):
        self.value = value
        
'''
class SemanticNode(object):
'''
    