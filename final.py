import itertools
import sys
from argparse   import ArgumentParser
#from functions import genQuad, nextQuad, newTemp, emptylist, makelist, merge, backpatch, QuadsList
#from symbolTable import *


keywords    = {"program":"programtk", "endprogram":"endprogramtk", "declarations":"declarationstk", "declare":"declaretk",
            "if":"iftk", "then":"thentk", "else":"elsetk", "endif":"endiftk", "do":"dotk", "while":"whiletk",
            "endwhile":"endwhiletk", "loop":"looptk", "endloop":"endlooptk", "exitforcase":"exitforcase",
            "endforcase":"endforcasetk", "forcase":"forcasetk","incase":"incasetk", "endincase":"endincasetk", "when":"whentk",
            "endwhen":"endwhentk", "default":"defaulttk", "enddefault":"enddefaulttk", "endfunction":"endfunctiontk", "return":"returntk",
            "in":"intk", "inout":"inouttk", "inandout":"inandouttk", "and":"andtk", "or":"ortk", "not":"nottk",
            "input":"inputtk", "print":"printtk", "function":"functiontk", "exit":"exittk", "enddowhile":"enddowhiletk"}

symbols     = {":":"colontk", ";":"qmarktk", ",":"commatk", "+":"plustk","-":"minustk", "*":"multtk", "/":"divtk",
            "(":"parenthopentk", ")":"parenthclosetk", "[":"sqbropen", "]":"sqbrclose", "<":"lessthantk",
            ">":"greaterthantk", "<>":"difftk", "<=":"lesseqtk", ">=":"greatereqtk", "=":"equaltk", ":=":"assigntk"}


class Table(object):
    def __init__ (self):
        self.scopemap = {}
        self.index = 0

    def newScope(self):
        scope = Scope()
        self.scopemap[self.index] = scope
        scope.IncreaseNestingLevel(self.index)
        self.index += 1


    def deleteScope(self):
        temp = self.scopemap.pop(self.index - 1)
        temp.DecreaseNestingLevel(self.index - 1)
        self.index -= 1


    def insertEntity(self, entity):
        self.scopemap[self.index - 1].appendEntity(entity)

    def lookUp(self, name):
        size = len(self.scopemap)
        for i in reversed (range (size)):
            for j in self.scopemap[i].entities :
                if j.name == name:
                    return j
        return None

    def FindNonLocal(self, name):
        size = len(self.scopemap)
        if size != 0 :
            size -= 1

        for i in reversed (range (size)):

            for j in self.scopemap[i].entities :

                if j.name == name:

                    return j

        return None

    def getOffset(self):
        return self.scopemap[self.index - 1].offset

    def getScope(self, name):
        size = len(self.scopemap)
        for i in reversed (range (size)):
            for j in self.scopemap[i].entities :
                if j.name == name:
                    return self.scopemap[i].nestingLevel

        return None

    def currentScope(self):
        return self.scopemap[self.index - 1].nestingLevel




token_str   = ""        # actual token
token       = ""        # token category returned by lex()
c           = ""        # lex() reads the file character by character file (c is the variable that
                        #      stores the file character read every time)
first       = True      # flag used to read the first character from file only
line        = 1
isMain      = 0
loopsList   = []
table       = Table()
FinalCode   = {}
label       = 0
argslen     = 0
start       = 0
mainLabel   = 0
jalList     = []

