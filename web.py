from flask import Flask
from flask import g, redirect, render_template, request, session, url_for

from advengine.adventure import Adventure


app = Flask(__name__)
app.secret_key = '\xaau!uhb\xec\x87\xcd\x94\x1d\xbf\x8eF/\x92|\x87\xcbko\xf1\xda3'


def do_turn(input):
    status, output = g.adv.do_command(input)
    session['status'] = status
    session['history'].append((input, output))
    session.modified = True
    
    
@app.before_first_request
def init_adventure():
    g.adv = Adventure('games/starflight.json')
    session['state'] = g.adv.export_state()
    session['history'] = []
    do_turn('')


@app.before_request
def init_request():
    g.adv = Adventure('games/starflight.json', session['state'])
    
    
@app.route('/')
def index():
    return render_template('game.html', title='Starflight', history=session['history'])


@app.route('/command', methods=['post'])
def do_command():
    do_turn(request.form.get('command'))
    return redirect(url_for('index'))



if __name__ == '__main__':  
    app.debug = True
    app.run()
