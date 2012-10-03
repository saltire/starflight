import collections
import re

import game


class Adventure:
    def __init__(self, gamefile):
        self.game = game.Game(gamefile)
        self.controls = self.game.get_controls()
        self.messages = collections.deque()
        
        
    def start_game(self):
        command = ''
        while True:
            status = self.do_turn(command)
            if status == 'gameover':
                break
            
            print
            print '>',
            command = raw_input().strip()
            
            
    def do_turn(self, command):
        self.game.new_turn()
        self.messages.clear()
        
        words = [word for word in command.split() if word not in ('the', 'a', 'an')]

        while True:
            status, actions = self.do_controls(words)
            if status != 'replace':
                break
            
            # replace command, substituting '%x' with words from original command
            words = re.sub('%(\d+)', lambda m: words[int(m.group(1)) - 1], actions).split()
            
        for action in actions:
            status = self.do_action(action)
            
        while self.messages:
            msg = self.messages.popleft()
            if msg == 'PAUSE':
                print
                raw_input('Press Enter to continue...')
                print
            else:
                print msg
            
        return status
    
    
    def do_controls(self, words):
        status = 'ok'
        allactions = []
        
        for controlset in self.controls:
            for control in controlset:
                status, actions = self.do_control(control, words)
                allactions.extend(actions)
                
                if status == 'done':
                    break
                elif status == 'replace':
                    return 'replace', actions
                elif status == 'gameover':
                    return 'gameover', allactions
        
        return status, allactions
    
    
    def do_control(self, control, words):
        status = 'ok'
        allactions = []
        
        if self.test_is_true(control.get('if'), words):
            if control.get('replace'):
                return 'replace', control.get('replace')
            
            for action in control.get('then', []):
                if isinstance(action, dict):
                    status, actions = self.do_control(action, words)
                    allactions.extend(actions)
                else:
                    allactions.append(action)
                    
            if control.get('done'):
                status = 'done'
            if control.get('gameover'):
                status = 'gameover'
            
        return status, allactions
    
    
    def test_is_true(self, test, words):
        if all(isinstance(subtest, list) for subtest in test):
            # test is a list of subtests (i.e. a list of lists)
            # any of these can be true
            return any(all(self.cond_is_true(cond, words) for cond in subtest) for subtest in test)
                  
        elif all(isinstance(cond, str) or isinstance(cond, unicode) for cond in test):
            # test is a list of conditions (i.e. a list of strings)
            # all of these must be true
            return all(self.cond_is_true(cond, words) for cond in test)
        
        else:
            raise Exception('Invalid test:', test)
    
    
    def cond_is_true(self, cond, words):
        #print 'test:', cond, ':',
        
        cond = cond.strip()
        
        if cond == '*':
            return True
        
        neg = False
        if cond[0] == '!':
            neg = True
            cond = cond[1:]
            
        cwords = cond.split()            
        success = getattr(self, 't_{0}'.format(cwords[0]))(words, *cwords[1:])
        #print not success if neg else success
        return not success if neg else success
    
    
    def do_action(self, action):
        awords = action.split()
        return getattr(self, 'a_{0}'.format(awords[0]))(*awords[1:])
    
    
    def t_start(self, words):
        return self.game.get_turn() == 1
    
    
    def t_input(self, words, *cwords):
        if len(words) < len(cwords):
            return False
        
        for index, cword in enumerate(cwords):
            if self.game.match_word(words[index], cword):
                continue
            else:
                return False
        return True
    
    
    def t_var(self, words, vid, value):
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
    
    
    def t_room(self, words, rid):
        return self.game.get_current_room() == rid
    
    
    def a_message(self, mid):
        self.messages.append(self.game.get_message(mid))
        return 'ok'
    
    
    def a_pause(self):
        self.messages.append('PAUSE')
        return 'ok'
    
    
    def a_look(self):
        self.messages.append(self.game.get_current_room().get_description())
        return 'ok'
    
    
    
        