#-------------------------------------#
#--------- Lexical Analyzer ----------#
#-------------------------------------#
def lex():

    global c, first, token_str, line
    count = 0
    buffer = ""

    if first == True:
        c = fileIterator.__next__()
        first = False

    while str(c).isspace():
        if c == "\n":
            line += 1

        c = fileIterator.__next__()

    if str(c).isalpha():
        buffer += str(c)
        count += 1
        while True:
            c = fileIterator.__next__()
            if str(c).isalnum():
                if count < 30:
                    buffer += str(c)
                    count += 1
            else:
                if buffer in keywords:
                    token_str = buffer
                    return keywords[buffer]
                else:
                    token_str = buffer
                    return "idtk"

    if str(c).isdecimal():
        buffer += str(c)
        while True:
            c = fileIterator.__next__()
            if str(c).isdecimal():
                buffer += str(c)
            else:
                if int(buffer) > -32767 and int(buffer) < 32767:
                    token_str = buffer
                    return buffer
                else:
                    print("integer {} too big, in line {}".format(int(buffer), line))
                    sys.exit()

    if str(c) == "<":
        c = fileIterator.__next__()
        if str(c) == "=":
            token_str = "<="
            c = fileIterator.__next__()
            return symbols[token_str]
        elif str(c) == ">":
            token_str = "<>"
            c = fileIterator.__next__()
            return symbols[token_str]
        else:
            token_str = "<"
            return symbols[token_str]

    if str(c) == ">":
        c= fileIterator.__next__()
        if str(c) == "=":
            token_str = ">="
            c= fileIterator.__next__()
            return symbols[token_str]
        else:
            token_str = ">"
            return symbols[token_str]

    if str(c) == ":":
        c= fileIterator.__next__()
        if str(c) == "=":
            token_str = ":="
            c= fileIterator.__next__()
            return symbols[token_str]
        elif str(c).isspace():
            token_str = ":"
            c= fileIterator.__next__()
            return symbols[token_str]
        else:
            syntax_error("unknown symbol", line, token_str, "did you mean ':'")

    if str(c) == "/":
        c = fileIterator.__next__()
        if str(c) == "*":
            while True:
                try:
                    c = fileIterator.__next__()

                    if c == "/":
                        c = fileIterator.__next__()
                        if c == "*" or c == "/":
                            print("nested comments not alowed")
                            sys.exit()

                    if str(c) == "*":
                        c = fileIterator.__next__()
                        if str(c) == "/":
                            c = fileIterator.__next__()
                            return lex()
                        else:
                            continue

                except StopIteration:
                    syntax_error(" syntax error: comments not closing,", line, token_str, None)
                    sys.exit()


        elif str(c) == "/":
            while True:
                try:
                    c = fileIterator.__next__()
                    if c == "/":
                        c = fileIterator.__next__()
                        if c == "*" or c == "/":
                            syntax_error(" nested comments not alowed,", line, token_str, None)
                            sys.exit()

                    if str(c) == "\n":
                        c = fileIterator.__next__()
                        return lex()
                    else:
                        continue

                except StopIteration:
                    syntax_error("syntax error: comments not closing,", line, token_str, None)
                    sys.exit()

        else:
            token_str = "/"
            return symbols[token_str]

    if str(c) == "+":
        token_str = "+"
        c = fileIterator.__next__()
        return symbols[token_str]

    if str(c) == "-":
        token_str = "-"
        c= fileIterator.__next__()
        return symbols[token_str]

    if str(c) == "*":
        token_str = "*"
        c= fileIterator.__next__()
        return symbols[token_str]

    if str(c) == "/":
        token_str = "/"
        c= fileIterator.__next__()
        return symbols[token_str]

    if str(c) == "=":
        token_str = "="
        c= fileIterator.__next__()
        return symbols[token_str]

    if str(c) == ",":
        token_str = ","
        c= fileIterator.__next__()
        return symbols[token_str]

    if str(c) == ";":
        token_str = ";"
        c= fileIterator.__next__()
        return symbols[token_str]

    if str(c) == "(":
        token_str = "("
        c= fileIterator.__next__()
        return symbols[token_str]

    if str(c) == ")":
        token_str = ")"
        c = fileIterator.__next__()
        return symbols[token_str]


#-------------------------------------#
#---------- Syntactic Rules ----------#
#-------------------------------------#
def program():
    global token

    if token == "programtk":
        table.newScope()
        token = lex()
        if token == "idtk":
            name = token_str
            token = lex()
            try:
                block(name)
                if token == "endprogramtk":
                    finalCode()
                    table.deleteScope()

                else:
                    syntax_error("'endprogram' keyword expected", line, token_str, None)
            except StopIteration:
                print("'endprogram' keyword expected, recieved EOF instead")
                sys.exit()
        else:
            syntax_error("program name expected", line, token_str, None)
    else:
        syntax_error("keyword 'program' was expected", line, token_str, None)


def block(name):
    global isMain, start

    isMain += 1
    declarations()
    subprograms()
    start = len(QuadsList)
    jalList.append(start)
    genQuad("begin_block", name, "_", "_")

    statements()
    isMain -= 1

    if (isMain == 0):
        genQuad("halt", "_", "_", "_")

    genQuad("end_block", name, "_", "_")


def declarations():
    global token
    while token == "declaretk":
        token = lex()
        varlist()
        if token == "qmarktk":
            token = lex()
            pass
        else:
            syntax_error("';' expected", line, token_str, None)


def varlist():
    global token
    if token == "idtk":
        entity = varEntity(token_str, "var", table.getOffset())
        table.insertEntity(entity)
        token = lex()
        while token == "commatk":
            token = lex()
            if token == "idtk":
                entity = varEntity(token_str, "var", table.getOffset())
                table.insertEntity(entity)
                token = lex()
                pass
            else:
                syntax_error(" expected variable name", line, token_str, None)
                sys.exit()


def subprograms():
    while token == "functiontk":
        subprogram()


def subprogram():
    global token
    if token == "functiontk":
        token = lex()

        if token == "idtk":
            name = token_str
            entity = funcEntity(token_str, "func")
            table.insertEntity(entity)
            table.newScope()
            token = lex()
            funcnbody(name)

            if token == "endfunctiontk":
                entity.updateFrameLenght(table.getOffset())
                finalCode()
                table.deleteScope()
                token = lex()
                pass

            else:
                syntax_error("'function' keyword expected", line, token_str, None)
        else:
            syntax_error("function name expected", line, token_str, None)
    else:
        syntax_error("'function' keyword expected", line, token_str, None)


def funcnbody(name):
    formalpars(name)
    block(name)


def formalpars(name):
    global token
    if token == "parenthopentk":
        token = lex()
        formalparlist(name)

        if token == "parenthclosetk":
            token = lex()
            pass

        else:
            syntax_error(" ')' expected", line, token_str, None)
    else:
        syntax_error(" '(' expected", line, token_str, None)


