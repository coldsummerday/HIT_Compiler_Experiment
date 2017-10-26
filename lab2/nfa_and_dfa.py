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
    def __init__(self,name):
        super(syntree_Node,self).__init__()
        self.name = name
        self.parent = None
        self.children = []
        self.level =None
        self.flag = False
    
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
    
    