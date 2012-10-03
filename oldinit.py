from adventure import engine


title = 'starflight'

adv = engine.Engine('games/{0}.json'.format(title))

while True:
    print '>',
    command = raw_input()
    result = adv.do_turn(command)
    print result