import json
import logging
import random
import re

import game


class Adventure:
    def __init__(self, gamepath):
        with open(gamepath, 'rb') as gamefile:
            data = json.load(gamefile)
        
        self.controls = data.get('controls', [])
        self.messages = data.get('messages', {})
        self.game = game.Game(data)
        
        def add_to_synonyms(wordslist):
            for words in wordslist:
                self.synonyms.update({word: self.synonyms.setdefault(word, set()) | set(words) for word in words})
            
        self.synonyms = {}
        add_to_synonyms(data.get('words', []))
        add_to_synonyms([noun.get('words', []) for noun in data.get('nouns', {}).values()])
                
        
    def do_command(self, command):
        """Get a command, and execute a single turn of the game."""
        status = 'ok'
        
        self.game.increment_turn()
        self.output = []
        self.words = [word for word in command.strip().split() if word not in ('the', 'a', 'an')]

        while True:
            status, actions = self.do_controls()
            if status != 'replace':
                break
            
            # if status == replace, actions will contain the replacement command
            self.words = self.substitute_words(actions).split()
            logging.debug('replace: %s', ' '.join(self.words))
            
        for action in actions:
            status = self.do_action(action)
            
        return status, self.output
    
    
    def substitute_words(self, phrase):
        """Substitute %1, %2, etc. in phrase with words from the original command."""
        sub_word = lambda m: self.words[int(m.group(1)) - 1] if len(self.words) >= int(m.group(1)) else ''
        #logging.debug('substituting from: %s to: %s', phrase, re.sub('%(\d+)', sub_word, phrase))
        return re.sub('%(\d+)', sub_word, phrase)
    
    
    def do_controls(self):
        """Step through all the tests and actions for this turn."""
        status = 'ok'
        allactions = []
        
        for controlset in self.controls:
            for control in controlset:
                status, actions = self.do_control(control)
                allactions.extend(actions)
                
                if status == 'done':
                    break
                elif status == 'replace':
                    return 'replace', actions
                elif status == 'gameover':
                    return 'gameover', allactions
        
        return status, allactions
    
    
    def do_control(self, control):
        """Execute the tests and (possibly) actions for a single control."""
        status = 'ok'
        allactions = []
        
        if self.test_is_true(control.get('if')):
            if control.get('replace'):
                return 'replace', control.get('replace')
            
            for action in control.get('then', []):
                if isinstance(action, dict):
                    # action is a subcontrol
                    status, actions = self.do_control(action)
                    
                    if status == 'replace':
                        return 'replace', actions
                    
                    allactions.extend(actions)
                    if status in ('done', 'gameover'):
                        break
                    
                else:
                    allactions.append(action)
                    
            if control.get('done'):
                status = 'done'
            if control.get('gameover'):
                status = 'gameover'
            
        return status, allactions
    
    
    def test_is_true(self, test):
        """Decide whether a test or set of tests evaluates to true."""
        if all(isinstance(subtest, list) for subtest in test):
            # test is a list of subtests (i.e. a list of lists)
            # any of these can be true
            return any(all(self.cond_is_true(cond) for cond in subtest) for subtest in test)
                  
        elif all(isinstance(cond, str) or isinstance(cond, unicode) for cond in test):
            # test is a list of conditions (i.e. a list of strings)
            # all of these must be true
            return all(self.cond_is_true(cond) for cond in test)
        
        else:
            raise Exception('Invalid test:', test)
    
    
    def cond_is_true(self, cond):
        """Decide whether a single condition evaluates to true."""
        #cond = self.substitute_words(cond.strip())
        #logging.debug('test: %s:', cond)
        if cond == '*':
            return True
        
        neg = False
        if cond[0] == '!':
            neg = True
            cond = cond[1:]
            
        cwords = cond.strip().split()
        success = getattr(self, 't_{0}'.format(cwords[0]))(*cwords[1:])
        logging.debug('test: %s: %s', cond, not success if neg else success)
        return not success if neg else success
    
    
    def do_action(self, action):
        """Call the method for a single action."""
        #action = self.substitute_words(action.strip())
        awords = action.strip().split()
        logging.debug('action: %s', action)
        return getattr(self, 'a_{0}'.format(awords[0]))(*awords[1:])
    
    
    def queue_output(self, message):
        """Add a message or messages to the output queue."""
        if isinstance(message, list):
            for msg in message:
                self.queue_output(msg)
        elif len(message):
            self.output.append(self.substitute_words(message))
    
    
    def match_word(self, inputword, word):
        """Check if an input word is a synonym of another word."""
        return word == '*' or any(inputword in self.synonyms.get(word, []) for word in word.split('|'))
    
    
    def match_nouns(self, inputword):
        """Return a set of nouns matching an input. If the noun is passed by ID,
        the set will contain that one noun. If an input wildcard is passed, it will
        contain all nouns matching the input word."""
        if inputword[0] == '%':
            return self.game.get_nouns_by_name(self.substitute_words(inputword))
        else:
            return set([self.game.get_noun(inputword)])
    
    
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
    
    
    def t_room(self, rid):
        return self.game.get_current_room_id() == rid
    
    
    def t_exitexists(self, direction):
        return any(self.match_word(direction, rexit) for rexit in self.game.get_current_room().get_exits())
    
    
    def t_nounloc(self, nword, rid):
        return any(noun for noun in self.match_nouns(nword) if rid in noun.get_locs())
    
    
    def t_ininv(self, nword):
        return self.t_nounloc(nword, 'INVENTORY')
    
    
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
    
    
    def a_message(self, mid):
        self.queue_output(self.messages[mid])
    
    
    def a_pause(self):
        self.queue_output('PAUSE')
    
    
    def a_look(self):
        room = self.game.get_current_room()
        self.queue_output(room.get_description())
        for mid in room.get_notes():
            self.a_message(mid)
    
    
    def a_move(self, dir):
        dir = self.substitute_words(dir)
        try:
            dest = next(dest for exit, dest in self.game.get_current_room().get_exits().items()
                        if self.match_word(dir, exit))
            self.game.go_to_room(dest)
            self.a_look()
            
        except StopIteration:
            self.a_message('cantgo')
            
            
    def a_examine(self, nword):
        msgs = []
        for noun in self.match_nouns(nword) & self.game.get_nouns_present():
            if noun.get_description():
                msgs.append(noun.get_description())
            msgs.extend(self.messages[mid] for mid in noun.get_notes())
        
        if msgs:
            self.queue_output(msgs)
        else:
            self.a_message('nothingunusual')
            
            
    def a_take(self, nword):
        presentnouns = self.match_nouns(nword) & self.game.get_nouns_present()
        if not presentnouns:
            self.a_message('dontsee')
        else:
            movables = set(noun for noun in presentnouns if noun.is_movable())
            if not movables:
                self.a_message('cantverb')
            else:
                notcarried = set(noun for noun in movables if 'INVENTORY' not in noun.get_locs())
                if not notcarried:
                    self.a_message('alreadycarrying')
                else:
                    for noun in notcarried:
                        noun.set_locs('INVENTORY')
                    self.a_message('taken')
                    
                    
    def a_wear(self, nword):
        presentnouns = self.match_nouns(nword) & self.game.get_nouns_present()
        if not presentnouns:
            self.a_message('dontsee')
        else:
            wearables = set(noun for noun in presentnouns if noun.is_wearable())
            if not wearables:
                self.a_message('cantverb')
            else:
                notworn = set(noun for noun in wearables if 'WORN' not in noun.get_locs())
                if not notworn:
                    self.a_message('alreadywearing')
                else:
                    for noun in notworn:
                        noun.set_locs('WORN')
                    self.a_message('wearing')
                
            
    def a_drop(self, nword):
        carried = self.match_nouns(nword) & self.game.get_nouns_by_loc('INVENTORY')
        if carried:
            for noun in carried:
                noun.set_locs(self.game.get_current_room_id())
            self.a_message('dropped')
        else:
            self.a_message('donthave')        
            
            
    def a_destroy(self, nword):
        for noun in self.match_nouns(nword):
            noun.clear_locs()
            
            
    def a_sendnoun(self, nword, rid):
        for noun in self.match_nouns(nword):
            noun.set_locs(rid)
            
            
    def a_sendtoroom(self, nword):
        self.a_sendnoun(nword, self.game.get_current_room_id())
        
        
    def a_sendtonoun(self, nword1, nword2):
        locs = set.union(noun.get_locs() for noun in self.match_nouns(nword2))
        for noun in self.match_nouns(nword1):
            noun.set_locs(locs)
            
            
    def a_swapnouns(self, nword1, nword2):
        nouns1 = self.match_nouns(nword1)
        nouns2 = self.match_nouns(nword2)
        locs1 = set.union(noun.get_locs() for noun in nouns1)
        locs2 = set.union(noun.get_locs() for noun in nouns2)
        for noun in nouns1:
            noun.set_locs(locs2)
        for noun in nouns2:
            noun.set_locs(locs1)
            
            
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
        
        
    def a_addroomnote(self, rid, mid):
        self.game.get_room(rid).add_note(mid)
        
        
    def a_removeroomnote(self, rid, mid):
        self.game.get_room(rid).remove_note(mid)
        
        
    def a_clearroomnotes(self, rid):
        self.game.get_room(rid).clear_notes()
            
    
    def a_setvar(self, vid, value):
        self.game.set_var(vid, value)
        
    
    def a_adjustvar(self, vid, value):
        self.game.adjust_var(vid, value)
    
        