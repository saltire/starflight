class Actions:
    def a_message(self, mid):
        self.queue_message(mid)
    
    
    def a_pause(self):
        self.queue_raw_output('PAUSE')
    
    
    def a_look(self):
        room = self.game.get_current_room()
        self.queue_raw_output(room.get_description())
        for mid in room.get_notes():
            self.queue_message(mid)
            
        for noun in self.game.get_nouns_by_loc(self.game.get_current_room_id()):
            if noun.is_visible():
                self.queue_raw_output(noun.get_short_desc())
                self.show_noun_contents(noun)
                
                
    def a_inv(self):
        inv = self.game.get_nouns_by_loc('INVENTORY') | self.game.get_nouns_by_loc('WORN')
        if inv:
            self.queue_message('carrying')
            for noun in inv:
                self.queue_message('invitemworn' if 'WORN' in noun.get_locs() else 'invitem',
                                   '%NOUN', noun.get_name())
                self.show_noun_contents(noun)
        else:
            self.queue_message('carryingnothing')
    
    
    def a_move(self, dir):
        dir = self.sub_input_words(dir)
        try:
            dest = next(dest for exit, dest in self.game.get_current_room().get_exits().items()
                        if self.match_word(dir, exit))
            self.game.go_to_room(dest)
            self.a_look()
            
        except StopIteration:
            self.queue_message('cantgo')
            
            
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
            
            
    def a_take(self, nword):
        presentnouns = self.match_nouns(nword) & self.game.get_nouns_present()
        if not presentnouns:
            self.queue_message('dontsee')
        else:
            movables = set(noun for noun in presentnouns if noun.is_movable())
            if not movables:
                self.queue_message('cantverb')
            else:
                notcarried = set(noun for noun in movables if 'INVENTORY' not in noun.get_locs())
                if not notcarried:
                    self.queue_message('alreadycarrying')
                else:
                    for noun in notcarried:
                        noun.set_loc('INVENTORY')
                    self.queue_message('taken')
                    
                    
    def a_wear(self, nword):
        presentnouns = self.match_nouns(nword) & self.game.get_nouns_present()
        if not presentnouns:
            self.queue_message('dontsee')
        else:
            wearables = set(noun for noun in presentnouns if noun.is_wearable())
            if not wearables:
                self.queue_message('cantverb')
            else:
                notworn = set(noun for noun in wearables if 'WORN' not in noun.get_locs())
                if not notworn:
                    self.queue_message('alreadywearing')
                else:
                    for noun in notworn:
                        noun.set_loc('WORN')
                    self.queue_message('wearing')
                
            
    def a_drop(self, nword):
        carried = self.match_nouns(nword) & self.game.get_nouns_by_loc('INVENTORY', 'WORN')
        if carried:
            for noun in carried:
                noun.set_loc(self.game.get_current_room_id())
            self.queue_message('dropped')
        else:
            self.queue_message('donthave')        
            
            
    def a_destroy(self, nword):
        for noun in self.match_nouns(nword):
            noun.clear_locs()
            
            
    def a_sendnoun(self, nword, rword):
        for noun in self.match_nouns(nword):
            noun.set_loc(*rword.split(','))
            
            
    def a_sendtoroom(self, nword):
        self.a_sendnoun(nword, self.game.get_current_room_id())
        
        
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
    
