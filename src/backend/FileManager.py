import queue
class fileManager:
    def __init__(self):
        self.queue = queue.Queue()
        self.fileMap = {}
        