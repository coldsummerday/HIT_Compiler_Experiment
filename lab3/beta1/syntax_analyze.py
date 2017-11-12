#!/usr/bin/python
# -*- coding:utf-8 -*-

from nfa_and_dfa import DFA,LRDFANode,syntree_Node,Symbole,Four
from prettytable import PrettyTable
import csv
class SyntaxAnalyze(object):

    def __init__(self):
        super(SyntaxAnalyze, self).__init__()
        self.first_set = {}
        self.productions = []
        self.all_elem = set()
        self.terminate = set()
        self.noterminate = set()
        self.productions_dict = {}
        self.lr_analyze_table = {}
        self.syntree = []
        self.lex_table = ['identifier','number']
        self.dubeg = True

    def read_syntax_grammar(self, file_name):
        for line in open(file_name, 'r'):
            line = line[:-1]
            cur_left = line.split(':')[0]
            cur_right = line.split(':')[1]
            right_list = []
            if cur_right.find(' ') != -1:
                right_list = cur_right.split(' ')
            else:
                right_list.append(cur_right)
            production = {cur_left: right_list}
            self.productions.append(production)

    def get_terminate_noterminate(self):
        for production in self.productions:
            for left in production.keys():
                if left not in self.productions_dict:
                    self.productions_dict[left] = []
                self.productions_dict[left].append((
                    tuple(production[left]),
                    self.productions.index(production)))
                self.all_elem.add(left)
                self.noterminate.add(left)
                for right in production[left]:
                    self.all_elem.add(right)
        self.terminate = self.all_elem - self.noterminate

    def __get_first_set(self, cur_status, all_elem):
        if cur_status in self.first_set:
            return self.first_set[cur_status]
        all_elem.add(cur_status)
        cur_status_set = set()
        for right_list in self.productions_dict[cur_status]:
            for right in right_list[0]:
                right_set = None
                if right in all_elem:
                    continue
                if right in self.first_set:
                    right_set = self.first_set[right]
                else:
                    right_set = self.__get_first_set(right, all_elem)
                cur_status_set |= right_set
                if '$' not in right_set:
                    break
        return cur_status_set

    def init_first_set(self):
        for terminate in self.terminate:
            self.first_set[terminate] = set([terminate])
        for noterminate in self.noterminate:
            self.first_set[noterminate] = self.__get_first_set(
                noterminate, set())

    def create_lr_dfa(self):
        all_status = {}
        all_object_set = {}
        self.DFA = DFA(set())

        def create_get_lr_dfa_node(set_id):
            if set_id in all_status:
                return all_status[set_id]
            return LRDFANode(set_id=set_id)

        def expand_production(self, cur_production, ex_object_set):
            ex_object_set.add(cur_production)
            right = cur_production[2]
            point_index = cur_production[3]
            tail_set = cur_production[4]
            if point_index < len(right) and\
                    (right[point_index] in self.noterminate):
                for pro_right in self.productions_dict[right[point_index]]:
                    new_tail_set = set()
                    flag = True
                    for i in range(point_index + 1, len(right)):
                        cur_first_set = self.first_set[right[i]]
                        if '$' in cur_first_set:
                            new_tail_set = tuple(
                                set(new_tail_set) | (cur_first_set - set('$')))
                        else:
                            flag = False
                            new_tail_set = tuple(
                                set(new_tail_set) | cur_first_set)
                            break
                    if flag:
                        new_tail_set = tuple(set(new_tail_set) | set(tail_set))
                    ex_new_production = (
                        pro_right[1],
                        right[point_index], pro_right[0], 0, new_tail_set)
                    if ex_new_production not in ex_object_set:
                        ex_object_set |= expand_production(
                            self, ex_new_production, ex_object_set)
                new_ex_object_set = {}
                for eos in ex_object_set:
                    pro_key = (eos[0], eos[1], eos[2], eos[3])
                    if tuple(pro_key) not in new_ex_object_set:
                        new_ex_object_set[tuple(pro_key)] = set()
                    new_ex_object_set[pro_key] |= set(eos[4])
                ex_object_set = set()
                for key in new_ex_object_set:
                    production = (key[0], key[1], key[2], key[
                                  3], tuple(new_ex_object_set[key]))
                    ex_object_set.add(tuple(production))
            return ex_object_set

        set_id = 0
        new_node = create_get_lr_dfa_node(set_id)
        object_set = expand_production(
            self, (0, 'start1', ('start',), 0, '#'), set())
        new_node.add_object_set_by_set(object_set)
        all_object_set[tuple(object_set)] = set_id
        all_status[set_id] = new_node
        object_set_queue = list()
        object_set_queue.append(new_node)
        while object_set_queue:
            top_object_node = object_set_queue.pop(0)
            old_set = top_object_node.object_set
            old_set_id = top_object_node.set_id
            # print 'object_set_id =', old_set_id
            for cur_production in old_set:
                # print cur_production
                pro_id = cur_production[0]
                left = cur_production[1]
                right = cur_production[2]
                point_index = cur_production[3]
                tail_set = cur_production[4]
                if point_index >= len(right) or '$' in right:
                    if old_set_id not in self.lr_analyze_table:
                        self.lr_analyze_table[old_set_id] = {}
                    for tail in tail_set:
                        if tail in self.lr_analyze_table[old_set_id]:
                            print 'the grammar is not a LR(1) grammar!!!'
                            return
                        self.lr_analyze_table[old_set_id][tail] = ('r', pro_id)
                else:
                    tar_set_id = 0
                    new_production = (pro_id, left, right,
                                      point_index + 1, tail_set)
                    new_object_set = expand_production(
                        self, new_production, set())
                    if tuple(new_object_set) in all_object_set.keys():
                        tar_set_id = all_object_set[tuple(new_object_set)]
                    else:
                        set_id += 1
                        tar_set_id = set_id
                        all_object_set[tuple(new_object_set)] = set_id
                        new_node = create_get_lr_dfa_node(tar_set_id)
                        new_node.add_object_set_by_set(new_object_set)
                        all_status[tar_set_id] = new_node
                        object_set_queue.append(new_node)
                    if old_set_id not in self.lr_analyze_table:
                        self.lr_analyze_table[old_set_id] = {}
                    if right[point_index] in self.terminate:
                        self.lr_analyze_table[old_set_id][
                            right[point_index]] = ('s', tar_set_id)
                    else:
                        self.lr_analyze_table[old_set_id][
                            right[point_index]] = ('g', tar_set_id)
        self.DFA.status = all_status

    def run_on_lr_dfa(self, tokens):
        self.symbole_table = []
        self.fours = []
        status_stack = [0]
        symbol_stack = ['#']
        top = 0
        success = False
        tokens.reverse()
        tempQueue = []
        syn_nodeStack = []
        self.fourOrder = 0
        def sem_analyze(nodes):
            def findnode(name):
                for node in nodes:
                    if node.name ==name:
                        return node
                return None
            def getSymbol(symbolename):
                for symbol in self.symbole_table:
                    if symbol.identifier ==symbolename:
                        return symbol
                return None
            sem_str = ''
            for node in nodes:
                sem_str += '%s,' %node.name
            sem_str=sem_str[:len(sem_str)-1]
            
            if sem_str =='statement,type,identifier,=,number,;':
                idNode = findnode('identifier')
                typeNode = findnode('type')
                numberNode = findnode('number')
                symbol = getSymbol(idNode.token)
                if symbol:
                    four = Four(self.fourOrder,'=',numberNode.token,symbol.identifier)
                    self.fours.append(four)
                    symbol.value = numberNode.token
                else:
                    newsymbole = Symbole(idNode.token,typeNode.token,None)
                    self.symbole_table.append(newsymbole)
                    four = Four(self.fourOrder,'=',numberNode.token,newsymbole.identifier)
                    self.fours.append(four)
                self.fourOrder += 1


            
        while not success:
            top = status_stack[-1]
            #print 'token =', tokens[-1]
            # print symbol_stack
            #print symbol_stack
            if tokens[-1]['id'] in self.lr_analyze_table[top]:
                action = self.lr_analyze_table[top][tokens[-1]['id']]
                if action[0] == 's':
                    status_stack.append(action[1])
                    symbol_stack.append(tokens[-1]['id'])
                    syn_nodeStack.append(syntree_Node(tokens[-1]['id'],tokens[-1]['token'],tokens[-1]['line_num']))
                    tokens = tokens[:-1]
                    if self.dubeg:
                        print(symbol_stack)
                elif action[0] == 'r':
                    if action[1] == 0:
                        print 'Syntax anaysis successfully!'
                        success = True
                        break
                    production = self.productions[action[1]]
                    left = production.keys()[0]
                    right_len = len(production[left])
                    new_line_num = syn_nodeStack[-1].line_num
                    tokens.append({'id':left,'token':None,'line_num':new_line_num})
                    if production[left] == ['$']:
                        continue
                    for node in syn_nodeStack[-right_len:]:
                        tempQueue.append(node)
                    syn_nodeStack = syn_nodeStack[:-right_len]
                    status_stack = status_stack[:-right_len]
                    symbol_stack = symbol_stack[:-right_len]
                    if self.dubeg:
                        print(symbol_stack)
                else:
                    status_stack.append(action[1])
                    if tempQueue:
                        new_line_num = tempQueue[0].line_num
                    else:
                        new_line_num = 0
                    parentNode = syntree_Node(tokens[-1]['id'],tokens[-1]['token'],new_line_num)
                    sem_queue = [parentNode] + tempQueue
                    sem_analyze(sem_queue)
                    self.syntree.append(parentNode)
                    while(tempQueue):
                        node = tempQueue.pop(0)
                        self.syntree.append(node)
                        parentNode.addchildNode(node)
                    syn_nodeStack.append(parentNode)
                    symbol_stack.append(tokens[-1]['id'])
                    tokens = tokens[:-1]
                    if self.dubeg:
                        print(symbol_stack)
                
            else:
                print ('Syntax error in line:%s!\n' %(str(tokens[-1]['line_num'])))
                break

    def read_and_analyze(self, fileName):
        token_table = open(fileName, 'r')
        tokens = []
        for line in token_table:
            line = line[:-1]
            element = line.split(' ')
            symbol =element[1]
            line_num = element[2]
            if element[0] not in self.lex_table:
                symbol = None
            token = {'id':element[0],'token':symbol,'line_num':line_num}
            tokens.append(token)
        tokens.append({'id':'#','token':None})
        self.run_on_lr_dfa(tokens)
    def printSyn_tree(self):
        root =None
        Queue = []
        for node in self.syntree:
            if node.parent ==None:
                root = node
        if root:
            root.level = 0
            Queue.append(root)
        while Queue:
            node = Queue.pop(0)
            for child in node.children:
                child.level = node.level + 1
                Queue.append(child)
        def printnode(parentnode):
            if not parentnode.flag:
                token = ''
                if parentnode.token !=None:
                    token = '->'+parentnode.token
                print(' '*parentnode.level+parentnode.name+token)
                parentnode.flag = True
            while parentnode.children:
                childNode = parentnode.children.pop(0)
                printnode(childNode)
        printnode(root)
    def printFirst_set(self):
        table = PrettyTable(['syn','set'])
        for key in self.first_set.keys():
            firstset = self.first_set[key]
            firststr =''
            for item in firstset:
                firststr += ' %s' %(item)
            table.add_row([key,firststr])
        self.first_set_table = table
    def save_Lr_anylyze_table(self,filename):
        col_headers = sorted(list(self.noterminate | self.terminate))
        col_headers.remove('')
        csv_handle = open(filename,'w')
        f_csv = csv.writer(csv_handle)
        f_csv.writerow(['lr_table']+col_headers)
        lr_table = self.lr_analyze_table
        for key in lr_table.keys():
            templist =[]
            for item in col_headers:
                if item in lr_table[key].keys():
                    templist.append(lr_table[key][item])
                else:
                    templist.append(' ')
            f_csv.writerow([key]+templist)
        csv_handle.close()
            

if __name__=="__main__":
    syn = SyntaxAnalyze()
    syn.dubeg = False
    syn.read_syntax_grammar('sem_grammer.txt')
    syn.get_terminate_noterminate()
    print(syn.productions_dict)
    #syn.init_first_set()
    #syn.create_lr_dfa()
    #syn.save_Lr_anylyze_table('lr_table.csv')
    #syn.printFirst_set()
    #print(syn.first_set_table.get_string())
    #with open('first.txt','w') as first_handle:
        #first_handle.write(syn.first_set_table.get_string())
    #syn.read_and_analyze('token_table.txt')
    #syn.printSyn_tree()

    #print(syn.fours)

                