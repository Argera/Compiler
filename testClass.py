class a(object):
    def __init__(self, x):
        self.x = x

    def __init__(self,x, y, z):
        self.y = y
        self.z  = z

    def print(self):
        print(self.x)
        print(self.y)
        print(self.z)
'''
class a_child(a):
    def __init__(self,x, y, z):
        self.y = y
        self.z  = z
        a.__init__(self, x)

    def print(self):
        print(self.x)
        print(self.y)
        print(self.z)

'''

ak = a("hi")
ak.print()

b = a("hillllllll", "kokasd", "iopj2")
b.print()
