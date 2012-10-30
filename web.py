from flask import Flask
from flask import g, jsonify, redirect, render_template, request, session, url_for

from simplekv.memory import DictStore
from flaskext.kvsession import KVSessionExtension

from advengine.adventure import Adventure


store = DictStore()

app = Flask(__name__)
app.secret_key = '\xaau!uhb\xec\x87\xcd\x94\x1d\xbf\x8eF/\x92|\x87\xcbko\xf1\xda3'

KVSessionExtension(store, app)


def do_turn(input):
    print 'do_turn'
    
    if session['queue']:
        status, output = session['queue']
        session['queue'] = None
    else:
        status, output = g.adv.do_command(input)
        session['state'] = g.adv.export_state()
    
    if 'PAUSE' in output:
        i = output.index('PAUSE') + 1
        session['queue'] = (status, output[i:])
        output = output[:i]

    session['history'].append((input, output))
    
    
@app.before_first_request
def init_adventure():
    print 'init_adv'
    g.adv = Adventure('games/starflight.json')
    session['history'] = []
    session['queue'] = None
    do_turn('')
    
    
@app.route('/')
def index():
    print 'index'
    return render_template('game.html', title='Starflight', history=session['history'])


@app.route('/command', methods=['post'])
def do_command():
    print 'do_command'
    g.adv = Adventure('games/starflight.json', session['state'])
    do_turn(request.form.get('command'))
    return redirect(url_for('index'))


@app.route('/fetch', methods=['post'])
def do_ajax_command():
    print 'do_ajax_command'
    g.adv = Adventure('games/starflight.json', session['state'])
    output = do_turn(request.form.get('command'))
    return jsonify({'output': output})



if __name__ == '__main__':  
    app.debug = True
    app.run()
