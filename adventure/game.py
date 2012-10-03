import gamedata


class Game:
    def __init__(self, gamepath):
        self.data = gamedata.GameData(gamepath)
        self.turn = 0
        
        self.vars = self.data.get_initial_vars()
        self.room = self.data.get_initial_room()
        
        
    def get_controls(self):
        return self.data.get_controls()
    
    
    def get_message(self, mid):
        return self.data.get_message(mid)
    
    
    def get_turn(self):
        return self.turn
    
    
    def new_turn(self):
        self.turn += 1
        
        
    def get_var(self, vid):
        return self.vars[vid]
    
    
    def get_current_room(self):
        return self.room
        
    
    def match_word(self, inputword, word):
        return self.data.match_word(inputword, word)
    