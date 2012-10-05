class Game:
    def __init__(self, data):
        self.data = data
        self.turn = 0
        
        self.vars = self.data.get_initial_vars()
        self.room = self.data.get_initial_room() # current room id
        
        
    def get_message(self, mid):
        return self.data.get_message(mid)
    
    
    def get_turn(self):
        return self.turn
    
    
    def increment_turn(self):
        self.turn += 1
        
        
    def get_var(self, vid):
        return self.vars[vid]
    
    
    def get_current_room_id(self):
        return self.room
    
    
    def go_to_room(self, rid):
        self.room = rid
    
    
    def get_current_room(self):
        return self.data.get_room(self.room)
        
    
    def match_word(self, inputword, word):
        return self.data.match_word(inputword, word)
    