from models.enums.CommandType import CommandType

class Command():
    def __init__(self, type:CommandType, data):
        self.type: CommandType = type
        self.data = data
        
    def to_dict(self):
        return {
            "type":self.type.value,
            "data":self.data
        }