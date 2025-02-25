import queue
from Connection import connection
import threading as th

from log_init import LOGGER
from config import CONFIGS
from models.DataTypeEnum import DataType

class file:
    __sendLock = th.Event()
    def __init__(self, fileName, fileLocation, fileSizeInBytes, connectionObject, send):
        if not isinstance(connectionObject,connection):
            LOGGER.error("File object requires a connection Object")
            raise Exception("Invalid parameters to constructor")
        
        if not isinstance(send,bool):
            LOGGER.error("Requires boolean of send to create file object")
            raise Exception("Invalid parameters to constructor")
        
        self.receivingQueue = queue.Queue(1)
        self.fileName = fileName
        self.fileLocation = fileLocation
        self.fileSizeInBytes = fileSizeInBytes
        self.connection = connectionObject
        self.progress = 0.0
        self.bytesProcessed = 0
        self.file = open(fileLocation,"rb" if send==True else "wb")
        self.__sendLock.set()
        
    def unblockSend(self):
        self.__sendLock.set()
        
    def __send(self):
        while data:=self.file.read(CONFIGS.fileConfigs.chunkSize):
            self.connection.sendingQueue.put({"callback":self.unblockSend,"type":DataType.FILE, "data":data})
            self.__sendLock.clear()
            self.__sendLock.wait()
            self.bytesProcessed+=len(data)
            self.progress = self.bytesProcessed/self.fileSizeInBytes
        self.file.close()
    
    # def __receive(self,data):
        