import re

import game


class Adventure:
    def __init__(self, gamefile):
        self.game = game.Game(gamefile)
        self.turn = 0
        
        
    def start_game(self):
        command = ''
        while True:
            status = self.do_turn(command)
            if status == 'gameover':
                break
            command = raw_input().strip()
            
            
    def do_turn(self, command):
        words = [word for word in command.split() if word not in ('the', 'a', 'an')]
        
        while True:
            self.turn += 1
            status, actions = self.do_controls(words)
            if status != 'replace':
                break
            
            # replace command, substituting '%x' with words from original command
            words = re.sub('%(\d+)', lambda m: words[int(m.group(1)) - 1], actions).split()
            
        for action in actions:
            self.do_action(action)
    
    
    def do_controls(self, words):
        status = 'ok'
        allactions = []
        
        for controlset in self.game.controls:
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
    
    
    def test_is_true(self, iftest, words):
        for test in iftest:
            # test must be all lists, or all strings
            if all(isinstance(subtest, list) for subtest in test):
                return any(all(self.cond_is_true(cond, words) for cond in subtest) for subtest in test)
            else:
                return all(self.cond_is_true(cond, words) for cond in test)
    
    
    def cond_is_true(self, cond, words):
        cond = cond.strip()
        
        if cond == '*':
            return True
        
        if cond == 'start' and self.turn == 1:
            return True
        
        neg = False
        if cond[0] == '!':
            neg = True
            cond = cond[1:]
            
        cwords = cond.split()
        success = getattr(self, "t_{0}".format(cwords[0]))(cwords[1:], words)
        return not success if neg else success
    
    
    def do_action(self, action):
        pass
    
    
    def t_input(self, cwords, words):
        for index, cword in enumerate(cwords):
            if self.game.match_word(words[index], cword):
                continue
            else:
                return False
        return True
    
    
    
        
    
        