def formalparlist(name):
    global token

    if token == "parenthclosetk":
        pass

    else:
        formalparitem(name)
        while token == "commatk":
            token = lex()
            formalparitem(name)


def formalparitem(name):
    global token
    if token == "intk":
        token = lex()

        if token == "idtk":
            entity = argparEntity(token_str, "argpar", table.getOffset(), "in")
            table.insertEntity(entity)
            arg = Argument("in", "integer")
            table.lookUp(name).argsLists.append(arg)
            token = lex()
            pass

        else:
            syntax_error("argument name expected", line, token_str, None)

    elif token == "inouttk":
        token = lex()

        if token == "idtk":
            entity = argparEntity(token_str, "argpar", table.getOffset(), "inout")
            table.insertEntity(entity)
            arg = Argument("inout", "integer")
            table.lookUp(name).argsLists.append(arg)
            token = lex()
            pass

        else:
            syntax_error("argument name expected", line, token_str, None)

    elif token == "inandouttk":
        token = lex()

        if token == "idtk":
            entity = argparEntity(token_str, "argpar", table.getOffset(), "inandout")
            table.insertEntity(entity)
            arg = Argument("inandout", "integer")
            table.lookUp(name).argsLists.append(arg)
            token = lex()
            pass

        else:
            syntax_error("argument name expected,", line, token_str, None)

    else:
        syntax_error("expected arguments evaluation parameters", line, token_str, "did you mean 'in' or 'inout' or 'inandout'")


def statements():
    global token

    statement()

    while token == "qmarktk":
        token = lex()
        statement()


def statement():
    global token

    if token == "idtk":
        temp = table.lookUp(token_str)

        if (temp == None):
            entity = tempvarEntity(token_str, "tempvar", table.getOffset())
            table.insertEntity(entity)

        temp = token_str
        token = lex()
        assignment_stat(temp)

    elif token == "iftk":
        token = lex()
        if_stat()

    elif token == "whiletk":
        token = lex()
        while_stat()

    elif token == "dotk":
        token = lex()
        do_while_stat()

    elif token == "looptk":
        token = lex()
        loop_stat()

    elif token == "exittk":
        token = lex()
        exit_stat()

    elif token == "forcasetk":
        token = lex()
        forcase_stat()

    elif token == "incasetk":
        token = lex()
        incase_stat()

    elif token == "returntk":
        token = lex()
        return_stat()


    elif token == "inputtk":
        token = lex()
        input_stat()

    elif token == "printtk":
        token = lex()
        print_stat()
    else:
        pass


def assignment_stat(id):
    global token

    if token == "assigntk":
        token = lex()
        Eplace = expression()
        genQuad(":=", Eplace, "_", id)

    else:
        syntax_error("':=' expected,", line, token_str, None)
        sys.exit()


def if_stat():
    global token

    if token == "parenthopentk":
        token = lex()
        Btrue , Bfalse = condition()

        if token == "parenthclosetk":
            token =  lex()

            if token == "thentk":
                token = lex()
                backpatch(Btrue, nextQuad())
                statements()
                ifList = makelist(nextQuad())
                genQuad("jump", "_", "_", "_")
                backpatch(Bfalse,nextQuad())
                elsepart()
                backpatch(ifList,nextQuad())

                if token == "endiftk":
                    token = lex()
                    pass

                else:
                    syntax_error("'endif' keyword expected,", line, token_str, "check for missing ';' in the above statments")

            else:
                syntax_error("'then' keyword expected,", line, token_str, None)

        else:
            syntax_error("')' expected,", line, token_str, None)

    else:
        syntax_error("'(' expected,", line, token_str, None)


def elsepart():
    global token

    if token == "elsetk":
        token = lex()
        statements()


def while_stat():
    global token

    if token == "parenthopentk":
        token = lex()
        Bquad = nextQuad()
        Btrue, Bfalse = condition()

        if token == "parenthclosetk":
            token = lex()
            backpatch(Btrue, nextQuad())
            statements()
            genQuad("jump", "_", "_", str(Bquad))
            backpatch(Bfalse, nextQuad())

            if token == "endwhiletk":
                token = lex()
                pass

            else:
                syntax_error("'endwhile' keyword expected,", line, token_str, "check for missing ';' in the above statments")

        else:
            syntax_error(" ')' expected,", line, token_str, None)

    else:
        syntax_error(" '(' expected,", line, token_str, None)


def do_while_stat():
    global token

    sQuad = nextQuad()
    statements()
    if token == "enddowhiletk":
        token = lex()

        if token == "parenthopentk":
            token = lex()
            Btrue, Bfalse = condition()
            backpatch(Bfalse,str(sQuad))
            backpatch(Btrue,nextQuad())

            if token == "parenthclosetk":
                token = lex()
                pass
            else:
                syntax_error(" ')' expected,", line, token_str, None)

        else:
            syntax_error(" '(' expected,", line, token_str, None)

    else:
        syntax_error(" 'enddowhile' keyword expected,", line, token_str, None)


