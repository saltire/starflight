import random


class Tests:
    def t_start(self):
        return self.game.get_turn() == 1
    
    
    def t_input(self, *cwords):
        return (len(self.words) >= len(cwords) and
                all(self.match_word(self.words[i], cword) for i, cword in enumerate(cwords)))
    
    
    def t_var(self, vid, value):
        var = self.game.get_var(vid)
        
        if value[0] == '<':
            return var < int(value[1:])
        elif value[0] == '>':
            return var > int(value[1:])
        elif value[0] in ('>=', '=>'):
            return var >= int(value[2:])
        elif value[0] in ('<=', '=<'):
            return var <= int(value[2:])
        else:
            return var == int(value)
    
    
    def t_room(self, rword):
        return any(self.game.get_current_room_id() == rid for rid in rword.split('|'))
    
    
    def t_exitexists(self, direction):
        return any(self.match_word(direction, rexit) for rexit in self.game.get_current_room().get_exits())
    
    
    def t_nounloc(self, nword, rword):
        return any(noun for noun in self.match_nouns(nword)
                   for rid in rword.split('|') if rid in noun.get_locs())
    
    
    def t_ininv(self, nword):
        return self.t_nounloc(nword, 'INVENTORY|WORN')
    
    
    def t_worn(self, nword):
        return self.t_nounloc(nword, 'WORN')
        
        
    def t_inroom(self, nword):
        return self.t_nounloc(nword, self.game.get_current_room_id())
    
    
    def t_present(self, nword):
        return bool(self.match_nouns(nword) & self.game.get_nouns_present())
    
    
    def t_contained(self, nword):
        return any(noun for noun in self.match_nouns(nword) for loc in noun.get_locs()
                   if loc in self.game.get_noun_list())
        
        
    def t_somewhere(self, nword):
        return any(noun.get_locs() for noun in self.match_nouns(nword))
    
    
    def t_wearable(self, nword):
        return any(noun.is_wearable() for noun in self.match_nouns(nword))
    
    
    def t_random(self, percent):
        return random.random() * 100 < percent
    
    