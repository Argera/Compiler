
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


class Scope(object):
    def __init__ (self):
        self.entities = []
        self.nestingLevel = 0
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

class varEntity(Entity):
    def __init__(self, name, type, offset):
        Entity.__init__(self, name)
        self.type = type
        self.offset = offset

class funcEntity(Entity):
    def __init__(self, name, type):
        Entity.__init__(self, name)
        self.type = type
        self.frameLength = 12
        self.argsLists = []

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
