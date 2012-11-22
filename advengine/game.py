import noun
import room


class Game:
    def __init__(self, data, state=None):
        if state is None:
            self.vars = {vid: int(value) for vid, value in data['vars'].items()}
            self.rooms = {rid: room.Room(rid, rdata) for rid, rdata in data['rooms'].items()}
            self.nouns = {nid: noun.Noun(nid, ndata) for nid, ndata in data['nouns'].items()}
    
            self.turn = 0
            self.current_room = next(rid for rid, room in self.rooms.items() if room.is_start())
            self.rooms[self.current_room].visit()
        else:
            for key in ('vars', 'turn', 'current_room'):
                setattr(self, key, state[key])
            self.rooms = {rid: room.Room(rid, rdata, state['rooms'][rid])
                          for rid, rdata in data['rooms'].items()}
            self.nouns = {nid: noun.Noun(nid, ndata, state['nouns'][nid])
                          for nid, ndata in data['nouns'].items()}
        
        
    def export_state(self):
        state = {key: getattr(self, key) for key in ('vars', 'turn', 'current_room')}
        state.update({'rooms': {rid: room.export_state() for rid, room in self.rooms.items()},
                      'nouns': {nid: noun.export_state() for nid, noun in self.nouns.items()}})
        return state
        
        
    def get_turn(self):
        return self.turn
    
    
    def increment_turn(self):
        self.turn += 1
        
        
    def get_var(self, vid):
        return self.vars.get(vid)
    
    
    def set_var(self, vid, value):
        self.vars[vid] = int(value)
        
        
    def adjust_var(self, vid, value):
        if vid in self.vars:
            if value[0] == '+':
                self.vars[vid] += int(value[1:])
            elif value[0] == '-':
                self.vars[vid] -= int(value[1:])
    
    
    def get_current_room_id(self):
        return self.current_room
    
    
    def go_to_room(self, rid):
        if rid in self.rooms:
            self.current_room = rid
            self.rooms[rid].visit()
    
    
    def get_current_room(self):
        return self.rooms[self.current_room]
    
    
    def get_room(self, rid):
        return self.rooms.get(rid)
    
    
    def get_noun(self, nid):
        return self.nouns.get(nid)
    
    
    def get_noun_list(self):
        return self.nouns.keys()
    
    
    def get_nouns_by_name(self, *word):
        return set(noun for noun in self.nouns.values() if set(word) & noun.get_words())
    
    
    def get_nouns_by_loc(self, *oid):
        return set(noun for noun in self.nouns.values() if set(oid) & noun.get_locs())
    
    
    def has_contents(self, *oid):
        return any(noun for noun in self.nouns.values() if set(oid) & noun.get_locs())
    
    
    def get_nouns_present(self):
        def get_noun_containers(noun, recursive=True):
            containers = set(self.nouns[nid] for nid in noun.get_locs() & set(self.nouns.keys()))
            return (containers if not recursive else
                    containers.union(*(get_noun_containers(cont) for cont in containers)))
        
        return set(noun for noun in self.nouns.values()
                   if (noun.get_locs().union(*(cont.get_locs() for cont in get_noun_containers(noun))) &
                       set([self.current_room, 'INVENTORY', 'WORN'])))
