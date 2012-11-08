class Room:
    def __init__(self, rid, rdata, rstate=None):
        self.id = rid
        self.data = rdata
        
        if rstate is None:
            self.exits = self.data.get('exits', {})
            self.desc = None
            self.notes = self.data.get('notes', [])
            self.visited = False
        else:
            for key, value in rstate.items():
                setattr(self, key, value)
        
        
    def export_state(self):
        return {key: getattr(self, key) for key in ('exits', 'desc', 'notes', 'visited')}
         
    
    def get_id(self):
        return self.id
            
            
    def is_start(self):
        return bool(self.data.get('start'))
    
    
    def visit(self):
        self.visited = True
        
        
    def visited(self):
        return self.visited
            
            
    def get_exits(self):
        return self.exits
    
    
    def set_exit(self, exitdir, rid):
        self.exits[exitdir] = rid
        
        
    def remove_exit_dir(self, exitdir):
        if exitdir in self.exits:
            del self.exits[exitdir]
            
            
    def remove_exit_dest(self, rid):
        for exitdir, dest in self.exits.items():
            if dest == rid:
                del self.exits[exitdir]
        
        
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