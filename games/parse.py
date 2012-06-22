import xml.etree.ElementTree as xml
#import yaml

from collections import OrderedDict
import json
#import pprint
import re


title = 'starflight'

game = xml.parse('games/{0}.xml'.format(title))

# rooms

rooms = {}
for rdata in game.find('rooms'):
    room = dict(rdata.items())
    room.update({item.tag: item.text for item in rdata if item.text})
    room['exits'] = {exit.get('dir'): exit.get('room') for exit in rdata.findall('exit')}
    for k, v in room.iteritems():
        if v == '1':
            room[k] = True
    rooms[room.pop('id')] = room

# nouns
    
nouns = {}
for ndata in game.find('nouns'):
    noun = dict(ndata.items())
    noun.update({item.tag: item.text for item in ndata if item.text})
    if 'words' in noun:
        noun['words'] = ndata.find('words').text.split(',')
    if ndata.find('loc') is not None:
        noun['loc'] = [loc.get('id') for loc in ndata.findall('loc')]
    for k, v in noun.iteritems():
        if v == '1':
            noun[k] = True
    nouns[noun.pop('id')] = noun

# words, variables, messages
    
words = [word.text.split(',') for word in game.find('words').findall('word')]
vars = {var.get('id'): int(var.get('value')) for var in game.find('vars')}
messages = {msg.get('id'): msg.text for msg in game.find('messages')}

# control trees (were called conds)

def get_control(cdata):
    control = OrderedDict()
    
    # get if conditions
    idata = cdata.findall('if')
    if len(idata) > 1:
        control['if'] = [i.text.split(',') for i in idata]
    elif len(idata) == 1:
        control['if'] = idata[0].text.split(',')
    
    # collect actions, and sub condition blocks
    control['then'] = []
    for child in cdata:
        if child.tag == 'action':
            control['then'].append(child.text)
        elif child.tag == 'cond':
            control['then'].append(get_control(child))
    
    # add other flags
    flags = ('done', 'gameover')
    control.update({cdata.find(flag).tag: True for flag in flags if cdata.find(flag) is not None})
    
    return control
    
controls = [[get_control(cdata) for cdata in controlset] for controlset in game.find('conds')]


# generate json file

gamedata = OrderedDict([
        ('rooms', rooms),
        ('nouns', nouns),
        ('words', words),
        ('vars', vars),
        ('messages', messages),
        ('controls', controls)
        ])

jsn = json.dumps(gamedata, indent=4)

# remove prettyprinting for bottom-level lists (personal formatting preference)
pattern, repl = r'\[(("[^"]*",\s)*)\s*("[^"]*"(,\s)?)\s+(("[^"]*",?\s*)*)\]', r'[\1\3\5]'
while re.search(pattern, jsn) is not None:
    jsn = re.sub(pattern, repl, jsn)
    
with open('games/{0}.json'.format(title), 'wb') as jsonfile:
    jsonfile.write(jsn)


# generate yaml file

#with open('starflight.yml', 'wb') as yml:
#    yml.write(yaml.dump(starflight, indent=4))

    
    