"""
a synchronized dict
"""
import threading

class Dict:
    def __init__(self):
        self.lock=threading.Lock()
        self.myDict=dict()

    def put(self,key,value):
        self.lock.acquire()

        self.myDict[key]=value

        self.lock.release()
    #end put

    def get(self,key,default=None):
        self.lock.acquire()

        ret = self.myDict.get(key,default)

        self.lock.release()

        return ret
    #end get

    def keys(self):
        return self.myDict.keys()
    #end keys

    def values(self):
        return self.myDict.values()
    #end values

    # def exists(self,key):
    #     return key in self.myDict.keys()
    # #end exists