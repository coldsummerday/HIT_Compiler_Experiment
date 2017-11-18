#!/usr/bin/python
# -*- coding:utf-8 -*-

from nfa_and_dfa import *
from prettytable import PrettyTable
import csv
import copy
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
        self.sem_actions = []
        self.sem_class = None

    def read_syntax_grammar(self, file_name):
        for line in open(file_name, 'r'):
            if line[0]=='#':
                continue
            line = line[:-1]
            cur_left = line.split(':')[0]
            cur_right = line.split(':')[1]
            right_list = []
            action_list = []
            if cur_right.find('->')!=-1:
                action_str = cur_right.split('->')[1]
                action_list = action_str.split(';')
                action_list.remove('')
                cur_right = cur_right.split('->')[0]
                left_line = line.split('->')[0]
                self.sem_actions.append({left_line:action_list})
            if cur_right.find(' ') != -1:
                right_list = cur_right.split(' ')
            else:
                right_list.append(cur_right)
            production = {cur_left: right_list}
            self.productions.append(production)

    def get_terminate_noterminate(self):
        for production in self.productions:
            for left in production.keys():
                if left =='actions':
                    continue
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
        self.sem_class = SemAnalyze()
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
                    ##在语法解析的基础上做语义分析,规约生成节点的时候做出相应的语义动作
                    sem_queue = [parentNode] + tempQueue
                    self.sem_class.sem_action(sem_queue)
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
                value = ''
                if parentnode.value !=None:
                    value = '->'+parentnode.value
                print(' '*parentnode.level+parentnode.name+value)
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
        if '' in col_headers:
            col_headers.remove('')
        csv_handle = open(filename,'w')
        f_csv = csv.writer(csv_handle)
        pretty_table = PrettyTable(['lr_table']+col_headers)
        
        f_csv.writerow(['lr_table']+col_headers)
        lr_table = self.lr_analyze_table
        for key in lr_table.keys():
            templist =[]
            for item in col_headers:
                if item in lr_table[key].keys():
                    templist.append(lr_table[key][item])
                else:
                    templist.append(' ')
            pretty_table.add_row([key]+templist)
            f_csv.writerow([key]+templist)
        csv_handle.close()
        with open(filename+'.pre','w') as pre_filehandle:
            pre_filehandle.write(pretty_table.get_string())


