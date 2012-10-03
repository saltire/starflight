import json

import noun
import room


class GameData:
    def __init__(self, gamepath):
        with open(gamepath, 'rb') as gamefile:
            self.data = json.load(gamefile)
        
        self.messages = self.data.get('messages', {})
        self.nouns = {nid: noun.Noun(ndata) for nid, ndata in self.data.get('nouns', {}).items()}
        self.rooms = {rid: room.Room(rdata) for rid, rdata in self.data.get('rooms', {}).items()}
            
        self.vocab = []
        for words in self.data.get('words', []):
            self.add_to_vocab(words)
        for nounobj in self.nouns.values():
            self.add_to_vocab(nounobj.get_words())
            
            
    def get_controls(self):
        return self.data.get('controls', [])
    
    
    def get_message(self, mid):
        return self.messages[mid]
    
    
    def get_initial_room(self):
        return next(room for room in self.rooms.values() if room.is_start())
    
    
    def get_initial_vars(self):
        return self.data.get('vars', {})
    
    
    def add_to_vocab(self, words):
        words = set(words)
        for group in [group for group in self.vocab if group & words]:
            words = group | words
            self.vocab.remove(group)
        if words:
            self.vocab.append(words)
        
        
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
    