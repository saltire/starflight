class Actions:
    def show_contents(self, oid, contains_msg=None, by_name=False, recursive=True, indent=0):
        """Queue for output a list of nouns contained within a noun or room."""
        for noun in sorted(self.game.get_nouns_by_loc(oid)):
            if noun.is_visible():
                self.queue_raw_output('\t' * indent +
                                      noun.get_name() if by_name else noun.get_short_desc())
                if recursive and self.game.has_contents(noun.get_id()):
                    if contains_msg:
                        self.queue_message(contains_msg, {'^': '\t' * (indent + 1), '%NOUN': noun.get_short_name()})
                    self.show_contents(noun.get_id(), contains_msg, by_name=True, indent=indent + 1)

    
    def a_message(self, mid):
        self.queue_message(mid)
    
    
    def a_pause(self):
        self.queue_raw_output('PAUSE')
    
    
    def a_showdesc(self, oword=None):
        for obj in self.match_objects(oword):
            self.queue_raw_output(obj.get_description())
        
        
    def a_shownotes(self, oword=None):
        for obj in self.match_objects(oword):
            for mid in obj.get_notes():
                self.queue_message(mid)


    def a_showcontents(self, oword=None, contains_msg=None, by_name=False, recursive=True):
        for obj in self.match_objects(oword):
            self.show_contents(obj.get_id(), contains_msg, by_name, recursive)
                
                
    def a_listcontents(self, oword=None, recursive=True):
        self.a_showcontents(oword, by_name=True, recursive=recursive)
                
                
    def a_inv(self, carry_msg, wear_msg=None, contains_msg=None):
        inv = self.game.get_nouns_by_loc('INVENTORY') | self.game.get_nouns_by_loc('WORN')
        if inv:
            for noun in inv:
                self.queue_message(wear_msg if wear_msg and 'WORN' in noun.get_locs() else carry_msg,
                                   {'%NOUN': noun.get_name()})
                if contains_msg and self.game.has_contents(noun.get_id()):
                    self.queue_message(contains_msg, {'^': '\t', '%NOUN': noun.get_short_name()})
                    self.show_contents(noun.get_id(), contains_msg, by_name=True, indent=1)
    
    
    def a_move(self, movedir):
        try:
            dest = next(dest for exitdir, dest in self.game.get_current_room().get_exits().items()
                        if self.match_word(movedir, exitdir))
            self.game.go_to_room(dest)
            self.a_look()
        except:
            pass
            
            
    def a_destroy(self, nword):
        for noun in self.match_nouns(nword):
            noun.clear_locs()
            
            
    def a_sendnoun(self, nword, rword):
        for noun in self.match_nouns(nword):
            noun.set_loc(*rword.split(','))
            
            
    def a_sendtoroom(self, nword):
        self.a_sendnoun(nword, self.game.get_current_room_id())
        
        
    def a_sendtoinv(self, nword):
        self.a_sendnoun(nword, 'INVENTORY')
        
        
    def a_wear(self, nword):
        self.a_sendnoun(nword, 'WORN')
        
        
    def a_sendtonounloc(self, nword1, nword2):
        locs = set.union(*(noun.get_locs() for noun in self.match_nouns(nword2)))
        for noun in self.match_nouns(nword1):
            noun.set_loc(*locs)
            
            
    def a_sendtonoun(self, nword1, nword2):
        self.a_sendnoun(nword1, nword2)
        
        
    def a_swapnouns(self, nword1, nword2):
        nouns1 = self.match_nouns(nword1)
        nouns2 = self.match_nouns(nword2)
        locs1 = set.union(*(noun.get_locs() for noun in nouns1))
        locs2 = set.union(*(noun.get_locs() for noun in nouns2))
        for noun in nouns1:
            noun.set_loc(*locs2)
        for noun in nouns2:
            noun.set_loc(*locs1)
            
            
    def a_setnoundesc(self, nword, mid):
        for noun in self.match_nouns(nword):
            noun.set_description(self.messages[mid])
            
            
    def a_addnounnote(self, nword, mid):
        for noun in self.match_nouns(nword):
            noun.add_note(mid)
        
        
    def a_removenounnote(self, nword, mid):
        for noun in self.match_nouns(nword):
            noun.remove_note(mid)
        
        
    def a_clearnounnotes(self, nword):
        for noun in self.match_nouns(nword):
            noun.clear_notes()
        
        
    def a_addroomnote(self, rword, mid):
        for rid in rword.split(','):
            self.game.get_room(rid).add_note(mid)
        
        
    def a_removeroomnote(self, rword, mid):
        for rid in rword.split(','):
            self.game.get_room(rid).remove_note(mid)
        
        
    def a_clearroomnotes(self, rword):
        for rid in rword.split(','):
            self.game.get_room(rid).clear_notes()
            
    
    def a_setvar(self, vid, value):
        self.game.set_var(vid, value)
        
    
    def a_adjustvar(self, vid, value):
        self.game.adjust_var(vid, value)
    
