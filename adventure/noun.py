class Noun:
    def __init__(self, ndata):
        for attr in ('loc', 'desc', 'name', 'movable', 'shortdesc', 'shortname', 'visible', 'wearable', 'words'):
            setattr(self, attr, ndata.get(attr))
            
            
    def get_words(self):
        return self.words or []