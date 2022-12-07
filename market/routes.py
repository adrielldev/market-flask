
from calendar import c
from crypt import methods
from flask import render_template,redirect,url_for,flash,get_flashed_messages,request
from market import app
from market.models import Item,User
from market import db
from market.forms import RegisterForm,LoginForm,PurchaseItemForm,SellItemForm
from flask_login import login_user,logout_user,login_required,current_user



@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')


@app.route('/market',methods=['POST','GET'])
@login_required
def market_page():
    purchase_form = PurchaseItemForm()
    selling_form = SellItemForm()
    if request.method == "POST":
        # purchase item logic
        purchased_item = request.form.get('purchased_item')
        p_item_object = Item.query.filter_by(name=purchased_item).first()
        if p_item_object:
            if current_user.can_purchase(p_item_object):
                p_item_object.buy(current_user)
                flash('Congratulations you purchased ' + p_item_object.name,category='success')
            else:
                flash('You dont have enough money',category='danger')

        # sell item logic
        sold_item = request.form.get('sold_item')
        s_item_object = Item.query.filter_by(name=sold_item).first()
        if s_item_object:
            if current_user.can_sell(s_item_object):
                s_item_object.sell(current_user)
                flash('Congratulations you sell the item',category='success')
            else:
                flash('you are not the owner of the item',category='danger')

        return redirect(url_for('market_page'))


    if request.method == "GET":

        items = Item.query.filter_by(owner=None)
        owned_items =  Item.query.filter_by(owner=current_user.id)

        return render_template('market.html',items=items,purchase_form=purchase_form,owned_items = owned_items,selling_form=selling_form)

@app.route('/register',methods=['GET','POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                             email_address = form.email_address.data,
                             password= form.password1.data
                             )
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash('Account created now you are logged' + user_to_create.username,category='success')
        return redirect(url_for('market_page'))

    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(err_msg,category='danger')

    return render_template('register.html',form=form)

@app.route('/login',methods=['POST','GET'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password1.data):
            login_user(attempted_user)
            flash('Success! You are logged in as: ' + attempted_user.username,category='success' )
            return redirect(url_for('market_page'))
        else:
            flash('Username and password does not match',category='danger')
    return render_template('login.html',form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash('You have been logged out!',category='info')

    return redirect(url_for('home_page'))


