class Room:
    def __init__(self, rdata):
        for attr in ('desc', 'exits', 'name', 'start'):
            setattr(self, attr, rdata.get(attr))
            
            
    def is_start(self):
        return bool(self.start)
            
            
    def get_description(self):
        return self.desc or ''
    
    
    def get_exits(self):
        return self.exits or {}