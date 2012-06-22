import game


class Engine:
    def __init__(self, file):
        self.game = game.Game(file)
        
        
    def new_game(self):
        self.state = game.State(self.game)
        return self.do_turn()
    
    
    def do_turn(self, command=''):
        """Execute a single turn of the game, and return the response."""
        input = [word for word in command.split() if word not in ('the', 'a', 'an')]
        
        while True:
            status, actions = self.do_controls(input)
            if status != 'restart':
                break
        
        return 'you typed: {0}'.format(' '.join(input))
    
    
    def do_controls(self, input):
        """Run through each set of control blocks."""
        for controlset in self.game.controls:
            for control in controlset:
                status, actions = self.do_control(control, input)
                if status == 'done':
                    break
                elif status == 'restart':
                    return 'restart', None
        return 'ok', actions
    
    
    def do_control(self, control, input):
        """Evaluate a single control block, and queue actions if appropriate."""
        if self.test_is_true(control.get('if')):
            for action in control.get('then'):
                self.queue_action(action)
            if control.get('done'):
                return 'done', actions
        return 'ok', actions
            
                
    def test_is_true(self, iftest):
        """Test to see if an "if" block evaluates to True or False."""
        for test in iftest:
            if isinstance(test[0], list):
                return any(all(self.cond_is_true(cond) for cond in subtest) for subtest in test)
            else:
                return all(self.cond_is_true(cond) for cond in test)
    
    
    def cond_is_true(self, cond):
        """Test to see if a single conditional statement evaluates to True or False."""
        pass
    
    
    def queue_action(self, action):
        """Execute an action."""
        # test if action is a control block
        if isinstance(action, dict):
            self.do_control(action)
        else:
            pass
        
        
        