import logging
import textwrap

from advengine import Adventure

gamefile = 'games/starflight.json'
adv = Adventure(gamefile)

logging.basicConfig(filename='debug.log', level=logging.DEBUG)

command = ''
while True:
    status, output = adv.do_command(command)
    
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
            
            
