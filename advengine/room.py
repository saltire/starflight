class Room:
    def __init__(self, rid, rdata):
        self.id = rid
        self.data = rdata
        
        def add_attrs(attrs, default):
            for attr in attrs:
                setattr(self, attr, self.data.get(attr, default))
        
        add_attrs(('name', 'desc'), '')
        add_attrs(('notes', 'exits'), [])
        
        self.visited = False
        
        
    def is_start(self):
        return bool(self.data.get('start'))
        
        
    def is_visited(self):
        return self.visited
    
    
    def visit(self):
        self.visited = True
