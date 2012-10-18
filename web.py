from flask import Flask
from flask import g, redirect, render_template, request, session, url_for

from advengine.adventure import Adventure


app = Flask(__name__)
app.secret_key = '\xaau!uhb\xec\x87\xcd\x94\x1d\xbf\x8eF/\x92|\x87\xcbko\xf1\xda3'


@app.before_request
def init_adventure():
    g.adv = Adventure('games/starflight.json')
    status, session['output'] = g.adv.do_command('')
    
    
@app.route('/')
def index():
    print session['output']
    return render_template('game.html', title='Starflight', output=session['output'])


@app.route('/command', methods=['post'])
def do_command():
    status, session['output'] = g.adv.do_command(request.form.get('command'))
    print session['output']
    return redirect(url_for('index'))



if __name__ == '__main__':  
    app.debug = True
    app.run()
