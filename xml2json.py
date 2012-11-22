import logging

from advengine import datafile


logging.basicConfig(level=logging.DEBUG)

df = datafile.DataFile()
df.convert_file('./games/starflight.xml', 'json', './games/starflight.json')
