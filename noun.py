class Noun:
    def __init__(self, ndata):
        self.data = ndata
        self.locs = set(self.data.get('locs') or [])
        self.notes = self.data.get('notes') or []
            
            
    def get_locs(self):
        return self.locs
    
    
    def get_notes(self):
        return self.notes
            
            
    def get_words(self):
        return self.data.get('words') or []
    
    
    def get_description(self):
        return self.data.get('desc') or ''

    