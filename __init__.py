import errno
import os

from flask import Flask
from flask import g, jsonify, redirect, render_template, request, session, url_for

from simplekv.fs import FilesystemStore
from flask.ext.kvsession import KVSessionExtension

from advengine.adventure import Adventure


app = Flask(__name__)
app.secret_key = '\xaau!uhb\xec\x87\xcd\x94\x1d\xbf\x8eF/\x92|\x87\xcbko\xf1\xda3'

flask_dir = os.path.dirname(os.path.realpath(__file__))

try:
    os.makedirs(os.path.join(flask_dir, 'sessions'))
except OSError as exception:
    if exception.errno != errno.EEXIST:
        raise
        
store = FilesystemStore(os.path.join(flask_dir, 'sessions'))
KVSessionExtension(store, app)

game = 'starflight'
gamepath = os.path.join(flask_dir, 'games/{0}.json'.format(game))


def do_turn(input):
    if session['queue']:
        input = ''
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
    
    
def init_adventure():
    g.adv = Adventure(gamepath)
    session['history'] = []
    session['queue'] = None
    do_turn('')
    
    
@app.before_first_request
def before_first_req():
    init_adventure()
    
    
@app.route('/')
def index():
    return render_template('game.html', title='Starflight', history=session['history'])


@app.route('/command', methods=['post'])
def do_command():
    g.adv = Adventure(gamepath, session['state'])
    do_turn(request.form.get('command'))
    return redirect(url_for('index'))


@app.route('/fetch', methods=['post'])
def do_ajax_command():
    g.adv = Adventure(gamepath, session['state'])
    do_turn(request.form.get('command'))    
    input, output = session['history'][-1]
    return jsonify({'input': input, 'output': output})


@app.route('/newgame', methods=['get','post'])
def new_game():
    init_adventure()
    return redirect(url_for('index'))



if __name__ == '__main__':  
    app.debug = True
    app.run()
