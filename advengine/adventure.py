import inspect
import logging

from datafile import DataFile
from game import Game
from tests import Tests
from actions import Actions


class Adventure():
    def __init__(self, gamepath):
        data = DataFile().get_data(gamepath)
        
        self.controls = data['controls']
        self.game = Game(data)
        
        self.tests = Tests(self.game)
        self.actions = Actions(self.game, self.tests)
        
        filters = dict(inspect.getmembers(self.tests, lambda m: hasattr(m, 'is_filter')))
        self.game.add_filters(filters)
        
        
    def do_command(self, command):
        """Get a command, and execute a single turn of the game."""
        self.game.start_turn(command)
        actions = self.do_command_actions(command)
        return self.game.end_turn(actions)
    
    
    def do_command_actions(self, command):
        """Step through all the tests and actions for this turn."""
        actions = []
        
        for controlset in self.controls:
            csactions = []
            for control in controlset:
                done = False
                for action, params in self.get_control_actions(control):
                    if action == 'replace':
                        logging.debug('replace: %s', params)
                        self.game.set_words(params)
                        return self.do_command_actions(params)
                    
                    elif action == 'gameover':
                        done = True
                        self.game.end_game()
                        break
                    
                    elif action == 'done':
                        done = True
                        break
                    
                    else:
                        csactions.append((action, params))
                        actions.append((action, params))
                        logging.debug((action, params))
                
                if done:
                    break
            
            for action, params in csactions:
                self.do_action(action, params)
                if self.game.gameover:
                    break
                
        return actions
    
    
    def get_control_actions(self, control):
        """Execute the tests and (possibly) actions for a single control."""
        actions = []
        
        if self.test_is_true(control.get('if')):
            if control.get('replace'):
                actions.append(('replace', self.game.sub_input_words(control.get('replace'))))
                return actions
            
            for action in control.get('then', []):
                if isinstance(action, dict):
                    # action is a subcontrol
                    actions.extend(self.get_control_actions(action))
                    
                else:
                    try:
                        action, params = action.split(' ', 1)
                        actions.append((action, params.split()))
                    except ValueError:
                        actions.append((action, []))
                    
            if control.get('done'):
                actions.append(('done', None))
            if control.get('gameover'):
                actions.append(('gameover', None))
            
        return actions
    
    
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
        
        cond, neg = (cond[1:], True) if cond[0] == '!' else (cond, False)
            
        cwords = cond.strip().split()
        success = getattr(self.tests, 't_' + cwords[0])(*cwords[1:])
        logging.debug('test: %s%s: %s', '!' if neg else '', cond, success ^ neg)
        return success ^ neg
    
    
    def do_action(self, action, params):
        """Call the method for a single action."""
        #action = self.sub_input_words(action.strip())
        logging.debug('action: %s', action)
        return getattr(self.actions, 'a_' + action)(*params)
    
    
    def is_game_over(self):
        return self.game.gameover


