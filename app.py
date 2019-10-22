from flask import (
    Flask, flash, g, redirect, render_template, request, url_for, session
)
from flask_login import (LoginManager, login_user, logout_user,
                             login_required, current_user)
from werkzeug.security import check_password_hash, generate_password_hash

import models
import forms

import datetime

DEBUG = True
PORT = 8000
HOST = '127.0.0.1'

app = Flask(__name__)
app.secret_key = 'auoesh.bouoastuh.43,uoausoehuosth3ououea.auoub!'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.session_protection = "strong"

@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    """Connect to the database befor each rquest."""
    g.db = models.DATABASE
    g.db.connect()

@app.after_request
def after_request(response):
    """Close database connection after each request."""
    g.db.close()
    return response

@app.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        models.User.create(
            name=form.name.data,
            username=form.username.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data)
        )
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("ایمیل یا رمز عبور اشتباه است")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('deck'))
            else:
                flash("ایمیل یا رمز عبور اشتباه است")
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/add', methods=('GET', 'POST'))
def add():
    try:
        current_user.name
    except:
        return render_template('not_access.html')

    try:
        if not models.Deck.select().where(models.Deck.user == current_user.username).exists():
            models.Deck.create(user=current_user.username, name="English", slug="English")
    except:
        pass

    if request.method == 'POST':
        deck = request.form['deck_select']
        front = request.form['front']
        back = request.form['back']
        error = None

        if not front:
            error = "لطفا کلمه رو وارد کن"

        elif not back:
            error = "لطفا معنی رو وارد کن"
        

        if deck != "None":
            query = models.Card.select().where(models.Card.deck==deck, 
            models.Card.front==front, 
            models.Card.user==current_user.username)

            if query.exists():
                error = "این کلمه وجود داره"
                
        if deck == "None":
            error = "لطفا دسته بندی رو انتخاب کن"

        if error is None:
            models.Card.create_card(user=current_user.username, deck=deck, front=front, back=back)
        else:
            flash(error)
        
    deck_options = models.Deck.select().where(models.Deck.user==current_user.username)

    return render_template('add.html', deck_options=deck_options)

@app.route('/review', methods=('GET', 'POST'))
def review():
    try:
        current_user.name
    except:
        return render_template('not_access.html')
        
    def convert_number(count):
        output = ''
        for n in str(count):    
            persian_numbers = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹']
            output += persian_numbers[int(n)]
        return output
        
    cards = models.Card.select().where(models.Card.date_add <= datetime.datetime.now(), 
            models.Card.user==current_user.username)
    try:
        card = models.Card.get(models.Card.date_add <= datetime.datetime.now(), 
                         models.Card.user==current_user.username)
        count = len(cards)
        persian_number = convert_number(count)
        new_cards = convert_number(len(models.Card.select().where(models.Card.level==1, 
                                       models.Card.date_add <= datetime.datetime.now(), 
                                       models.Card.user==current_user.username)))
    except:
        card = None
        persian_number = None
        new_cards = convert_number(len(cards.select().where(models.Card.level==1)))

    if request.method == 'POST':
        status = request.form['status']

        if status == 'بلدم':
            card.level = card.level * 2
            card.save()
        else:
            card.level = 1
            card.save()
        
        card.date_add = datetime.datetime.now() + datetime.timedelta(days=card.level)
        card.save()
    
    cards = models.Card.select().where(models.Card.date_add <= datetime.datetime.now(), 
            models.Card.user==current_user.username)
    try:
        card = models.Card.get(models.Card.date_add <= datetime.datetime.now(), 
                         models.Card.user==current_user.username)
        count = len(cards)
        persian_number = convert_number(count)
        new_cards = convert_number(len(models.Card.select().where(models.Card.level==1, 
                                       models.Card.date_add <= datetime.datetime.now(), 
                                       models.Card.user==current_user.username)))     
    except:
        card = None
        persian_number = None
        new_cards = convert_number(len(cards.select().where(models.Card.level==1)))

    return render_template('review.html', card=card, persian_number=persian_number, new_cards=new_cards)

@app.route('/deck', methods=("POST", "GET"))
def deck():
    try:
        current_user.name
    except:
        return render_template('not_access.html')

    decks = models.Deck.select().where(models.Deck.user==current_user.username)

    if request.method == "POST":
        deck_name = request.form["deckName"]
        name_edit = request.form['nameEdit']

        if name_edit:
            deck = models.Deck.get(models.Deck.name == deck_name)
            is_exists = models.Deck.select().where(models.Deck.name == name_edit, 
                                                   models.Deck.user == current_user.username).exists()
            if is_exists == False or deck_name == name_edit:                                      
                deck.name = name_edit
                deck.save()
            else:
                flash("این دسته وجود دارد")

    return render_template("deck.html", decks=decks)

@app.route('/deck/<slug>', methods=("POST", "GET"))
def deck_details(slug):
    try:
        current_user.name
    except:
        return render_template('not_access.html')

    name = slug.replace('-', '')
    deck = models.Deck.get(models.Deck.name==name, 
                           models.Deck.user==current_user.username)
    cards = models.Card.select().where(models.Card.deck==deck,
                                       models.Card.user==current_user.username)
    error = None

    if request.method == "POST":
        search_by = request.form['searchBy']
        query = request.form['query']

        if search_by == 'front':
            cards = models.Card.select().where(models.Card.deck==deck, 
                                               models.Card.front.contains(query),
                                               models.Card.user==current_user.username)
        else:
            cards = models.Card.select().where(models.Card.deck==deck, 
                                               models.Card.back.contains(query),
                                               models.Card.user==current_user.username
                                               )

        if len(cards) == 0:
            error = "کارتی پیدا نشد"
            
    flash(error)

    return render_template("deck_details.html", deck=deck, slug=slug, cards=cards)




if __name__ == "__main__":
    models.initialize()
    try:
        models.User.create(
            name = 'Adel',
            username = 'adel_mhz',
            email = 'adel.mohamadzadeph@gmail.com',
            password = generate_password_hash('password')
        )
    except:
        pass

    app.run(debug=DEBUG, host=HOST, port=PORT)

