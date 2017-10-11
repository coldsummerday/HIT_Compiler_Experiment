
import string
##暂时bug：无法解析代码中带中文，无界面

key_words = ["auto","break","case","char","const","continue","default",  
  
"do","double","else","enum","extern","float","for",  
  
"goto","if","int","long","register","return","short",  
  
"signed","static","sizeof","struct","switch","typedef","union",  
  
"unsigned","void","volatile","while"]

invaildchars ='@#$%^&*~'
syn = ''
index = 0
charValue=''
content = ''
stringState = 0
charState = 0
digitState = 0
lineIndex = 1
mySymbolTable = []
tokens=[]
def getMyProm(filename):
    global content
    with open(filename,'r') as file_hanlde:
        content = file_hanlde.read()
def clearComment():
    ##去除注释
    global content
    state = 0
    tempindex = -1
    for c in content:
        tempindex += 1
        if state == 0:
            if c=='/':
                state = 1
                startIndex = tempindex
        elif state==1:
            if c == '*':
                state = 2
            else:
                state = 0
        elif state ==2:
            if c=='*':
                state = 3
            else:
                pass
        elif state==3:
            if c=='/':
                endindex = tempindex +1
                comment = content[startIndex:endindex]
                tokens.append(('COMMENT',comment))
                content = content.replace(comment,'')
                tempindex = startIndex -1
                state = 0
            elif  c =='*':
                pass
            else:
                state = 2

def analysis(mystr):
    ##analysis the code,
    global _p,charValue,syn,stringState,digitState,lineIndex,charState,index
    charState = ''
    char = mystr[index]
    index += 1
    while char == ' ':
        char = mystr[index]
        index+=1
    if char in string.ascii_letters or char =='_':
        while char in string.ascii_letters or char in string.digits or char =='_' or char in invaildchars:
            charValue+=char
            char = mystr[index]
            index += 1
        index -= 1
        for invaildchar in invaildchars:
            if invaildchar in charValue:
                syn = '@-6' ##标识符含有非法字符
                break
            else:
                syn = 'ID'
        for keystring in key_words:
            if keystring == charValue:
                syn = charValue.upper()  ##关键字
                break
        if syn == "ID":
            inSymbolTable(charValue)  
    elif char=='\"':
        while char in string.ascii_letters or char in '\"% ':
            charValue += char
            if stringState ==0:
                if char=='\"':
                    stringState = 1
            elif stringState == 1:
                if char=='\"':
                    stringState = 2
            char = mystr[index]
            index += 1
        if stringState == 1:
            syn='@-2' ##字符串不封闭
            stringState = 0
        elif stringState == 2:
            stringState = 0
            syn = "STRING"
        index -=1
    elif char in string.digits:
        while char in string.digits or char =='.' or char in string.ascii_letters:
            charValue += char
            if digitState==0:
                if char == '0':
                    digitState = 1
                else:
                    digitState = 2
            elif digitState == 1:
                if char=='.':
                    digitState = 3
                else:
                    digitState = 5
            elif digitState == 2:
                if char == '.':
                    digitState = 3
            char = mystr[index]
            index += 1
        for char in string.ascii_letters:
            if char in charValue:
                syn = '@-7' #字母跟数字混合
                digitState = 0
        if syn != '@-7':
            if digitState == 5:
                syn = '@-3'##数字以0开头
                digitState = 0
            else:
                digitState = 0
                if '.' not in charValue:
                    syn = 'DIGIT'
                else:
                    if charValue.count('.') == 1:
                        syn = 'FLOAT'
                    else:
                        syn = '@-5'##浮点数含有多个点
        index -= 1
    elif char=='\'':
        while char in string.ascii_letters or char in '@#$%&*\\\'\"':
            charValue += char
            if charState == 0:
                if char=='\'':
                    charState = 1
            elif charState == 1:
                if char=='\\':
                    charState = 2
                elif  char in string.ascii_letters or char in '@#$%&*':
                    charState = 3
            elif  charState == 3:
                if char == '\'':
                    charState = 4
            char = mystr[index]
            index += 1
        index -= 1
        if charState == 4:
            syn = "character".upper()
            charState = 0
        else:
            syn ="@-4" #字符串不封闭
            charState = 0
    elif char == '<':
        charValue = char
        char = mystr[index]

        if char =='=':
            charValue += char
            index += 1
            syn = '<='
        else:
            syn='<'
    elif char=='>':
        charValue = char
        char = mystr[index]
        if char == '=':
            charValue += char
            index += 1
            syn = '>='
        else:
            syn = '>'
    elif char == '!':
        charValue = char
        char = mystr[index]
        if char=='=':
            charValue = char
            index += 1
            syn = '!='
        else:
            syn = '!'
    elif char =='+':
        charValue = char
        char = mystr[index]
        if char == '+':
            charValue += char
            index += 1
            syn = '++'
        elif char == '=':
            charValue += char
            index += 1
            syn = '+='
        else:
            syn = '+'
    elif char == '-':
        charValue = char
        char = mystr[index]
        if char=='-':
            index += 1
            charValue += char
            syn = '--'
        elif char == '=':
            index += 1
            charValue += char
            syn = '-='
        else:
            syn = '-'
    elif char == '=':
        charValue = char
        char = mystr[index]
        if char == '=':
            charValue += char
            index += 1
            syn = '=='
        else:
            syn = '='
    elif char == '&':
        charValue = char
        char = mystr[index]
        if char=='&':
            charValue += char
            index += 1
            syn = '&&'
        else:
            syn = '&'
    elif char =='|':
        charValue += char
        char = mystr[index]
        if char == '|':
            charValue += char
            index += 1
            syn = '|'
        else:
            syn = '|'
    elif char =='*':
        charValue = char
        char = mystr[index]
        if char =='*':
            charValue += char
            index += 1
            syn = '**'
        elif char == '=':
            charValue += char
            index += 1
            syn ='*='
        else:
            syn ='*'
    elif char == '/':
        charValue = char
        char = mystr[index]
        if char=='/':
            charValue += char
            index += 1
            syn = '//'
        elif char =='=':
            charValue += char
            index += 1
            syn = '/='
        else:
            syn = '/'
    elif char in "};()[]{,":
        charValue = char
        syn = char
    elif char =='\n':
        syn ='@-1' ##行数加一
         
