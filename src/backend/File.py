import queue
from Connection import connection
import threading as th
import msgpack

from log_init import LOGGER
from config import CONFIGS

from models.enums.DataType import DataType
from models.enums.CommandType import CommandType
from models.Command import Command

class file:
    __sendLock = th.Event()
    __ackLock = th.Event()
    __receiveLock = th.Event()
    __sendThread = None
    __receiveThread = None
    def __init__(self, fileName: str, fileLocation: str, fileSizeInBytes: int, connectionObject: connection, send: bool, uniqueId: str):
        self.receivingQueue = queue.Queue(1)
        self.fileName: str = fileName
        self.fileLocation: str = fileLocation
        self.fileSizeInBytes: int = fileSizeInBytes
        self.connection: connection = connectionObject
        self.progress: float = 0.0
        self.bytesProcessed: int = 0
        self.file = open(fileLocation,"rb" if send==True else "wb")
        self.__sendLock.set()
        self.__receiveLock.set()
        self.uuid: str = uniqueId
        
    def unblockSend(self):
        self.__ackLock.set()
        
    def __send(self):
        try:
            while self.__sendLock.is_set():
                data=self.file.read(CONFIGS.fileConfigs.chunkSize)
                self.connection.sendingQueue.put({"type":DataType.FILE, "data":data})
                self.__ackLock.clear()
                self.__ackLock.wait()
                self.bytesProcessed+=len(data)
                self.progress = float(self.bytesProcessed)/float(self.fileSizeInBytes)
        finally:
            self.file.close()
    
    def __receive(self):
        try:
            while self.__receiveLock.is_set():
                try:
                    data = self.receivingQueue.get(timeout=1.0)
                except queue.Empty:
                    continue
                self.file.write(data)
                self.bytesProcessed+=len(data)
                self.progress = float(self.bytesProcessed)/float(self.fileSizeInBytes)
                ack = msgpack.packb(Command(CommandType.ACK_FILE, {"uuid":self.uuid}).to_dict())
                self.connection.sendingQueue.put({"type":DataType.COMMAND, "data": ack})
        finally:
            self.file.close()
            
    def startSendThread(self):
        self.__sendLock.set()
        self.__sendThread=th.Thread(target=self.__send)
        self.__sendThread.start()
        
    def __stopSendThread(self):
        self.__sendLock.clear()
        if(self.__sendThread):
            self.__sendThread.join(timeout=10.0)
            if(self.__sendThread.is_alive()):
                return False
        return True
    
    def startReceiveThread(self):
        self.__receiveLock.set()
        self.__receiveThread=th.Thread(target=self.__receive)
        self.__receiveThread.start()
        
    def __stopReceiveThread(self):
        self.__receiveLock.clear()
        if(self.__receiveThread):
            self.__receiveThread.join(timeout=10.0)
            if(self.__receiveThread.is_alive()):
                return False
        return True
    
    def closeFile(self):
        if(self.__stopSendThread() and self.__stopReceiveThread()):
            return True
        return False