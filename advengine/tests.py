import random



def is_filter(method):
    """Allow a test to be used as a filter for nouns. The test must take
    a single argument: an input word that could refer to a noun."""
    method.is_filter = True
    return method



class Tests:
    def __init__(self, game):
        self.game = game
        
        
    def start(self):
        return self.game.get_turn() == 0
    
    
    def input(self, *cwords):
        return self.game.input_matches(cwords)
    
    
    def var(self, vid, value):
        var = self.game.vars[vid]
        
        if value[0] == '<':
            return var < int(value[1:])
        elif value[0] == '>':
            return var > int(value[1:])
        elif value[:2] in ('>=', '=>'):
            return var >= int(value[2:])
        elif value[:2] in ('<=', '=<'):
            return var <= int(value[2:])
        else:
            return var == int(value)
    
    
    def room(self, rword):
        return any(self.game.current_room.id == rid for rid in rword.split('|'))
    
    
    def visited(self, rword):
        return any(self.game.rooms[rid].is_visited() for rid in rword.split('|'))
    
    
    def exitexists(self, direction):
        return any(self.game.match_word(direction, exitdir)
                   for exitdir in self.game.current_room.exits.iterkeys())
    
    
    def carrying(self):
        return bool(self.game.get_nouns_by_loc('INVENTORY', 'WORN'))
    
    
    def nounloc(self, nword, rword):
        return any(True for noun in self.game.match_nouns(nword)
                   for rid in rword.split('|')
                   if self.game.is_noun_at(noun, rid))
    
    
    @is_filter
    def ininv(self, nword):
        return self.nounloc(nword, 'INVENTORY|WORN')
    
    
    @is_filter
    def worn(self, nword):
        return self.nounloc(nword, 'WORN')
        
        
    @is_filter
    def inroom(self, nword):
        return self.nounloc(nword, self.game.current_room.id)
    
    
    @is_filter
    def present(self, nword):
        return bool(self.game.match_nouns(nword) & self.game.get_nouns_present())
    
    
    @is_filter
    def contained(self, nword):
        return any(True for noun in self.game.match_nouns(nword)
                   for oid in self.game.get_noun_locs(noun)
                   if oid in self.game.nouns.keys())
        
        
    @is_filter
    def somewhere(self, nword):
        return any(self.game.get_noun_locs(noun) for noun in self.game.match_nouns(nword))
    
    
    @is_filter
    def movable(self, nword):
        return any(noun.is_movable() for noun in self.game.match_nouns(nword))
    
    
    @is_filter
    def wearable(self, nword):
        return any(noun.is_wearable() for noun in self.game.match_nouns(nword))
    
    
    @is_filter
    def hasdesc(self, oword):
        return any(obj.desc for obj in self.game.match_objects(oword))
    
    
    @is_filter
    def hasnotes(self, oword):
        return any(obj.notes for obj in self.game.match_objects(oword))
    
    
    @is_filter
    def hascontents(self, oword):
        return any(self.game.get_nouns_by_loc(obj.id) for obj in self.game.match_objects(oword))
    
    
    def random(self, percent):
        return random.random() * 100 < percent
    
    
