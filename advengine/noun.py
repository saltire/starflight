class Noun:
    def __init__(self, nid, ndata, nstate=None):
        self.id = nid
        self.data = ndata
        
        if nstate is None:
            self.locs = set(self.data.get('locs', []))
            self.desc = None
            self.notes = self.data.get('notes', [])
        else:
            for key, value in nstate.items():
                setattr(self, key, value)
        
        
    def export_state(self):
        return {key: getattr(self, key) for key in ('locs', 'desc', 'notes')}
    
    
    def get_id(self):
        return self.id
    
    
    def get_locs(self):
        return self.locs
    
    
    def set_loc(self, *rid):
        self.locs = set(rid)
    
    
    def add_loc(self, *rid):
        self.locs |= set(rid)
        
        
    def remove_loc(self, *rid):
        self.locs -= set(rid)
    
    
    def clear_locs(self):
        self.locs = set()
    
    
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
            
            
    def get_words(self):
        return set(self.data.get('words', []))
    
    
    def get_name(self):
        return self.data.get('name', '')

    
    def get_short_name(self):
        return self.data.get('shortname', '')
    
    
    def get_short_desc(self):
        return self.data.get('shortdesc', '')
    
    
    def is_movable(self):
        return bool(self.data.get('movable'))
    
    
    def is_visible(self):
        return bool(self.data.get('visible'))

    
    def is_wearable(self):
        return bool(self.data.get('wearable'))
    