class SemAnalyze(object):
    def __init__(self):
        self.symbole_table = []
        self.fours = []
        self.order = 0
        self.offset = 0
        self.symbole_width = {'int':4,'double':8,'char':4}
        self.compare_operator = ['<','>']
    def gen(self,order,op,value1,value2,value3):
        newFour = Four(order,op,value1,value2,value3)
        return newFour

    def printSymbole_table(self):
        table = PrettyTable(['id','type','width','offset','array_dim'])
        for symbole in self.symbole_table:
            table.add_row([symbole.identifier,symbole.type,symbole.width,str(symbole.offset),str(symbole.dim)])
        print(table)
    def isSymboleExist(self,identifier):
        for symbole in self.symbole_table:
            if symbole.identifier == identifier:
                return symbole
        return None
        
    def sem_action(self,nodes):
        parentNode = nodes[0]
        sem_str = ''
        sem_str += '%s:' %(parentNode.name)
        for node in nodes[1:]:
            sem_str += '%s ' %node.name
        sem_str=sem_str[:len(sem_str)-1]
        #print(sem_str)
        ##声明语句的语义动作
        
        if sem_str =='type:int':
            parentNode.changeNodeType('int')
            parentNode.changeNodeWidth(4)
            return
        if sem_str =='type:char':
            parentNode.changeNodeType('char')
            parentNode.changeNodeWidth(1)
            return
        if sem_str =='type:double':
            parentNode.changeNodeType('double')
            parentNode.changeNodeWidth(8)
            return
        if sem_str=='array_statement:[ number ] array_statement':
            if nodes[4].typeflag and nodes[4].widthflag:
                parentNode.changeNodeWidth(int(nodes[2].value) * nodes[4].width)
                parentNode.changeNodeType('array')
                parentNode.dim.append(int(nodes[2].value))
                parentNode.mergerArrayDimList(nodes[4].dim)
                return
            else:
                parentNode.changeNodeWidth(int(nodes[2].value))
                parentNode.changeNodeType('array')
                parentNode.dim.append(int(nodes[2].value))
                return
        if sem_str == 'type_statement:type array_statement':
            if nodes[2].typeflag:
                parentNode.changeNodeType('%s(%s)' %(nodes[1].type,nodes[2].type))
                parentNode.changeNodeWidth(nodes[2].width * nodes[1].width)
                parentNode.dim = nodes[2].dim
                return
            else:
                parentNode.changeNodeType(nodes[1].type)
                parentNode.changeNodeWidth(nodes[1].width)
                return
        if sem_str =='declaration:type_statement identifier ;':
            newsymbole = Symbole(nodes[2].value,nodes[1].type,nodes[1].width,self.offset)
            if len(nodes[1].dim)!=0:
                newsymbole.dim = nodes[1].dim
            self.symbole_table.append(newsymbole)
            self.offset += nodes[1].width
            return
        if sem_str[:9] == 'operator:':
            parentNode.value = nodes[1].name
            return
        if sem_str =='primary_expression:identifier':
            symbole=self.isSymboleExist(nodes[1].value)
            if not symbole:
                print('id:'+nodes[1].value+' not define!')
                ##变量是否出错
                return
            else:
                parentNode.value = symbole.identifier
                parentNode.changeNodeType(symbole.type)
                parentNode.changeNodeWidth(symbole.width)
                return
        if sem_str == 'primary_expression:number':
            if nodes[1].value.find('.') != -1:
                parentNode.value = float(nodes[1].value)
                parentNode.changeNodeType('double')
                parentNode.changeNodeWidth(8)
            else:
                parentNode.value = int(nodes[1].value)
                parentNode.changeNodeType('int')
                parentNode.changeNodeWidth(4)
            return
        if sem_str == 'primary_expression:( expression )':
            parentNode.value = nodes[2].value
            parentNode.changeNodeWidth(nodes[2].width)
            parentNode.changeNodeType(nodes[2].type)
            return
        if sem_str=='arithmetic_expression:operator':
            parentNode.value = nodes[1].value
            parentNode.changeNodeType('operator')
            return
        if sem_str == 'arithmetic_expression:operator primary_expression arithmetic_expression':
            if nodes[3].typeflag:
                if nodes[3].type =='arithmetic':
                    parentNode.addArithmetic(nodes[1].value,nodes[2].value,nodes[2].width)
                    parentNode.mergeArithmetic(nodes[3].arithmetic_list)
            else:
                parentNode.addArithmetic(nodes[1].value,nodes[2].value,nodes[2].width)
            return

        ##所有算式算子集结完毕,等待生成四元式
        if sem_str == 'constant_expression:primary_expression arithmetic_expression':

            #比较四元式的情况,用算式类 把所有的算子保存到List 等待if 或者while语句解决
            if nodes[2].typeflag and nodes[2].arithmetic_list[0].op in self.compare_operator:
                parentNode.changeNodeWidth(nodes[1].width)
                parentNode.addArithmetic('first',nodes[1].value,nodes[1].width)
                parentNode.mergeArithmetic(nodes[2].arithmetic_list)
                parentNode.changeNodeType('compareexpression')
                return
            if not nodes[2].typeflag:
                parentNode.changeNodeType('expression')
                parentNode.value = nodes[1].value
                parentNode.width = nodes[1].width
                return
            parentNode.changeNodeType('expression')
            ##保存代码段
            parentNode.four_list = Four_list()
            node1_width = nodes[1].width
            for Arithmetic in nodes[2].arithmetic_list:
                max_width = max(node1_width,Arithmetic.width)
                #e_str += '%s%s' %(Arithmetic.op,str(Arithmetic.value))
            lastValue = nodes[1].value
            while(nodes[2].arithmetic_list):
                arithmetic = nodes[2].arithmetic_list.pop(0)
                tempT = TempVariable('T'+str(self.offset),self.offset,max_width)
                self.symbole_table.append(Symbole(tempT.id,'temp',tempT.width,tempT.offset))
                self.offset += max_width
                newfour = self.gen(self.order,arithmetic.op,lastValue,arithmetic.value,tempT.id)
                self.order += 1
                parentNode.four_list.addfour(copy.deepcopy(newfour))
                lastValue = tempT.id
            parentNode.value = lastValue
            parentNode.changeNodeWidth(max_width)
            return
        if sem_str == 'expression:constant_expression':
            if nodes[1].typeflag and nodes[1].type == 'compareexpression':
                parentNode.changeNodeType('compareexpression')
                parentNode.value = nodes[1].value
                parentNode.changeNodeWidth(nodes[1].width)
                parentNode.arithmetic_list = nodes[1].arithmetic_list
            else:
                if nodes[1].four_list:
                    parentNode.four_list = nodes[1].four_list
                parentNode.changeNodeType('expression')
                parentNode.value = nodes[1].value
                parentNode.changeNodeWidth(nodes[1].width)
        if sem_str=='assignment_value:expression':
            if nodes[1].four_list:
                parentNode.four_list = nodes[1].four_list
            parentNode.changeNodeType('expression')
            parentNode.value = nodes[1].value
            parentNode.changeNodeWidth(nodes[1].width)
        if sem_str == 'assignment_value:identifier':
            symbole=self.isSymboleExist(nodes[1].value)
            if not symbole:
                print('id:'+nodes[1].value+' not define!')
                ##变量是否出错
                return
            else:
                parentNode.value = symbole.identifier
                parentNode.changeNodeType(symbole.type)
                parentNode.changeNodeWidth(symbole.width)
                return
        if sem_str=='assignment_init:= assignment_value':
            if nodes[2].four_list:
                parentNode.four_list = nodes[2].four_list
            ##addAri方法会改变Node的属性
            parentNode.addArithmetic('=',nodes[2].value,nodes[2].width)
            #改成正确的属性
            parentNode.changeNodeType('variable_assignment')
            return
        if sem_str == 'assignment_left:identifier assignment_array':
            symbole = self.isSymboleExist(nodes[1].value)
            if not symbole:
                print('id:'+nodes[1].value+' not define!')
                ##变量是否出错
                return
            else:
                parentNode.changeNodeWidth(symbole.width)
                parentNode.value = nodes[1].value
                if not nodes[2].typeflag:
                    parentNode.changeNodeType('identifier')
                else:
                    parentNode.changeNodeType('array')
                    parentNode.dim = nodes[2].dim
        if sem_str == 'assignment_array:[ number ] assignment_array':
            parentNode.dim.append(nodes[2].value)
            parentNode.changeNodeType('array')
            if  nodes[4].typeflag:
                parentNode.mergerArrayDimList(nodes[4].dim)
        if sem_str == 'assignment:assignment_left assignment_init ;':
            symbole=self.isSymboleExist(nodes[1].value)
            if not symbole:
                print('id:'+nodes[1].value+' not define!')
                ##变量是否出错
                return
            else:
                assignment_id = 1
                symbole_each_width = 1
                if symbole.type.find('array')!=-1:
                    symbole_type = symbole.type.split('(')[0]
                    symbole_each_width = self.symbole_width[symbole_type]
                else:
                    symbole_each_width = symbole.width
                if nodes[1].type == 'array':
                    outOfRangeFlag = isArrayOut(symbole.dim,nodes[1].dim)
                    if not outOfRangeFlag:
                        print('array %s out of range!' %(symbole.identifier))
                        return
                    else:
                        arrayOffset = 1
                        for i in nodes[1].dim:
                            arrayOffset *= int(i)
                    assignment_id = '%s(%s,%s,%d)' %(symbole.identifier,symbole.offset,arrayOffset,symbole_each_width)
                else:
                    assignment_id = symbole.identifier
                parentNode.value = symbole.identifier
                parentNode.changeNodeType(symbole.type)
                parentNode.changeNodeWidth(symbole.width)
                if nodes[2].four_list:
                    parentNode.four_list = nodes[2].four_list
                else:
                    parentNode.four_list = Four_list()
                if nodes[2].type == 'variable_assignment':
                ##简单变量赋值
                    arithmetic = nodes[2].arithmetic_list.pop()
                    tempT = TempVariable('T'+str(self.offset),self.offset,symbole.width)
                    self.symbole_table.append(Symbole(tempT.id,'temp',tempT.width,tempT.offset))
                    self.offset += symbole.width
                    if symbole_each_width < arithmetic.width:
                        ##暂时先赋值默认Number只有int 跟 double不考虑
                        newfour=self.gen(self.order,'int()',arithmetic.value,'_',tempT.id)
                        parentNode.four_list.addfour(copy.deepcopy(newfour))
                        newfour = self.gen(self.order,'=',tempT.id,'_',assignment_id)
                        parentNode.four_list.addfour(copy.deepcopy(newfour))
                    elif symbole_each_width > arithmetic.width:
                        newfour = self.gen(self.order,'double()',arithmetic.value,'_',tempT.id)
                        parentNode.four_list.addfour(copy.deepcopy(newfour))
                        newfour = self.gen(self.order,'=',tempT.id,'_',assignment_id)
                        parentNode.four_list.addfour(copy.deepcopy(newfour))
                    else:
                        newfour = self.gen(self.order,'=',arithmetic.value,'_',assignment_id)
                        parentNode.four_list.addfour(copy.deepcopy(newfour))

        if sem_str[0:10] == 'statement:':
            if nodes[1].four_list:
                parentNode.four_list = nodes[1].four_list
            parentNode.changeNodeType('statement')
            
        if sem_str=='selection_statement:if ( expression ) statement else statement':
            parentNode.four_list = Four_list()
            first_value = nodes[3].arithmetic_list.pop(0).value
            arithmetic = nodes[3].arithmetic_list.pop()
            true_jump_four = Four(self.order,'j'+arithmetic.op,first_value,arithmetic.value,0)
            false_jump_four = Four(self.order,'j','_','_',1)
            parentNode.four_list.addfour(true_jump_four)
            parentNode.four_list.addfour(false_jump_four)
            parentNode.four_list.jump_list.extend([true_jump_four,false_jump_four])
            true_jump_four.value3 = 2
            TrueStatementlength = len(nodes[5].four_list.four_list)
            false_jump_four.value3 = 2 + TrueStatementlength +1
            for four in nodes[5].four_list.four_list:
                parentNode.four_list.addfour(four)
            add_jump_four_offset(nodes[5].four_list.jump_list,2)
            parentNode.four_list.jump_list.extend(nodes[5].four_list.jump_list)
            ##表达式为真的时候运行完毕跳转
            true_statment = Four(1,'j','_','_',1)
            parentNode.four_list.addfour(true_statment)
            parentNode.four_list.jump_list.append(true_statment)
            FalseStatementLength = len(nodes[7].four_list.four_list)
            beforeLength = len(parentNode.four_list.four_list)
            for four in nodes[7].four_list.four_list:
                parentNode.four_list.addfour(four)
            add_jump_four_offset(nodes[7].four_list.jump_list,beforeLength)
            parentNode.four_list.jump_list.extend(nodes[7].four_list.jump_list)
            true_statment.value3 = parentNode.four_list.offset
        if sem_str=='statement_list:statement statement_list':
            if  nodes[2].four_list:
                nodes[1].four_list=mergeFourList(nodes[1].four_list,nodes[2].four_list)
            parentNode.four_list = nodes[1].four_list
            return
        if sem_str =='compound_statement:{ statement_list }':
            parentNode.four_list = nodes[2].four_list
            return
        
        if sem_str=='iteration_statement:while ( expression ) do statement':
            parentNode.four_list = Four_list()
            first_value = nodes[3].arithmetic_list.pop(0).value
            arithmetic = nodes[3].arithmetic_list.pop()
            true_jump_four = Four(self.order,'j'+arithmetic.op,first_value,arithmetic.value,0)
            false_jump_four = Four(self.order,'j','_','_',1)
            parentNode.four_list.addfour(true_jump_four)
            parentNode.four_list.addfour(false_jump_four)
            statement_jump_four = Four(self.order,'j','_','_',0)
            parentNode.four_list.jump_list.extend([true_jump_four,false_jump_four,statement_jump_four])
            true_jump_four.value3 = 2
            for four in nodes[6].four_list.four_list:
                parentNode.four_list.addfour(four)
            parentNode.four_list.addfour(statement_jump_four)
            false_jump_four.value3 = len(parentNode.four_list.four_list)
            parentNode.four_list.jump_list.extend(nodes[6].four_list.jump_list)
        if sem_str == 'external_declaration:statement':
            parentNode.four_list = nodes[1].four_list
            return
        
        if sem_str == 'start:external_declaration start':
            if  nodes[2].four_list:
                if not nodes[1].four_list:
                    nodes[1].four_list = Four_list()
                nodes[1].four_list=mergeFourList(nodes[1].four_list,nodes[2].four_list)
            parentNode.four_list = nodes[1].four_list
            #更新四元式表
            self.fours = nodes[1].four_list
            return
            


