from flask import abort, flash, jsonify, redirect, render_template, request, url_for

from app import app
from bot import get_callback
from forms import LoginForm, RegisterForm


@app.route('/')
@app.route('/index')
def index():
    return 'Samson Society'


@app.route('/bot/callback/<callback_message>', methods=['GET', 'POST'])
def bot_callback(callback_message):
    callback = get_callback(callback_message)
    return callback_message


#@app.route('/bot/post')
#@login_required
#def bot_post():
    #return render_template('bot_post.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.POST)
    if form.validate_on_submit():
        remember_me = form.remember_me.data
        login_user(user, remember=remember_me)

        flash('Logged in Successfully.')
        next = request.args.get('next')
        if not next_is_valid(next):
            return abort(400)

        return redirect(next or url_for('index'))
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.POST)
    if form.validate_on_submit():
        remember_me = form.remember_me.data
        login_user(user, remember=remember_me)

        flash('Registered Successfully.')
        next = request.args.get('next')
        if not next_is_valid(next):
            return abort(400)

        return redirect(next or url_for('index'))
    return render_template('register.html', form=form)
