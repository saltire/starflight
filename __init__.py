import logging
import textwrap

import adventure

gamefile = 'games/starflight.json'
adv = adventure.Adventure(gamefile)

#logging.basicConfig(level=logging.DEBUG)

command = ''
while True:
    status, output = adv.do_turn(command)
    
    for msg in output:
        if msg == 'PAUSE':
            print
            raw_input('Press Enter to continue...')
            print
        else:
            print '\n'.join(textwrap.fill(para) for para in msg.splitlines())
    
    if status == 'gameover':
        break
    
    print
    print '>',
    command = raw_input().strip()
            
            