def mergeFourList(firstFourlist,SendFourlist):
    length = len(firstFourlist.four_list)
    for four in SendFourlist.four_list:
        firstFourlist.addfour(four)
    add_jump_four_offset(SendFourlist.jump_list,length)
    firstFourlist.jump_list.extend(SendFourlist.jump_list)
    return firstFourlist

def add_jump_four_offset(jump_four_list,offset):
    for four in jump_four_list:
        four.value3 += offset

def isArrayOut(identifyDim,nowDim):
    if len(nowDim)==1:
        width = 1
        for i in identifyDim:
            width *= i
        if width < int(nowDim[0]):
            return False
        else:
            return True  
    if len(nowDim) != len(identifyDim):
        return False
    elif len(nowDim) == len(identifyDim):
        for i in range(len(nowDim)):
            if identifyDim[i] < int(nowDim[i]):
                return False
        return True
    
        
                        

        

        
            
        
                
                
                       

        
            
        
                
        
            
            
        
           

if __name__=="__main__":
    syn = SyntaxAnalyze()
    syn.dubeg = False
    syn.read_syntax_grammar('sem_grammer.txt')
    syn.get_terminate_noterminate()
    syn.init_first_set()
    syn.create_lr_dfa()
    syn.save_Lr_anylyze_table('lr_table.csv')
    syn.printFirst_set()

    #print(syn.first_set_table.get_string())
    #with open('first.txt','w') as first_handle:
        #first_handle.write(syn.first_set_table.get_string())
    syn.read_and_analyze('token_table.txt')
    #syn.sem_class.printSymbole_table()
    #syn.printSyn_tree()

    print(syn.sem_class.fours)

                