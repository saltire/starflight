class Noun:
    def __init__(self, nid, ndata):
        self.id = nid
        self.data = ndata
        self.locs = set(self.data.get('locs', []))
        self.notes = self.data.get('notes', [])
        self.desc = self.data.get('desc',  '')
        
        
    def get_id(self):
        return self.id
            
            
    def get_locs(self):
        return self.locs
    
    
    def set_locs(self, rid):
        self.locs = set([rid] if isinstance(rid, str) or isinstance(rid, unicode) else rid)
    
    
    def add_loc(self, rid):
        self.locs.add(rid)
        
        
    def remove_loc(self, rid):
        self.locs.discard(rid)
    
    
    def clear_locs(self):
        self.locs = set()
    
    
    def get_notes(self):
        return self.notes
    
    
    def add_note(self, mid):
        self.notes.append(mid)
        
        
    def remove_note(self, mid):
        while mid in self.notes:
            self.notes.remove(mid)
        
        
    def clear_notes(self):
        self.notes = []
            
            
    def get_words(self):
        return self.data.get('words', [])
    
    
    def get_name(self):
        return self.data.get('name', '')

    
    def get_short_name(self):
        return self.data.get('shortname', '')
    
    
    def get_short_desc(self):
        return self.data.get('shortdesc', '')
    
    
    def get_description(self):
        return self.desc
    
    
    def set_description(self, message):
        self.desc = message
        
        
    def is_movable(self):
        return bool(self.data.get('movable'))
    
    
    def is_visible(self):
        return bool(self.data.get('visible'))

    
    def is_wearable(self):
        return bool(self.data.get('wearable'))
    
