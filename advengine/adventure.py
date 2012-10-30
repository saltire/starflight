import json
import logging
import re

import game
import tests
import actions


class Adventure(tests.Tests, actions.Actions):
    def __init__(self, gamepath, state=None):
        with open(gamepath, 'rb') as gamefile:
            data = json.load(gamefile)
        
        self.controls = data.get('controls', [])
        self.messages = data.get('messages', {})
        self.game = game.Game(data, state)
        
        def add_to_synonyms(wordslist):
            for words in wordslist:
                self.synonyms.update({word: self.synonyms.setdefault(word, set()) | set(words) for word in words})
            
        self.synonyms = {}
        add_to_synonyms(data.get('words', []))
        add_to_synonyms([noun.get('words', []) for noun in data.get('nouns', {}).values()])
        
        
    def export_state(self):
        return self.game.export_state()
        
        
    def do_command(self, command):
        """Get a command, and execute a single turn of the game."""
        self.game.increment_turn()
        self.output = []
        self.words = [word for word in command.strip().split() if word not in ('the', 'a', 'an')]

        while True:
            status = self.do_controls()
            if status != 'replace':
                break
            
        return status, self.output
    
    
    def do_controls(self):
        """Step through all the tests and actions for this turn."""
        status = 'ok'
        
        for controlset in self.controls:
            allactions = []
            for control in controlset:
                status, actions = self.do_control(control)
                allactions.extend(actions)
                
                if status == 'replace':
                    self.words = self.sub_input_words(actions).split()
                    logging.debug('replace: %s', ' '.join(self.words))
                    return 'replace'
                
                elif status == 'gameover':
                    logging.debug('gameover')
                    break
                
                elif status == 'done':
                    logging.debug('done')
                    status = 'ok'
                    break
        
            for action in allactions:
                self.do_action(action)
                
            if status == 'gameover':
                break
            
        return status
    
    
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
                    if status == 'gameover':
                        return 'gameover', allactions
                    if status == 'done':
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
            return any(self.test_is_true(subtest) for subtest in test)
                  
        elif all(isinstance(cond, str) or isinstance(cond, unicode) for cond in test):
            # test is a list of conditions (i.e. a list of strings)
            # all of these must be true
            return all(self.cond_is_true(cond) for cond in test)
        
        else:
            raise Exception('Invalid test:', test)
    
    
    def cond_is_true(self, cond):
        """Decide whether a single condition evaluates to true."""
        #cond = self.sub_input_words(cond.strip())
        #logging.debug('test: %s:', cond)
        if cond == '*':
            return True
        
        neg = False
        if cond[0] == '!':
            neg = True
            cond = cond[1:]
            
        cwords = cond.strip().split()
        success = getattr(self, 't_{0}'.format(cwords[0]))(*cwords[1:])
        logging.debug('test: %s%s: %s', '!' if neg else '', cond, not success if neg else success)
        return not success if neg else success
    
    
    def do_action(self, action):
        """Call the method for a single action."""
        #action = self.sub_input_words(action.strip())
        awords = action.strip().split()
        logging.debug('action: %s', action)
        return getattr(self, 'a_{0}'.format(awords[0]))(*awords[1:])
    
    
    def queue_output(self, message):
        """Add a message or messages to the output queue."""
        if isinstance(message, list):
            for msg in message:
                self.queue_output(msg)
                
        elif len(message):
            message = re.sub('%VAR\((.+?)\)', lambda m: str(self.game.get_var(m.group(1))), message)
            message = message.replace('%TURNS', str(self.game.get_turn()))
            self.output.append(self.sub_input_words(message))
    
    
    def sub_input_words(self, phrase):
        """Substitute %1, %2, etc. in phrase with words from the original command."""
        sub_input = lambda m: self.words[int(m.group(1)) - 1] if len(self.words) >= int(m.group(1)) else ''
        #logging.debug('substituting from: %s to: %s', phrase, re.sub('%(\d+)', sub_word, phrase))        
        return re.sub('%(\d+)', sub_input, phrase)
    
    
    def match_word(self, inputword, word):
        """Check if an input word is a synonym of another word."""
        return word == '*' or any(inputword in self.synonyms.get(word, []) for word in word.split('|'))
    
    
    def match_nouns(self, inputword):
        """Return a set of nouns matching an input. If the noun is passed by ID,
        the set will contain that one noun. If an input wildcard is passed, it will
        contain all nouns matching the input word."""
        if inputword[0] == '%':
            return self.game.get_nouns_by_name(self.sub_input_words(inputword))
        else:
            return set(self.game.get_noun(nid) for nid in inputword.split(','))
    
    
    def show_noun_contents(self, container):
        """Queue for output a list of nouns contained within a noun."""
        contents = self.game.get_nouns_by_loc(container.get_id())
        if contents:
            self.queue_output(self.messages['invitemcontains'].replace('%NOUN', container.get_short_name()))
            for noun in contents:
                self.queue_output(self.messages['invitemcontained'].replace('%NOUN', noun.get_name()))
                self.show_noun_contents(noun)
                
        
        