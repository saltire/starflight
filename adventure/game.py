import json


class Game:
    def __init__(self, file):
        with open(file, 'rb') as gamefile:
            data = json.load(gamefile)
        
        for var in ('rooms', 'nouns', 'vars', 'messages'):
            setattr(self, var, data.get(var, {}))
            
        self.controls = data.get('controls', [])
            
        self.vocab = set()
        for words in data.get('words', []):
            self.add_to_vocab(words)
        for noun in self.nouns:
            self.add_to_vocab(noun['words'])
            
    
    def add_to_vocab(self, words):
        words = set(words)
        for group in self.vocab:
            if group & words:
                words = group | words
                self.vocab.discard(group)
        self.vocab.add(words)
        
        
    def match_word(self, inputword, word):
        if word == '*':
            return True
        
        words = word.split('|')
        if inputword in words:
            return True
        
        for w in words:
            for group in self.vocab:
                if w in group and inputword in group:
                    return True
            
        return False
    