def loop_stat():
    global token, loopsList

    list = []
    loopsList.append(list)
    sQuad = nextQuad()
    statements()
    genQuad("jump", "_", "_", str(sQuad))
    backpatch(loopsList[-1],nextQuad())
    loopsList.pop()

    if token == "endlooptk":
        token = lex()
        pass

    else:
        syntax_error(" 'endloop' keyword expected,", line, token_str, "check for missing ';' in the above statments")


def exit_stat():
    global loopsList

    exitlist = makelist(nextQuad())
    genQuad("jump", "_", "_", "_")
    loopsList[-1] = merge(loopsList[-1], exitlist)
    pass


def forcase_stat():
    global token

    exitlist = emptylist()
    sQuad = nextQuad()
    while token == "whentk":
        token = lex()

        if token == "parenthopentk":
            token = lex()
            Btrue,Bfalse = condition()

            if token == "parenthclosetk":
                token = lex()

                if token == "colontk":
                    token = lex()
                    backpatch(Btrue, nextQuad())
                    statements()
                    list = makelist(nextQuad())
                    genQuad("jump", "_", "_", "_")
                    exitlist = merge(exitlist,list)
                    backpatch(Bfalse, nextQuad())

                else:
                    syntax_error(" ':' expected,", line, token_str, None)

            else:
                syntax_error(" ')' expected,", line, token_str, None)

        else:
            syntax_error(" '(' expected,", line, token_str, None)

    if token == "defaulttk":
        token = lex()

        if token == "colontk":
            token = lex()
            statements()

            if token == "enddefaulttk":
                token = lex()
                genQuad("jump","_", "_",str(sQuad))

                if token == "endforcasetk":
                    token = lex()
                    backpatch(exitlist,nextQuad())
                    pass
                else:
                    syntax_error("'endforcase' keyword expected,", line, token_str, "check for missing ';' in the above statments")
            else:
                syntax_error("'enddefault' keyword expected,", line, token_str, "check for missing ';' in the above statments")
        else:
            syntax_error(" ':' expected,", line, token_str, None)
    else:
        syntax_error("'default' keyword expected,", line, token_str, None)


def incase_stat():
    global token

    flag = newTemp()
    flagQuad = nextQuad()
    genQuad(":=", "1", "_", flag)

    while token == "whentk":
        token = lex()
        condTrue, condFalse = condition()
        backpatch(condTrue,nextQuad())
        genQuad(":=", "0", "_", flag)

        if token == "colontk":
            token = lex()
            statements()
            backpatch(condFalse,nextQuad())

        else:
            syntax_error(" ':' expected,", line, token_str, None)

    genQuad("=", "0", flag, str(flagQuad))

    if token == "endincasetk":
        token = lex()
        pass

    else:
        syntax_error("'endincase' keyword expected,", line, token_str, "check for missing ';' in the above statments")


def return_stat():
    global token

    Eplace = expression()
    genQuad("retv", Eplace, "_", "_")


def print_stat():
    expression()


def input_stat():
    if token == "idtk":
        token = lex()
        pass
    else:
        syntax_error(" variable name expected,", line, token_str, None)


def actualpars():
    global token, argslen

    if token == "parenthopentk":
        token = lex()
        actualparlist()

        if token == "parenthclosetk":
            token = lex()
            w = newTemp()
            entity = tempvarEntity(w, "tempvar", table.getOffset())
            table.insertEntity(entity)
            genQuad("par", w, "RET", "_")



            return w

        else:
            syntax_error(" ')' expected,", line, token_str, None)

    else:
        syntax_error(" '(' expected,", line, token_str, None)


def actualparlist():
    global token

    if token == "parenthclosetk":
        pass

    else:
        actualparitem()
        while token == "commatk":
            token = lex()
            actualparitem()


def actualparitem():
    global token

    if token == "intk":
        token = lex()
        temp = expression()

        genQuad ("par",temp,"CV","_")


    elif token == "inouttk":
        token = lex()

        if token == "idtk":
            temp = token_str
            token = lex()
            genQuad ("par",temp,"REF","_")
            pass

        else:
            syntax_error(" variable name expected", line, token_str, None)

    elif token == "inandouttk":
        token = lex()

        if token == "idtk":
            token = lex()
            pass

        else:
            syntax_error(" variable name expected,", line, token_str, None)

    else:
        syntax_error("expected arguments evaluation parameters", line, token_str, "did you mean 'in' or 'inout' or 'inandout'")


def condition():
    global token

    Btrue, Bfalse = boolterm()
    while token == "ortk":
        backpatch(Bfalse,nextQuad())
        token = lex()
        Q2true, Q2false = boolterm()
        Btrue = merge(Btrue, Q2true)
        Bfalse = Q2false

    return Btrue, Bfalse

def boolterm():
    global token

    Qtrue, Qfalse = boolfactor()
    while token == "andtk":
        backpatch(Qtrue,nextQuad())
        token = lex()
        R2true, R2false = boolfactor()
        Qfalse = merge(Qfalse, R2false)
        Qtrue = R2true

    return Qtrue , Qfalse


