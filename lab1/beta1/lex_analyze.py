#!/usr/bin/env python
#!-*- coding:utf-8 -*- 
from nfa_and_dfa import DFA,DFANode,NFA,NFANode
import string
class LexicalAnalyze(object):
    def __init__(self):
        super(LexicalAnalyze,self).__init__()
        self.productions = []
        self.key_words = {}
        self.tool_set ={}
        self.NFA = None
        self.DFA = None
        self.token_table = []
        self.limiters = {'<':'LT','>':'RT','=':'EQ','(':'LB',')':'RB','{':'LOB','}':'ROB','>=':'GE','<=':'LE'}
    def read_lex_grammar(self,filename):
        cur_left = None
        cur_right = []
        line_num = 0
        with open(filename,'r') as  file_handle:
            lines = file_handle.readlines()
        for line in lines:
            line = line.rstrip()
            index = line.find(':')
            cur_left = line[:index]
            cur_right = line[index+1:]
            line_num += 1
            if line_num < 5:
                self.tool_set[cur_left] = set(cur_right.split('|'))
                continue
            elif line_num == 5:
                for word in set(cur_right.split('|')):
                    self.key_words[word] = cur_left
                continue
            production = {}
            production['left'] = cur_left
            index = cur_right.find(' ')
            if index != -1:
                production['input'] = cur_right[0:index]
                production['right'] = cur_right[index+1:]
            else:
                production['input'] = cur_right
                production['right'] = None
            self.productions.append(production)
    def create_nfa(self):
        all_status = {}
        def get_create_nfa_node(name,_type):
            if name in all_status:
                node = all_status[name]
            else:
                node = NFANode(name = name,_type = _type)
            return node
        start_node = get_create_nfa_node('start',0)
        end_node = get_create_nfa_node('end',1)
        all_status['start'] = start_node
        all_status['end'] = end_node
        for production in self.productions:
            name = production['left']
            alpha = production['input']
            right = production['right']
            node = get_create_nfa_node(name,0)
            if right is not None:
                target_node = get_create_nfa_node(right,0)
            if alpha not in self.tool_set.keys():
                if right is None:
                    node.add_edge(alpha,'end')
                else:
                    if right in self.tool_set:
                        for value in self.tool_set[right]:
                            node.add_edge(alpha,value)
                    else:
                        node.add_edge(alpha,right)
            else:
                for value in self.tool_set[alpha]:
                    if right is None:
                        node.add_edge(value,'end')
                    else:
                        if right in self.tool_set:
                            for value in self.tool_set[right]:
                                node.add_edge(alpha,value)
                        else:
                            node.add_edge(alpha,right)
                            node.add_edge(value,right)
            all_status[name] = node
            if right is not None:
                all_status[right] = target_node

            alphabets = set()
            for i in range(ord(' '),ord('~')+1):
                alphabets.add(chr(i))
            self.NFA = NFA(alphabets)
            self.NFA.status = all_status
    def nfa_to_dfa(self):
        all_status = {}

        def get_create_dfaNode(name, _type):
            if name in all_status:
                return all_status[name]
            else:
                node = DFANode(name, _type)
            return node
        for node_name in self.NFA.status['start'].edge['$']:
            start_node = get_create_dfaNode('start', 0)
            dfa_node = get_create_dfaNode(node_name, 0)
            start_node.add_edge('$', node_name)
            all_status['start'] = start_node
            all_status[node_name] = dfa_node
            is_visit = set()
            queue = list()
            nfa_node_set = set()
            nfa_node_set.add(node_name)
            queue.append((nfa_node_set, node_name))
            while queue:
                node_name = queue.pop(0)
                top_node_name = node_name[0]
                dfa_node_name = node_name[1]
                dfa_node = get_create_dfaNode(dfa_node_name, 0)
                for alpha in self.NFA.alphabets:
                    target_set = set()
                    for nfa_node_name in top_node_name:
                        nfa_name = self.NFA.status[nfa_node_name]
                        if alpha in nfa_name.edge.keys():
                            for name in nfa_name.edge[alpha]:
                                target_set.add(name)
                    if not target_set:
                        continue
                    dfa_new_node_name = ''
                    _type = 0
                    tmp_list = list(target_set)
                    target_list = sorted(tmp_list)
                    for tar in target_list:
                        dfa_new_node_name = '%s$%s' % (dfa_new_node_name, tar)
                        _type += int(self.NFA.status[tar]._type)
                    if _type > 0:
                        _type = 1
                    dfa_new_node = get_create_dfaNode(dfa_new_node_name, _type)
                    dfa_node.add_edge(alpha, dfa_new_node_name)
                    all_status[dfa_node_name] = dfa_node
                    all_status[dfa_new_node_name] = dfa_new_node
                    if dfa_new_node_name in is_visit:
                        continue
                    else:
                        is_visit.add(dfa_new_node_name)
                        queue.append((target_set, dfa_new_node_name))
        alphabets = set()
        for i in range(ord(' '), ord('~') + 1):
            alphabets.add(chr(i))
        self.DFA = DFA(alphabets)
        self.DFA.status = all_status
    def run_on_dfa(self,line,pos):
        for dfa_name in self.DFA.status['start'].edge['$']:
            cur_pos = pos
            token = ''
            token_type = dfa_name
            child_node = self.DFA.status[dfa_name]
            while cur_pos < len(line) and line[cur_pos] in child_node.edge.keys():
                token += line[cur_pos]
                child_node = self.DFA.status[list(child_node.edge[line[cur_pos]])[0]]
                cur_pos += 1
            if child_node._type > 0:
                if token in self.key_words.keys():
                    token_type = token
                return cur_pos -1,token_type,token
        return pos,None, ''
    def read_and_analyze(self,filename):
        line_num  = 0
        lex_error = False
        for line in open(filename,'r'):
            pos = 0
            line_num += 1
            line = line.split('\n')[0]
            while pos < len(line) and not lex_error:
                while pos < len(line) and line[pos] in ['\t','\n',' ','\r']:
                    pos += 1
                if pos < len(line):
                    pos,token_type,token = self.run_on_dfa(line,pos)
                    if token_type is None:
                        print('Lexical error at line %s ,column %s' %(str(line_num),str(pos)))
                        lex_error = False
                        break
                    else:
                        if token in self.limiters:
                            token_type = token
                        self.token_table.append((token_type,token))
                    pos += 1
        if not lex_error:
            output = open('token_table.txt','w+')
            for token_type,token in self.token_table:
                type_of_token = token_type
                if token_type =='limiter' or token_type =='operator':
                    type_of_token = token
                output.write('%s %s\n' % (type_of_token, token))
            output.close()
            return True
        return False
    def printDFA(self):
        file_handle = open('dfa.txt','w')
        for key in self.DFA.status.keys():
            Value = self.DFA.status[key]
            file_handle.write(str(key)+'->:\n')
            for nodekey in Value.edge.keys():
                print(nodekey,Value.edge[nodekey])
                file_handle.write(str(nodekey)+'\t')
                file_handle.write('\n')
            
if __name__=="__main__":
    lex_ana = LexicalAnalyze()
    lex_ana.read_lex_grammar('lex_grammar.txt')
    lex_ana.create_nfa()
    lex_ana.nfa_to_dfa()
    lex_ana.read_and_analyze('test.txt')
    #lex_ana.printDFA()
    
