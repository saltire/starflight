class Noun:
    def __init__(self, nid, ndata):
        self.id = nid
        self.data = ndata
        
        def add_attrs(attrs, default):
            for attr in attrs:
                setattr(self, attr, self.data.get(attr, default))
        
        add_attrs(('name', 'desc', 'shortname', 'shortdesc'), '')
        add_attrs(('notes', 'words', 'locs'), [])
    
    
    def is_movable(self):
        return bool(self.data.get('movable'))
    
    
    def is_visible(self):
        return bool(self.data.get('visible'))

    
    def is_wearable(self):
        return bool(self.data.get('wearable'))
    
