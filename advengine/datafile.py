from collections import OrderedDict as odict
import json
import os
import re
import xml.etree.ElementTree as xml


class DataFile:
    def get_data(self, gamepath):
        data = self.import_file(gamepath)
        return {'rooms': data.get('rooms', {}),
                'nouns': data.get('nouns', {}),
                'words': data.get('words', []),
                'vars': data.get('vars', {}),
                'messages': data.get('messages', {}),
                'controls': data.get('controls', [])
                }
        
        
    def convert_file(self, gamepath, ext):
        gamedata = self.import_file(gamepath)
        if ext == 'json':
            outdata = self.export_json(gamedata)
        elif ext == 'xml':
            outdata = self.export_xml(gamedata)
        
        outpath = '{0}.{1}'.format(os.path.basename(gamepath).rsplit('.', 1)[0], ext)
        with open(outpath, 'wb') as outfile:
            outfile.write(outdata)
        
        
    def import_file(self, gamepath):
        ext = gamepath.rsplit('.', 1)[1]
        if ext == 'json':
            return self.import_json(gamepath)
        elif ext == 'xml':
            return self.import_xml(gamepath)        
        
    
    def import_json(self, gamepath):
        with open(gamepath, 'rb') as gamefile:
            return json.load(gamefile, object_pairs_hook=odict)


    def export_json(self, gamedata):
        jsondata = json.dumps(gamedata, indent=4)
        
        # remove prettyprinting for bottom-level lists (personal formatting preference)
        pattern, repl = r'\[(("[^"]*",\s)*)\s*("[^"]*"(,\s)?)\s+(("[^"]*",?\s*)*)\]', r'[\1\3\5]'
        while re.search(pattern, jsondata) is not None:
            jsondata = re.sub(pattern, repl, jsondata)

        return jsondata
    
    
    def import_xml(self, gamepath):
        data = xml.parse(gamepath)
        
        def get_room(rdata):
            room = dict(rdata.items())
            room.update({item.tag: item.text for item in rdata if item.text})
            room['exits'] = {ex.get('dir'): ex.get('room') for ex in rdata.findall('exit')}
            room['notes'] = [note.get('id') for note in rdata.findall('note')]
            for k, v in room.iteritems():
                if v == '1':
                    room[k] = True
            return room.pop('id'), room

            
        def get_noun(ndata):
            noun = dict(ndata.items())
            noun.update({item.tag: item.text for item in ndata if item.text})
            if 'words' in noun:
                noun['words'] = ndata.find('words').text.split(',')
            for opt in ('loc', 'note'):
                if ndata.find(opt) is not None:
                    noun['{0}s'.format(opt)] = [tag.get('id') for tag in ndata.findall(opt)]
            for k, v in noun.iteritems():
                if v == '1':
                    noun[k] = True
            return noun.pop('id'), noun

        
        def get_control(cdata):
            control = odict()
            
            # get if conditions
            idata = cdata.findall('if')
            if len(idata) > 1:
                control['if'] = [i.text.split(',') for i in idata]
            elif len(idata) == 1:
                control['if'] = idata[0].text.split(',')
            
            if cdata.find('replace') is not None:
                # add command replacements
                control['replace'] = cdata.find('replace').text
            else: 
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

        
        return odict([('rooms', odict(get_room(rdata) for rdata in data.find('rooms'))),
                      ('nouns', odict(get_noun(ndata) for ndata in data.find('nouns'))),
                      ('words', [word.text.split(',') for word in data.find('words').findall('word')]),
                      ('vars', odict((var.get('id'), int(var.get('value')))
                                     for var in data.find('vars'))),
                      ('messages', odict((msg.get('id'), msg.text)
                                         for msg in data.find('messages'))),
                      ('controls', [[get_control(cdata) for cdata in controlset]
                                    for controlset in data.find('conds')])
                      ])
        

    def export_xml(self, gamedata):
        root = xml.Element('adventure')
        
        
        
        return root.dump()

    
        