import json


class Game:
    def __init__(self, file):
        with open(file, 'rb') as gamefile:
            data = json.load(gamefile)
        
        for var in ('rooms', 'nouns', 'vars', 'words', 'messages', 'controls'):
            setattr(self, var, data.get(var))
        
        
    