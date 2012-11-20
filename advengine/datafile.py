from collections import OrderedDict as odict
import json
import os
import re
from xml.dom import minidom
import xml.etree.ElementTree as xml
import yaml


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
        
        
    def convert_file(self, gamepath, ext, outpath=None):
        data = self.import_file(gamepath)
        if ext == 'json':
            outdata = self.export_json(data)
        elif ext in ('yaml', 'yml'):
            outdata = self.export_yaml(data)
        elif ext == 'xml':
            outdata = self.export_xml(data)
        else:
            raise ValueError('Invalid or unrecognized file type')
        
        if outpath is None:
            outpath = '{0}.{1}'.format(os.path.basename(gamepath).rsplit('.', 1)[0], ext)
        with open(outpath, 'wb') as outfile:
            outfile.write(outdata)
        
        
    def import_file(self, gamepath):
        ext = gamepath.rsplit('.', 1)[1]
        if ext == 'json':
            return self.import_json(gamepath)
        elif ext in ('yaml', 'yml'):
            return self.import_yaml(gamepath)
        elif ext == 'xml':
            return self.import_xml(gamepath)        
        else:
            raise ValueError('Invalid or unrecognized file type')
    
    
    def import_json(self, gamepath):
        with open(gamepath, 'rb') as gamefile:
            return json.load(gamefile, object_pairs_hook=odict)


    def export_json(self, data):
        jsondata = json.dumps(data, indent=4)
        
        # remove prettyprinting for bottom-level lists (personal formatting preference)
        pattern, repl = r'\[(("[^"]*",\s)*)\s*("[^"]*"(,\s)?)\s+(("[^"]*",?\s*)*)\]', r'[\1\3\5]'
        while re.search(pattern, jsondata) is not None:
            jsondata = re.sub(pattern, repl, jsondata)

        return jsondata
    
    
    def import_yaml(self, gamepath):
        with open(gamepath, 'rb') as gamefile:
            return yaml.load(gamefile)
    
    
    def export_yaml(self, data):
        def contains_composites(seq):
            return seq and not any(isinstance(x, list) or isinstance(x, odict) for x in seq)
        
        yaml.add_representer(odict, lambda dumper, data:
                             dumper.represent_mapping('tag:yaml.org,2002:map', data.items(), False))
        yaml.add_representer(unicode, lambda dumper, data:
                             dumper.represent_scalar('tag:yaml.org,2002:str', data))
        yaml.add_representer(list, lambda dumper, data:
                             dumper.represent_sequence('tag:yaml.org,2002:seq', data,
                                                       contains_composites(data)))

        yamldata = yaml.dump(data, indent=4)
         
        return yamldata

    
    def import_xml(self, gamepath):
        data = xml.parse(gamepath)
        
        def get_room(rdata):
            room = odict(rdata.items())
            room.update({item.tag: item.text for item in rdata if item.text})
            room['exits'] = {ex.get('dir'): ex.get('room') for ex in rdata.findall('exit')}
            room['notes'] = [note.get('id') for note in rdata.findall('note')]
            for k, v in room.iteritems():
                if v == '1':
                    room[k] = True
            return room.pop('id'), room

            
        def get_noun(ndata):
            noun = odict(ndata.items())
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
        

    def export_xml(self, data):
        root = xml.Element('adventure')
        
        rooms = xml.SubElement(root, 'rooms')
        for rid, rdata in data['rooms'].items():
            room = xml.SubElement(rooms, 'room')
            room.set('id', rid)
            if 'start' in rdata:
                room.set('start', '1')
            for sub in set(['name', 'desc']) & set(rdata):
                xml.SubElement(room, sub).text = rdata[sub]
            for mid in rdata.get('notes', []):
                xml.SubElement(room, 'note').set('id', mid)
            for exitdir, exid in rdata.get('exits', {}).items():
                ex = xml.SubElement(room, 'exit')
                ex.set('dir', exitdir)
                ex.set('room', exid)
                
        nouns = xml.SubElement(root, 'nouns')
        for nid, ndata in data['nouns'].items():
            noun = xml.SubElement(nouns, 'noun')
            noun.set('id', nid)
            for flag in set(['visible', 'movable', 'wearable']) & set(ndata):
                noun.set(flag, '1')
            for sub in set(['name', 'desc', 'shortname', 'shortdesc']) & set(ndata):
                xml.SubElement(noun, sub).text = ndata[sub]
            for loc in ndata.get('locs', []):
                xml.SubElement(noun, 'loc').set('id', loc)
            if 'words' in ndata:
                xml.SubElement(noun, 'words').text = ','.join(ndata['words'])
                
        words = xml.SubElement(root, 'words')
        for wordlist in data['words']:
            xml.SubElement(words, 'word').text = ','.join(wordlist)
            
        variables = xml.SubElement(root, 'vars')
        for vid, value in data['vars'].items():
            var = xml.SubElement(variables, 'var')
            var.set('id', vid)
            var.set('value', str(value))
            
        messages = xml.SubElement(root, 'messages')
        for mid, message in data['messages'].items():
            msg = xml.SubElement(messages, 'message')
            msg.set('id', mid)
            msg.text = message
        
        
        def create_cond(cond):
            condtag = xml.Element('cond')
            for test in cond.get('if', []):
                if isinstance(test, list):
                    for subtest in test:
                        xml.SubElement(condtag, 'if').text = subtest
                else:
                    xml.SubElement(condtag, 'if').text = test
            for action in cond.get('then', []):
                if isinstance(action, dict):
                    condtag.append(create_cond(action))
                else:
                    xml.SubElement(condtag, 'action').text = action
            for flag in set(['done', 'gameover']) & set(cond):
                xml.SubElement(condtag, flag)
            return condtag
            
        controls = xml.SubElement(root, 'controls')
        for condset in data['controls']:
            cset = xml.SubElement(controls, 'condset')
            for cond in condset:
                cset.append(create_cond(cond))
        
        
        return minidom.parseString(xml.tostring(root)).toprettyxml(indent='\t', encoding='UTF-8')


