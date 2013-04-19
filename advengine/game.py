import re

from noun import Noun
from room import Room


class Game:
    def __init__(self, data):
        self.vars = {vid: int(value) for vid, value in data['vars'].items()}
        self.rooms = {rid: Room(rid, rdata) for rid, rdata in data['rooms'].items()}
        self.nouns = {nid: Noun(nid, ndata) for nid, ndata in data['nouns'].items()}
        
        self.messages = data['messages']

        def add_to_synonyms(wordslist):
            for words in wordslist:
                self.synonyms.update({word: self.synonyms.setdefault(word, set()) | set(words) for word in words})
            
        self.synonyms = {}
        add_to_synonyms(data['words'])
        add_to_synonyms([noun.get('words', []) for noun in data['nouns'].values()])
        
        self.locations = set()
        for noun in self.nouns.values():
            self.locations |= set((noun.id, loc) for loc in noun.locs)

        self.current_room = next(room for room in self.rooms.values() if room.is_start())
        self.current_room.visit()

        self.turns = []
        self.gameover = False
        
        
    def add_filters(self, filters):
        """Store tests that can be used as filters for nouns."""
        self.filters = filters


    # turn management
    
    def start_turn(self, command):
        self.current_turn = {'command': command, 'output': []}
        self.set_words(command)
        
        
    def set_words(self, command):
        self.current_turn['words'] = [word for word in command.strip().split()
                                      if word not in ('the', 'a', 'an')]
        
    
    def end_turn(self, actions):
        self.current_turn['actions'] = actions
        self.turns.append(self.current_turn)
        return self.current_turn['output']


    def get_turn(self):
        return len(self.turns)
    
    
    def end_game(self):
        self.gameover = True
    
    
    # word matching
    
    def sub_input_words(self, phrase):
        """Substitute %1, %2, etc. in phrase with words from the input command."""
        sub_input = lambda m: (self.current_turn['words'][int(m.group(1)) - 1]
                               if len(self.current_turn['words']) >= int(m.group(1)) else '')
        #logging.debug('substituting from: %s to: %s', phrase, re.sub('%(\d+)', sub_word, phrase))  
        return re.sub('%(\d+)', sub_input, phrase)
    
    
    def match_word(self, inputword, word):
        """Check if an input word is a synonym of another word."""
        inputword = self.sub_input_words(inputword)
        return word == '*' or any(inputword in self.synonyms.get(word, []) for word in word.split('|'))
    
    
    def input_matches(self, words):
        """Check if a phrase matches the words from the input command."""
        return (len(self.current_turn['words']) >= len(words) and
                all(self.match_word(self.current_turn['words'][i], word) for i, word in enumerate(words)))
    
    
    # object matching
    
    def match_nouns(self, nword):
        """Return a set of nouns matching an input. If input is a noun ID or a
        comma-separated list of IDs, the set will contain said noun or nouns.
        If an input wildcard is passed, it will contain all nouns matching that
        input word. If a filter is specified after the wildcard, the results
        will be narrowed based on whether they pass the corresponding test."""

        def filter_is_true(nid, test):
            """Run a test on a particular noun, passed by ID."""
            try:
                tmethod = self.filters[test.lstrip('!')]
            except KeyError:
                return True
            
            return tmethod(nid) ^ (test[0] == '!') # negate if test starts with !
            
        def get_matching_nouns(iword):
            return (self.get_nouns_by_name(self.sub_input_words(nword)) if nword[0] == '%'
                    else filter(bool, (self.nouns.get(nid) for nid in nword.split(','))))
            
        if ':' in nword:
            # filter matching nouns using tests
            nword, tests = nword.split(':', 1)
            return set(noun for noun in get_matching_nouns(nword)
                       if all(filter_is_true(noun.id, test) for test in tests.split(':')))
        else:
            return get_matching_nouns(nword)
        
        
    def match_objects(self, oword=None):
        """Return a set containing either a single room (default the current room)
        or a number of nouns or a room matching the given word or id."""
        return set([self.current_room]
                    if oword is None or oword == '%current_room'
                    else (self.match_nouns(oword) or
                          filter(bool, [self.rooms.get(oword)])))
        
        
    # message queueing
    
    def queue_output(self, *messages):
        """Add a string or list of strings to the output queue."""
        for msg in messages:
            msg = re.sub('%VAR\((.+?)\)', lambda m: str(self.vars[m.group(1)]), msg)
            msg = msg.replace('%TURNS', str(self.get_turn()))
            self.current_turn['output'].append(self.sub_input_words(msg))
            
            
    def queue_message(self, *mids):
        """Get a message from the list and queue it for output,
        optionally replacing one or more substrings passed in a dict."""
        for mid in mids:
            self.queue_output(self.messages[mid])
    
    
    # room actions
    
    def go_to_room(self, rid):
        self.current_room = self.rooms[rid]
        self.rooms[rid].visit()
        
        
    # noun queries
        
    def get_nouns_by_name(self, *words):
        return set(noun for noun in self.nouns.values() if set(words) & set(noun.words))
    
    
    def get_noun_locs(self, noun):
        return set(oid for nid, oid in self.locations if nid == noun.id)
    
    
    def get_nouns_by_loc(self, *oids):
        return set(noun for noun in self.nouns.values() if set(oids) & self.get_noun_locs(noun))
    
    
    def is_noun_at(self, noun, *oids):
        return any((noun.id, oid) in self.locations for oid in oids)
    
    
    def has_contents(self, *oids):
        return any(oid in oids for _, oid in self.locations)
    
    
    def get_nouns_present(self):
        def get_noun_containers(noun, recursive=True):
            containers = set(self.nouns[nid] for nid in self.get_noun_locs(noun) & set(self.nouns.keys()))
            return (containers if not recursive else
                    containers.union(*(get_noun_containers(cont) for cont in containers)))
        
        return set(noun for noun in self.nouns.values()
                   if (self.get_noun_locs(noun).union(*(cont.get_locs() for cont in get_noun_containers(noun))) &
                       set([self.current_room.id, 'INVENTORY', 'WORN'])))
        
        
    # noun actions
    
    def add_noun(self, noun, *oids):
        self.locations |= set((noun.id, oid) for oid in oids)
        
    
    def remove_noun(self, noun, *oids):
        self.locations -= set((noun.id, oid) for oid in oids)
        
        
    def destroy_noun(self, noun):
        self.locations = set((nid, oid) for nid, oid in self.locations if nid != noun.id)
        
        
    def move_noun(self, noun, *oids):
        self.destroy_noun(noun)
        self.add_noun(noun, *oids)
    
    
    # variable actions
    
    def set_var(self, vid, value):
        self.vars[vid] = int(value)
        