def boolfactor():
    global token

    if token == "nottk":
        token = lex()

        if token == "opensqbrackettk":
            token = lex()
            condition()
            token = lex()

            if token == "closesqbrackettk":
                token = lex()
                pass

            else:
                syntax_error(" ']' expected,", line, token_str, None)

        else:
            syntax_error("'[' expected,", line, token_str, None)

    elif token == "opensqbrackettk":
        token = lex()
        condition()
        token = lex()

        if token == "closesqbrackettk":
            token = lex()
            pass

        else:
            syntax_error("']' expected", line, token, None)

    else:
        E1place = expression()
        relop = token_str
        relational_oper()
        E2place = expression()
        Rtrue = makelist(nextQuad())
        genQuad(relop, E1place, E2place, "_")
        Rfalse = makelist(nextQuad())
        genQuad("jump","_","_","_")

        return  Rtrue, Rfalse


def expression():
    global token

    Eplace = ""
    optionalsign()
    T1place = term()

    while token == "plustk" or token == "minustk":
        operator = token_str
        add_oper()
        T2place = term()
        w = newTemp()
        entity = tempvarEntity(w, "tempvar", table.getOffset())
        table.insertEntity(entity)
        genQuad(operator, T1place, T2place, w)
        T1place = w

    Eplace = T1place

    return Eplace


def term():
    global token

    F1place = factor()
    while token == "multtk" or token == "divtk":
        operator = token_str
        mul_oper()
        F2place = factor()
        w = newTemp()
        genQuad(operator, F1place, F2place, w)
        F1place = w

    Tplace = F1place

    return Tplace


def factor():
    global token

    if token.isdecimal():
        temp = token_str
        token = lex()

        return temp

    elif token == "parenthopentk":
        token = lex()
        temp = expression()

        if token == "parenthclosetk":
            token = lex()

            return temp

        else:
            syntax_error("')' expected", line, token, None)

    elif token == "idtk":
        temp_id = token_str
        token = lex()
        temp = idtail(temp_id)

        if temp == None:
            return temp_id

        else:
            return temp

    else:
        syntax_error("expected some kind of value or expression", line, token, None)


def idtail(temp_id):
    global token

    if token == "parenthopentk":
        temp = actualpars()
        genQuad("call",temp_id,"_","_")

        return temp


def relational_oper():
    global token

    if token == "equaltk":
        token = lex()
        pass

    elif token == "lesseqtk":
        token = lex()
        pass

    elif token == "greatereqtk":
        token = lex()
        pass

    elif token == "lessthantk":
        token = lex()
        pass

    elif token == "greaterthantk":
        token = lex()
        pass

    elif token == "difftk":
        token = lex()
        pass

    else:
        syntax_error("expected some kind of relational operator", line, token_str,
                        " did you mean one of '=', '<=', '>=', '<>', '<', '>' ?")


def add_oper():
    global token

    if token == "plustk":
        token = lex()
        pass

    elif token == "minustk":
        token = lex()
        pass

    else:
        syntax_error("expected addition or subrtaction operator", line, token_str, " did you mean one of '+', '-' ?")


def mul_oper():
    global token

    if token == "multtk":
        token = lex()
        pass

    elif token == "divtk":
        token = lex()
        pass

    else:
        syntax_error("expected division or multiplication operator", line, token_str, "did you mean one of '*' or  '/' ?")


def optionalsign():
    if token == "addtk" or token == "minustk":
        add_oper()


#-------------------------------------#
#------- Final Code generation -------#
#-------------------------------------#
def gnvlcode(variable):
    entityScope = table.getScope(variable)
    currentScope = table.currentScope()
    diff = currentScope - entityScope
    while (diff > 0):
        FinalCode[len(FinalCode) - 1].append(["lw ", "$t0, ","-4($sp)"])
        diff -= 1

    FinalCode[len(FinalCode) - 1].append(["addi ", "$t0, ","$t0, " ,"-{}".format(table.FindNonLocal(variable).offset)])


def loadvr(value, reg):

    if value.isdecimal():
        FinalCode[len(FinalCode) - 1].append(["li ","$t{}, ".format(reg),"{}".format(value)])

    elif (table.getScope(value) == 0 and table.lookUp(value).type == "var"):

        FinalCode[len(FinalCode) - 1].append(["lw ", "$t{}, ".format(reg), "-{}($s0)".format( table.lookUp(value).offset)])

    elif (table.lookUp(value).type == "tempvar"
            or ((table.lookUp(value).type == "argpar" and table.lookUp(value).parMode == "in") and table.getScope(value) == table.currentScope())
            or (table.lookUp(value).type == "var" and table.getScope(value) == table.currentScope())):

        FinalCode[len(FinalCode) - 1].append(["lw ", "$t{}, ".format(reg), "-{}($sp)".format(table.lookUp(value).offset)])

    elif ((table.lookUp(value).type == "argpar" and table.lookUp(value).parMode == "inout")
            and table.getScope(value) == table.currentScope()):

        FinalCode[len(FinalCode) - 1].append(["lw ", "$t0, ", "-{}($sp)".format( table.lookUp(value).offset)])
        FinalCode[len(FinalCode) - 1].append(["lw ","$t{}, ".format(reg), "($t0)"])

    elif (((table.lookUp(value).type == "argpar" and table.lookUp(value).parMode == "in")
            and table.getScope(value) < table.currentScope())
            or (table.lookUp(value).type == "var")):

        gnvlcode(value)
        FinalCode[len(FinalCode) - 1].append(["lw ","$t{}, ".format(reg), "($t0)"])

    elif ((table.lookUp(value).type == "argpar" and table.lookUp(value).parMode == "inout")
            and table.getScope(value) < table.currentScope()):

        gnvlcode(value)
        FinalCode[len(FinalCode) - 1].append(["lw ", "$t0, ", "($t0)"])
        FinalCode[len(FinalCode) - 1].append(["lw ", "$t{}, ".format(reg), "($t0)"])


