class Actions:
    def a_message(self, mid):
        self.queue_message(mid)
    
    
    def a_pause(self):
        self.queue_raw_output('PAUSE')
    
    
    def a_showdesc(self, oid=None):
        obj = (self.game.get_current_room() if oid is None else 
            self.game.get_noun(oid) or self.game.get_room(oid))
        self.queue_raw_output(obj.get_description())
        
        
    def a_shownotes(self, oid=None):
        obj = (self.game.get_current_room() if oid is None else 
            self.game.get_noun(oid) or self.game.get_room(oid))
        for mid in obj.get_notes():
            self.queue_message(mid)


    def a_showcontents(self, oid=None, by_name=False):
        obj = (self.game.get_current_room() if oid is None else 
            self.game.get_noun(oid) or self.game.get_room(oid))
        for noun in self.game.get_nouns_by_loc(obj.get_id()):
            if noun.is_visible():
                self.queue_raw_output(noun.get_name() if by_name else noun.get_short_desc())
                self.show_noun_contents(noun)
                
                
    def a_listcontents(self, oid=None):
        self.a_showcontents(oid, True)
                
                
    def a_move(self, movedir):
        try:
            dest = next(dest for exitdir, dest in self.game.get_current_room().get_exits().items()
                        if self.match_word(movedir, exitdir))
            self.game.go_to_room(dest)
            self.a_look()
        except:
            pass
            
            
    def a_inv(self, intro_msg, carry_msg, wear_msg):
        inv = self.game.get_nouns_by_loc('INVENTORY') | self.game.get_nouns_by_loc('WORN')
        if inv:
            self.queue_message(intro_msg)
            for noun in inv:
                self.queue_message(wear_msg if 'WORN' in noun.get_locs() else carry_msg,
                                   {'%NOUN': noun.get_name()})
                self.show_noun_contents(noun)
    
    
    def a_examine(self, nword):
        msgs = []
        for noun in self.match_nouns(nword) & self.game.get_nouns_present():
            if noun.get_description():
                msgs.append(noun.get_description())
            msgs.extend(self.messages[mid] for mid in noun.get_notes())
        
        if msgs:
            self.queue_raw_output(msgs)
        else:
            self.queue_message('nothingunusual')
            
            
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
    
