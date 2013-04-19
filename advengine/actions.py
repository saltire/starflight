class Actions:
    def __init__(self, game, tests):
        self.game = game
        
        
    def _show_contents(self, oid, contains_msg=None, by_name=False, recursive=True, indent=0):
        """Queue for output a list of nouns contained within a noun or room."""
        for noun in sorted(self.game.get_nouns_by_loc(oid)):
            if noun.is_visible():
                self.game.queue_output('\t' * indent + noun.name
                                           if by_name else noun.shortdesc)
                if recursive and self.game.has_contents(noun.id):
                    if contains_msg:
                        self.game.queue_message(contains_msg, {'^': '\t' * (indent + 1),
                                                               '%NOUN': noun.shortname})
                    self._show_contents(noun.id, contains_msg, by_name=True, indent=indent + 1)

    
    def a_message(self, mid):
        self.game.queue_message(mid)
    
    
    def a_pause(self):
        self.game.queue_output('PAUSE')
    
    
    def a_showdesc(self, oword=None):
        for obj in self.game.match_objects(oword):
            self.game.queue_output(obj.desc)
        
        
    def a_shownotes(self, oword=None):
        for obj in self.game.match_objects(oword):
            for mid in obj.notes:
                self.game.queue_message(mid)


    def a_showcontents(self, oword=None, contains_msg=None, by_name=False, recursive=True):
        for obj in self.game.match_objects(oword):
            self._show_contents(obj.id, contains_msg, by_name, recursive)
                
                
    def a_listcontents(self, oword=None, recursive=True):
        self.a_showcontents(oword, by_name=True, recursive=recursive)
                
                
    def a_inv(self, carry_msg, nothing_msg, wear_msg=None, contains_msg=None):
        inv = self.game.get_nouns_by_loc('INVENTORY') | self.game.get_nouns_by_loc('WORN')
        if inv:
            for noun in inv:
                self.game.queue_message(wear_msg if wear_msg
                                        and 'WORN' in self.game.get_noun_locs(noun)
                                        else carry_msg, {'%NOUN': noun.name})
                if contains_msg and self.game.has_contents(noun.id):
                    self.game.queue_message(contains_msg, {'^': '\t', '%NOUN': noun.shortname})
                    self._show_contents(noun.id, contains_msg, by_name=True, indent=1)
        else:
            self.game.queue_message(nothing_msg)
    
    
    def a_move(self, movedir):
        try:
            dest = next(dest for exitdir, dest in self.game.current_room.exits.items()
                        if self.game.match_word(movedir, exitdir))
            self.game.go_to_room(dest)
        except StopIteration:
            pass
            
            
    def a_destroy(self, nword):
        for noun in self.game.match_nouns(nword):
            self.game.destroy_noun(noun)
            
            
    def a_sendnoun(self, nword, rword):
        for noun in self.game.match_nouns(nword):
            self.game.move_noun(noun, *rword.split(','))
            
            
    def a_sendtoroom(self, nword):
        for noun in self.game.match_nouns(nword):
            self.game.move_noun(noun, self.game.current_room.id)
        
        
    def a_sendtoinv(self, nword):
        for noun in self.game.match_nouns(nword):
            self.game.move_noun(noun, 'INVENTORY')
        
        
    def a_wear(self, nword):
        for noun in self.game.match_nouns(nword):
            self.game.move_noun(noun, 'WORN')
        
        
    def a_sendtonounloc(self, nword, d_nword):
        oids = set.union(*(self.game.get_noun_locs(noun) for noun in self.game.match_nouns(d_nword)))
        for noun in self.game.match_nouns(nword):
            self.game.move_noun(noun, *oids)
            
            
    def a_sendtonoun(self, nword, d_nword):
        for noun in self.game.match_nouns(nword):
            self.game.move_noun(noun, *(noun.id for noun in self.game.match_nouns(d_nword)))
        
        
    def a_swapnouns(self, nword1, nword2):
        nouns1 = self.game.match_nouns(nword1)
        nouns2 = self.game.match_nouns(nword2)
        locs1 = set.union(*(self.game.get_noun_locs(noun) for noun in nouns1))
        locs2 = set.union(*(self.game.get_noun_locs(noun) for noun in nouns2))
        for noun in nouns1:
            self.game.move_noun(noun, *locs2)
        for noun in nouns2:
            self.game.move_noun(noun, *locs1)
            
            
    def a_setnoundesc(self, nword, mid):
        for noun in self.game.match_nouns(nword):
            noun.desc = self.messages[mid]
            
            
    def a_addnounnote(self, nword, mid):
        for noun in self.game.match_nouns(nword):
            noun.notes.append(mid)
        
        
    def a_removenounnote(self, nword, mid):
        for noun in self.game.match_nouns(nword):
            while mid in noun.notes:
                noun.notes.remove(mid)
        
        
    def a_clearnounnotes(self, nword):
        for noun in self.game.match_nouns(nword):
            del noun.notes[:]
        
        
    def a_addroomnote(self, rword, mid):
        for rid in rword.split(','):
            self.game.rooms[rid].notes.append(mid)
        
        
    def a_removeroomnote(self, rword, mid):
        for rid in rword.split(','):
            while mid in self.game.rooms[rid].notes:
                self.game.rooms[rid].notes.remove(mid)
        
        
    def a_clearroomnotes(self, rword):
        for rid in rword.split(','):
            del self.game.rooms[rid].notes[:]
            
    
    def a_setvar(self, vid, value):
        self.game.vars[vid] = value
        
    
    def a_adjustvar(self, vid, value):
        if value[0] == '+':
            self.game.vars[vid] += int(value[1:])
        elif value[0] == '-':
            self.game.vars[vid] -= int(value[1:])
        elif value[0] == '*':
            self.game.vars[vid] *= int(value[1:])
        elif value[0] == '/':
            self.game.vars[vid] /= int(value[1:])
    