def storerv(reg, value):

    if  (table.getScope(value) == 0
            and table.lookUp(value).type == "var") :

        FinalCode[len(FinalCode) - 1].append(["sw ", "$t{}, ".format(reg), "-{}($s0)".format(table.lookUp(value).offset)])

    elif (table.lookUp(value).type == "tempvar"
            or((table.lookUp(value).type == "argpar" and table.lookUp(value).parMode == "in") and table.getScope(value) == table.currentScope())
            or (table.lookUp(value).type == "var" and table.getScope(value) == table.currentScope())):

        FinalCode[len(FinalCode) - 1].append(["sw ", "$t{}, ".format(reg), "-{}($sp)".format(table.lookUp(value).offset)])

    elif ((table.lookUp(value).type == "argpar" and table.lookUp(value).parMode == "inout")
            and table.getScope(value) == table.currentScope()):

        FinalCode[len(FinalCode) - 1].append(["lw ", "$t0, ",  "-{}($sp)".format(table.lookUp(value).offset)])
        FinalCode[len(FinalCode) - 1].append(["sw ", "$t{}, ".format(reg), "($t0)"])

    elif (((table.lookUp(value).type == "argpar" and table.lookUp(value).parMode == "in") or table.getScope(value) < table.currentScope())
            or ( table.lookUp(value).type == "var" and table.getScope(value) == table.currentScope())):

        gnvlcode(value)
        FinalCode[len(FinalCode) - 1].append(["sw ", "$t{}, ".format(reg), "($t0)"])

    elif ((table.lookUp(value).type == "argpar" and table.lookUp(value).parMode == "inout")
            and table.getScope(value) < table.currentScope()):

        gnvlcode(value)
        FinalCode[len(FinalCode) - 1].append(["lw ", "$t0, ", "($t0)"] )
        FinalCode[len(FinalCode) - 1].append(["sw ", "$t{}, ".format(reg), "($t0)"])




