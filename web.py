from flask import Flask
from flask import g, redirect, render_template, request, session, url_for

from simplekv.memory import DictStore
from flaskext.kvsession import KVSessionExtension

from advengine.adventure import Adventure


store = DictStore()

app = Flask(__name__)
app.secret_key = '\xaau!uhb\xec\x87\xcd\x94\x1d\xbf\x8eF/\x92|\x87\xcbko\xf1\xda3'

KVSessionExtension(store, app)


def do_turn(input):
    print 'do_turn'
    status, output = g.adv.do_command(input)
    session['history'].append((input, output))
    session['state'] = g.adv.export_state()
    session.modified = True
    
    
@app.before_first_request
def init_adventure():
    print 'init_adv'
    g.adv = Adventure('games/starflight.json')
    session['history'] = []
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



if __name__ == '__main__':  
    app.debug = True
    app.run()
