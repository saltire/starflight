import random



def is_filter(method):
    """Allow a test to be used as a filter for nouns. The test must take
    a single argument: an input word that could refer to a noun."""
    method.is_filter = True
    return method



class Tests:
    def __init__(self, game):
        self.game = game
        
        
    def t_start(self):
        return self.game.get_turn() == 0
    
    
    def t_input(self, *cwords):
        return self.game.input_matches(cwords)
    
    
    def t_var(self, vid, value):
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
    
    
    def t_room(self, rword):
        return any(self.game.current_room.id == rid for rid in rword.split('|'))
    
    
    def t_visited(self, rword):
        return any(self.game.rooms[rid].is_visited() for rid in rword.split('|'))
    
    
    def t_exitexists(self, direction):
        return any(self.game.match_word(direction, exitdir)
                   for exitdir in self.game.current_room.exits.iterkeys())
    
    
    def t_carrying(self):
        return bool(self.game.get_nouns_by_loc('INVENTORY', 'WORN'))
    
    
    def t_nounloc(self, nword, rword):
        return any(True for noun in self.game.match_nouns(nword)
                   for rid in rword.split('|')
                   if self.game.is_noun_at(noun, rid))
    
    
    @is_filter
    def t_ininv(self, nword):
        return self.t_nounloc(nword, 'INVENTORY|WORN')
    
    
    @is_filter
    def t_worn(self, nword):
        return self.t_nounloc(nword, 'WORN')
        
        
    @is_filter
    def t_inroom(self, nword):
        return self.t_nounloc(nword, self.game.current_room.id)
    
    
    @is_filter
    def t_present(self, nword):
        return bool(self.game.match_nouns(nword) & self.game.get_nouns_present())
    
    
    @is_filter
    def t_contained(self, nword):
        return any(True for noun in self.game.match_nouns(nword)
                   for oid in self.game.get_noun_locs(noun)
                   if oid in self.game.nouns.keys())
        
        
    @is_filter
    def t_somewhere(self, nword):
        return any(self.game.get_noun_locs(noun) for noun in self.game.match_nouns(nword))
    
    
    @is_filter
    def t_movable(self, nword):
        return any(noun.is_movable() for noun in self.game.match_nouns(nword))
    
    
    @is_filter
    def t_wearable(self, nword):
        return any(noun.is_wearable() for noun in self.game.match_nouns(nword))
    
    
    @is_filter
    def t_hasdesc(self, oword):
        return any(obj.desc for obj in self.game.match_objects(oword))
    
    
    @is_filter
    def t_hasnotes(self, oword):
        return any(obj.notes for obj in self.game.match_objects(oword))
    
    
    @is_filter
    def t_hascontents(self, oword):
        return any(self.game.get_nouns_by_loc(obj.id) for obj in self.game.match_objects(oword))
    
    
    def t_random(self, percent):
        return random.random() * 100 < percent
    
    