def finalCode():

    global start, argslen, mainLabel
    i = start
    flag = 0

    while i < len(QuadsList) :
        command = QuadsList[i][0]
        FinalCode[len(FinalCode)] = []

        if (table.currentScope() == 0 and flag == 0):
            FinalCode[len(FinalCode) - 1].append( ["add ","$sp, ", "$sp, ", "{}".format(table.getOffset())] )
            FinalCode[len(FinalCode) - 1].append( ["move " ,"$s0, ", "$sp, "])
            FinalCode[len(FinalCode)] = []
            mainLabel = i
            flag =1

        if (command == "jump") :
            FinalCode[len(FinalCode) - 1].append( ["j","{}".format(QuadsList[i][3])] )


        elif(command in ["<", ">", "=", ">=", "<=", "<>"]):
            loadvr(QuadsList[i][1], 1)
            loadvr(QuadsList[i][2], 2)
            label = QuadsList[i][3]

            if(command == "="):
                FinalCode[len(FinalCode) - 1].append(["beq","$t1, ", "$t2, ","{}".format(label)])

            elif(command == "<"):
                FinalCode[len(FinalCode) - 1].append(["blt","$t1, ", "$t2, ","{}".format(label)])

            elif(command == ">"):
                FinalCode[len(FinalCode) - 1].append(["bgt","$t1, ", "$t2, ","{}".format(label)])

            elif(command == "<>"):
                FinalCode[len(FinalCode) - 1].append(["bne","$t1, ", "$t2, ","{}".format(label)])

            elif(command == "<="):
                FinalCode[len(FinalCode) - 1].append(["bge","$t1, ", "$t2, ","{}".format(label)])

            elif(command == ">="):
                FinalCode[len(FinalCode) - 1].append(["ble","$t1, ", "$t2, ","{}".format(label)])

        elif(command == ":="):
            loadvr(QuadsList[i][1], 1)
            storerv(1, QuadsList[i][3])

        elif(command in ["+", "-", "*", "/"]):
            loadvr(QuadsList[i][1], 1)
            loadvr(QuadsList[i][2], 2)

            if(command == "+"):
                FinalCode[len(FinalCode) - 1].append(["add ","$t1, ", "$t1, ", "$t2"])

            elif(command == "-"):
                FinalCode[len(FinalCode) - 1].append(["sub ","$t1, ", "$t1, ", "$t2"])

            elif(command == "*"):
                FinalCode[len(FinalCode) - 1].append(["mul ","$t1, ", "$t1, ", "$t2"])

            elif(command == "/"):
                FinalCode[len(FinalCode) - 1].append(["div ","$t1, ", "$t1, ", "$t2"])

            storerv(1, QuadsList[i][3])

        elif(command == "out"):
            pass

        elif(command == "in"):
            pass

        elif(command == "retv"):
            loadvr(QuadsList[i][1],1)
            FinalCode[len(FinalCode) - 1].append(["lw ","$t0, ", "-8($sp)"])
            FinalCode[len(FinalCode) - 1].append(["sw ", "$t1, ", "($t0)"] )

        elif(command == "par"):
            j = i
            while (QuadsList[j][0] != "call"):
                j += 1
                pass
            name = QuadsList[j][1]

            mode =  QuadsList[i][2]
            temp = QuadsList[i][1]

            if(mode == "RET"):
                FinalCode[len(FinalCode) - 1].append(["addi ","$t0, ", "$sp, ", "-{}".format(table.lookUp(QuadsList[i][1]).offset)])
                FinalCode[len(FinalCode) - 1].append(["sw ","$t0, ", "-8($fp)"])
                argslen = 0

            elif(mode == "CV"):
                if(argslen == 0):
                    FinalCode[len(FinalCode) - 1].append(["add ","$fp, ", "$sp ","-{}".format(table.lookUp(name).frameLength)])

                loadvr(temp,0)
                FinalCode[len(FinalCode) - 1].append(["sw ","$t0, ","-{}($fp)".format(12+4* argslen)])

            elif(mode == "REF"):
                if(argslen == 0):
                    FinalCode[len(FinalCode) - 1].append(["add ","$fp, ", "$sp ","-{}".format(table.lookUp(name).frameLength)])

                if table.getScope(temp) == table.currentScope() or table.lookUp(temp).parMode == "in" :
                    FinalCode[len(FinalCode) - 1].append(["add ", "$t0, ", "$s0, ","-{}".format(table.lookUp(temp).offset)])
                    FinalCode[len(FinalCode) - 1].append(["sw ","$t0, ","-{}($fp)".format(12 + 4*argslen)])

                elif table.getScope(temp) == table.currentScope() and table.lookUp(temp).parMode == "inout":
                    FinalCode[len(FinalCode) - 1].append(["lw ","$t0, ","-{}($sp)".format(table.lookUp(temp).offset)])
                    FinalCode[len(FinalCode) - 1].append(["sw ","$t0, ","-{}($fp)".format(12 + 4*argslen)])

                elif table.getScope(temp) != table.currentScope() and  table.lookUp(temp).parMode == "in" :
                    print(table.getScope(temp) , table.currentScope())
                    gnvlcode(temp)
                    FinalCode[len(FinalCode) - 1].append(["sw ","$t0, ","-{}($fp)".format(12+4* argslen)])

                elif table.getScope(temp) != table.currentScope() and  table.lookUp(temp).parMode == "inout" :
                    gnvlcode(temp)
                    FinalCode[len(FinalCode) - 1].append(["lw ","$t0, ","($t0)"])
                    FinalCode[len(FinalCode) - 1].append(["sw ","$t0, ","-{}($fp)".format(12+4* argslen)])
                argslen += 1

        elif(command == "call"):
            temp_id = QuadsList[i][1]

            k = 0
            while (k < len (jalList)):
                if (QuadsList[jalList[k]][1] == temp_id):
                    break

                k += 1

            if table.getScope(temp_id) + 1 == table.currentScope():
                FinalCode[len(FinalCode) - 1].append(["lw ","$t0, ", "-4($sp)"])
                FinalCode[len(FinalCode) - 1].append(["sw ","$t0, ", "-4($fp)"])

            else:
                FinalCode[len(FinalCode) - 1].append(["sw ","$sp, ", "-4($fp)"])

            FinalCode[len(FinalCode) - 1].append(["add ", "$sp, ", "$sp, ", "{}".format(table.lookUp(temp_id).frameLength)])
            FinalCode[len(FinalCode) - 1].append(["jal ", "L{}".format(jalList[k])])
            FinalCode[len(FinalCode) - 1].append(["addi ", "$sp, ", "$sp, ", "-{}".format(table.lookUp(temp_id).frameLength)])

        elif (command == "begin_block"):
            FinalCode[len(FinalCode) - 1].append(["sw " ,"$ra, " , "($sp)"])

        elif (command == "end_block"):
            FinalCode[len(FinalCode) - 1].append(["lw " ,"$ra, " ,"($sp)"])
            FinalCode[len(FinalCode) - 1].append(["jr " ,"$ra"])

        elif (command == "halt"):
            FinalCode[len(FinalCode) - 1].append(["li " ,"$v0, " ,"10"])
            FinalCode[len(FinalCode) - 1].append(["syscall"])
        i += 1

#-------------------------------------#
#----------- error handler -----------#
#-------------------------------------#
def syntax_error(err_text, line, buff, extra):

    print("| ===== Syntax Error =====\n|")
    print("| >> {}, in line {}".format(err_text, line))
    print("|    instead found '{}'".format(buff))
    if extra !=  None:
        print("|    {}".format(extra))

    sys.exit()

