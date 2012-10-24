import noun
import room


class Game:
    def __init__(self, data):
        self.vars = {vid: int(value) for vid, value in data.get('vars', {}).items()}
        self.rooms = {rid: room.Room(rid, rdata) for rid, rdata in data.get('rooms', {}).items()}
        self.nouns = {nid: noun.Noun(nid, ndata) for nid, ndata in data.get('nouns', {}).items()}

        self.turn = 0
        self.current_room = next(rid for rid, room in self.rooms.items() if room.is_start())
        
        
    def get_turn(self):
        return self.turn
    
    
    def increment_turn(self):
        self.turn += 1
        
        
    def get_var(self, vid):
        return self.vars[vid]
    
    
    def set_var(self, vid, value):
        self.vars[vid] = int(value)
        
        
    def adjust_var(self, vid, value):
        if value[0] == '+':
            self.vars[vid] += int(value[1:])
        elif value[0] == '-':
            self.vars[vid] -= int(value[1:])
    
    
    def get_current_room_id(self):
        return self.current_room
    
    
    def go_to_room(self, rid):
        self.current_room = rid
    
    
    def get_current_room(self):
        return self.rooms[self.current_room]
    
    
    def get_room(self, rid):
        return self.rooms[rid]
    
    
    def get_noun(self, nid):
        return self.nouns[nid]
    
    
    def get_noun_list(self):
        return self.nouns.keys()
    
    
    def get_nouns_by_name(self, *word):
        return set(noun for noun in self.nouns.values() if set(word) & noun.get_words())
    
    
    def get_nouns_by_loc(self, *loc):
        return set(noun for noun in self.nouns.values() if set(loc) & noun.get_locs())
    
    
    def get_nouns_present(self):
        def get_noun_containers(noun, recursive=True):
            containers = set(self.nouns[nid] for nid in noun.get_locs() & set(self.nouns.keys()))
            return (containers if not recursive else
                    containers.union(*(get_noun_containers(cont) for cont in containers)))
        
        return set(noun for noun in self.nouns.values()
                   if (noun.get_locs().union(*(cont.get_locs() for cont in get_noun_containers(noun))) &
                       set([self.current_room, 'INVENTORY', 'WORN'])))