def inSymbolTable(token):
    global mySymbolTable
    if token not in mySymbolTable:
        mySymbolTable.append(token)
if __name__=="__main__":
    getMyProm('F://code//python//test.txt')
    clearComment()
    while index!=len(content):
        analysis(content)
        if syn == '@-1':
            lineIndex += 1 #记录程序的行数
        elif syn == '@-2':
            print ('字符串 ' + charValue + ' 不封闭! Error in line ' + str(lineIndex))
        elif syn == '@-3':
            print ('数字 ' + charValue + ' 错误，不能以0开头! Error in line ' + str(lineIndex))
        elif syn == '@-4':
            print ('字符 ' + charValue + ' 不封闭! Error in line ' + str(lineIndex))
        elif syn == '@-5':
            print ('数字 ' + charValue + ' 不合法! Error in line ' + str(lineIndex))
        elif syn == '@-6':
            print ('标识符' + charValue + ' 不能包含非法字符!Error in line ' + str(lineIndex))
        elif syn == '@-7':
            print ('数字 ' + charValue + ' 不合法,包含字母! Error in line ' + str(lineIndex))
        else: #若程序中无词法错误的情况
            tokens.append((syn,charValue))
        charValue = ''
    
    for itemindex,symboitem in enumerate(mySymbolTable):
        print(str(itemindex)+'\t\t\t'+symboitem+'\n')
    for token in tokens:
        print(token[0],token[1])
        
    