#-------------------------------------#
#---------- syntax analyzer ----------#
#-------------------------------------#
def syntax_analyzer():

    try:
        global token

        token = lex()
        program()

    except StopIteration:
        print(" recieved unexpected EOF, instead found: '{}'", line, token_str, None)

#-------------------------------------#
#----------- print to file -----------#
#-------------------------------------#
def toFile(dict):

    file = open('test.int', 'a+')
    cfile = open('ctest.c', 'w+')
    last = 0
    variables = []
    cfile.write("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")

    for i in dict:
        file.write(str(i) + ":" + ','.join(dict[i]) + '\n')

        if dict[i][0] in ["<=" ,"=" ,">=","<", ">" , "<>" ]:
            cfile.write("\tL_{}: if ({} {} {}) goto L_{};".format(i, dict[i][1], dict[i][0], dict[i][2], dict[i][3]))

        elif dict[i][0] == "jump":
            cfile.write("\tL_{}: goto L_{};".format(i, dict[i][3]))

        elif dict[i][0] in ["+", "=", "*", "-"]:
            cfile.write("\tL_{}: {} = {} {} {} ;".format(i, dict[i][3], dict[i][1], dict[i][0], dict[i][2]))
            pass
        elif dict[i][0] == ":=" :
            cfile.write("\tL_{}: {} = {};".format(i, dict[i][3], dict[i][1]))
            if dict[i][3] not in variables:
                variables.append(dict[i][3])

        last = i
        cfile.write("\n")

    cfile.write("\tL_{}: ".format(last) + "{}")
    cfile.write("\n}")
    cfile.seek(0,0)
    cfile.write("int main()\n{\n\tint " + ','.join(variables) + ";" + "\n")


#-------------------------------------#
#-------- print final to file --------#
#-------------------------------------#
def FinaltoFile(dict):

    file = open('final.asm', 'w+')
    file.write("L:\n")
    file.write("    j Lmain \n")
    for i in dict:
        if i == mainLabel :
            file.write("Lmain:\n")

        else:
            file.write("L{}:\n".format(i))

        for j in range(len(dict[i])):
            file.write("   " + ''.join(dict[i][j]) + '\n')


#-------------------------------------#
#--------- Symbol Tamble -------------#
#-------------------------------------#

class Scope(object):

    def __init__ (self):
        self.entities = []
        self.nestingLevel = 0
        self.enclosingScope = None
        self.offset = 12

    def appendEntity(self, entity):
        self.entities.append(entity)
        self.offset = self.offset + 4

    def IncreaseNestingLevel(self,index):
        self.nestingLevel = index

    def DecreaseNestingLevel(self,index):
        self.nestingLevel = index


class Entity(object):

    def __init__(self, name):
        self.name = name
        self.next = None

class varEntity(Entity):

    def __init__(self, name, type, offset):
        Entity.__init__(self, name)
        self.type = type
        self.offset = offset

class funcEntity(Entity):

    def __init__(self, name, type):
        Entity.__init__(self, name)
        self.type = type
        self.startQuad = -1
        self.frameLength = 12
        self.argsLists = []

    def update(self, start):
        self.startQuad = start

    def updateFrameLenght(self, offset):
        self.frameLength = offset


class constEntity(Entity):

    def __init__(self, name, type, value):
        Entity.__init__(self, name)
        self.type = type
        self.value = value

class tempvarEntity(Entity):

    def __init__(self, name, type, offset):
        Entity.__init__(self, name)
        self.type = type
        self.offset = offset

class argparEntity(Entity):

    def __init__(self, name, type, offset, parMode):
        Entity.__init__(self, name)
        self.parMode = parMode
        self.type = type
        self.offset = offset


class Argument(object):

    def __init__(self, parMode, type):
        self.parMode = parMode
        self.type = type
        self.next = None


#-------------------------------------#
#-----------IC functions--------------#
#-------------------------------------#

label = 0
tempVarGlobal = 0
QuadsList = {}

def genQuad( operator, x, y, z):
    global label
    List = [operator, x, y, z]
    QuadsList[label] = List
    label += 1

def nextQuad():
    global label
    return label

def newTemp():
    global tempVarGlobal
    temp = "T_{}".format(tempVarGlobal)
    tempVarGlobal += 1
    return temp

def emptylist():
    temp = []
    return temp

def makelist(label):
    temp = []
    temp.append(label)
    return temp

def merge(list1, list2):
    temp = list1 + list2
    return temp

def backpatch(list,z):
    for l in list:
        QuadsList[l][3] = str(z)


#-------------------------------------#
#---------------- main ---------------#
#-------------------------------------#


parser = ArgumentParser()
parser.add_argument("filename")
args = parser.parse_args()

if args.filename.endswith('.stl'):
    file = open(args.filename)

else:
    print("invalid file format, try again with '.stl' file")
    sys.exit()

file = open(args.filename)
fileIterator = itertools.chain.from_iterable(file)
first = True
syntax_analyzer()
toFile(QuadsList)
FinaltoFile(FinalCode)
file.close()
