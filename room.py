class Room:
    def __init__(self, rdata):
        self.data = rdata
        self.notes = self.data.get('notes', [])
            
            
    def is_start(self):
        return bool(self.data.get('start'))
            
            
    def get_description(self):
        return self.data.get('desc', '')
    
    
    def get_exits(self):
        return self.data.get('exits', {})
    
    
    def get_notes(self):
        return self.notes
    
    
    def add_note(self, mid):
        self.notes.append(mid)
    
    
    def remove_note(self, mid):
        while mid in self.notes:
            self.notes.remove(mid)
            
            
    def clear_notes(self, mid):
        self.notes = []