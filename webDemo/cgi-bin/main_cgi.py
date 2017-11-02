#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import cgi,cgitb
from syntax_analyze import SyntaxAnalyze
from lexical_analyze import LexicalAnalyze
def lex_analyze(flag):
    lex_ana = LexicalAnalyze()
    if flag == '2':
        lex_ana.debug = False
    lex_ana.read_lex_grammar('lex_grammar.txt')
    lex_ana.create_nfa()
    lex_ana.nfa_to_dfa()
    lex_ana.read_and_analyze('save.cc')
def syn_analyze():
    syn_ana = SyntaxAnalyze()
    syn_ana.dubeg = False
    syn_ana.read_syntax_grammar('syn_grammar.txt')
    syn_ana.get_terminate_noterminate()
    syn_ana.init_first_set()
    syn_ana.create_lr_dfa()
    syn_ana.printFirst_set()
    with open('first.txt','w') as first_handle:
        first_handle.write(syn_ana.first_set_table.get_string())
    syn_ana.save_Lr_anylyze_table('lr_table.csv')
    syn_ana.read_and_analyze('token_table.txt')
    syn_ana.printSyn_tree()
    

print('Content-type:text/html')
print('')
form = cgi.FieldStorage()
code = form.getvalue('code')
flag = form.getvalue('flag')
os.chdir('./cgi-bin')
with open('save.cc','w') as savefile_handle:
    savefile_handle.write(code)

if flag=='1':
    lex_analyze(flag)
if flag=='2':
    lex_analyze(flag)
    syn_analyze()


