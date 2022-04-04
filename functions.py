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
