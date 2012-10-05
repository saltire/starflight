import json

import noun
import room


class GameData:
    def __init__(self, gamepath):
        with open(gamepath, 'rb') as gamefile:
            self.data = json.load(gamefile)
        
        self.nouns = {nid: noun.Noun(ndata) for nid, ndata in self.data.get('nouns', {}).items()}
        self.rooms = {rid: room.Room(rdata) for rid, rdata in self.data.get('rooms', {}).items()}
            
            
    def get_controls(self):
        return self.data.get('controls', [])
    
    
    def get_messages(self):
        return self.data.get('messages', {})
    
    
    def get_vocab(self):
        def add_to_vocab(vocab, words):
            words = set(words)
            for group in [group for group in vocab if group & words]:
                words = group | words
                vocab.remove(group)
            if words:
                vocab.append(words)
            return vocab

        vocab = []
        for words in self.data.get('words', []):
            add_to_vocab(vocab, words)
        for nounobj in self.nouns.values():
            add_to_vocab(vocab, nounobj.get_words())
            
        return vocab
    
    
    def get_initial_room(self):
        return next(rid for rid, room in self.rooms.items() if room.is_start())
    
    
    def get_initial_vars(self):
        return self.data.get('vars', {})
    
    
    def get_initial_noun_locs(self):
        return {nid: noun.get_initial_locs() for nid, noun in self.nouns.items()}
    
        
    def get_room(self, rid):
        return self.rooms[rid]