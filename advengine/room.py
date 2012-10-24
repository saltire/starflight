class Room:
    def __init__(self, rid, rdata, rstate=None):
        self.id = rid
        self.data = rdata
        
        if rstate is None:
            self.exits = self.data.get('exits', {})
            self.desc = None
            self.notes = self.data.get('notes', [])
        else:
            for key, value in rstate:
                setattr(self, key, value)
        
        
    def export_state(self):
        return {key: getattr(self, key) for key in ('exits', 'desc', 'notes')}
         
    
    def get_id(self):
        return self.id
            
            
    def is_start(self):
        return bool(self.data.get('start'))
            
            
    def get_exits(self):
        return self.exits
    
    
    def set_exit(self, dir, rid):
        self.exits[dir] = rid
        
        
    def remove_exit_dir(self, dir):
        if dir in self.exits:
            del self.exits[dir]
            
            
    def remove_exit_dest(self, rid):
        for dir, dest in self.exits.items():
            if dest == rid:
                del self.exits[dir]
        
        
    def clear_exits(self):
        self.exits.clear()
    
    
    def get_description(self):
        return self.desc if self.desc is not None else self.data.get('desc', '')
    
    
    def set_description(self, message):
        self.desc = message
        
        
    def get_notes(self):
        return self.notes
    
    
    def add_note(self, mid):
        self.notes.append(mid)
    
    
    def remove_note(self, mid):
        while mid in self.notes:
            self.notes.remove(mid)
            
            
    def clear_notes(self):
        self.notes = []