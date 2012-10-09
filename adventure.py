import json
import logging
import re

import game


class Adventure:
    def __init__(self, gamepath):
        with open(gamepath, 'rb') as gamefile:
            data = json.load(gamefile)
        
        self.controls = data.get('controls', [])
        self.messages = data.get('messages', {})
        self.game = game.Game(data)
        
        def add_to_vocab(vocab, words):
            words = set(words)
            for group in [group for group in vocab if group & words]:
                words = group | words
                vocab.remove(group)
            if words:
                vocab.append(words)
            return vocab

        self.vocab = []
        for words in data.get('words', []):
            add_to_vocab(self.vocab, words)
        for noun in data.get('nouns', {}).values():
            add_to_vocab(self.vocab, noun.get('words', []))

        
    def do_turn(self, command):
        """Get a command, and execute a single turn of the game."""
        self.game.increment_turn()
        self.output = []
        self.words = [word for word in command.split() if word not in ('the', 'a', 'an')]

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
                    allactions.extend(actions)
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
        cond = self.substitute_words(cond.strip())
        #logging.debug('test: %s:', cond)
        
        if cond == '*':
            return True
        
        neg = False
        if cond[0] == '!':
            neg = True
            cond = cond[1:]
            
        cwords = cond.split()
        success = getattr(self, 't_{0}'.format(cwords[0]))(*cwords[1:])
        logging.debug('test: %s: %s', cond, not success if neg else success)
        return not success if neg else success
    
    
    def do_action(self, action):
        """Call the method for a single action."""
        action = self.substitute_words(action.strip())
        awords = action.split()
        logging.debug('action: %s', action)
        return getattr(self, 'a_{0}'.format(awords[0]))(*awords[1:])
    
    
    def queue_output(self, message):
        """Add a message or messages to the output queue."""
        if len(message):
            self.output.append(self.substitute_words(message))
    
    
    def match_word(self, inputword, word):
        """Check if an input word is a synonym of another word."""
        if word == '*':
            return True
        
        words = word.split('|')
        if inputword in words:
            return True
        
        for w in words:
            for group in self.vocab:
                if w in group and inputword in group:
                    return True
            
        return False
    
    
    def t_start(self):
        return self.game.get_turn() == 1
    
    
    def t_input(self, *cwords):
        if len(self.words) < len(cwords):
            return False
        
        for index, cword in enumerate(cwords):
            if self.match_word(self.words[index], cword):
                continue
            else:
                return False
        return True
    
    
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
    
    
    def a_message(self, mid):
        self.queue_output(self.messages[mid])
    
    
    def a_pause(self):
        self.queue_output('PAUSE')
    
    
    def a_look(self):
        room = self.game.get_current_room()
        self.queue_output(room.get_description())
        for mid in room.get_notes():
            self.a_message(mid)
    
    
    def a_move(self, direction=''):
        try:
            dest = next(dest for exit, dest in self.game.get_current_room().get_exits().items()
                            if self.match_word(direction, exit))
            self.game.go_to_room(dest)
            self.a_look()
            
        except StopIteration:
            self.a_message('cantgo')
            
            
    def a_examine(self, nword=''):
        try:
            noun = next(noun for noun in self.game.get_nouns_present() if nword in noun.get_words())
            desc = noun.get_description()
            notes = noun.get_notes()
            if not desc and not notes:
                raise StopIteration
            
            self.queue_output(desc)
            for mid in notes:
                self.a_message(mid)
        
        except StopIteration:
            self.a_message('nothingunusual')
            
    
    def a_setvar(self, vid, value):
        self.game.set_var(vid, value)
        
    
    def a_adjustvar(self, vid, value):
        self.game.adjust_var(vid, value)
        
        
    def a_removeroomnote(self, rid, mid):
        self.game.get_room(rid).remove_note(mid)
    
        