import logging
import textwrap

from advengine import Adventure


logging.basicConfig(filename='debug.log', level=logging.DEBUG)
#logging.basicConfig(level=logging.DEBUG)

gamefile = 'games/starflight.json'
adv = Adventure(gamefile)

command = ''
while True:
    output = adv.do_command(command)
    
    for msg in output:
        if msg == 'PAUSE':
            print
            raw_input('Press Enter to continue...')
            print
        else:
            print '\n'.join(textwrap.fill(para) for para in msg.splitlines())
    
    if adv.is_game_over():
        break
    
    print
    print '>',
    command = raw_input().strip()
