from flask import Flask, render_template, request, redirect, jsonify, url_for, abort, g, session, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, Category, ListItem, User

import sys
import codecs
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
from flask import make_response
import requests
import json

sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = "super secret key"

engine = create_engine('sqlite:///catalog.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
dbSession = DBSession()


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']


# function to login with provider used in the course
@app.route('/oauth/<provider>', methods=['POST'])
def login(provider):
    auth_code = request.json.get('code')
    if provider == 'google':
        try:
            oauth_flow = flow_from_clientsecrets(
                'client_secrets.json', scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(auth_code)
        except FlowExchangeError:
            response = make_response(json.dumps(
                'Failed to upgrade the authorization code.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        access_token = credentials.access_token
        url = (
            'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])
        if result.get('error') is not None:
            response = make_response(json.dumps(result.get('error')), 500)
            response.headers['Content-Type'] = 'application/json'

        h = httplib2.Http()
        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {'access_token': credentials.access_token, 'alt': 'json'}
        answer = requests.get(userinfo_url, params=params)

        data = answer.json()
        email = data['email']

        user = dbSession.query(User).filter_by(email=email).first()
        if not user:
            user = User(email=email)
            dbSession.add(user)
            dbSession.commit()

        token = user.generate_auth_token(600)
        session['profile'] = token
        session['logged_in'] = True
        print session['logged_in']
        return jsonify({'token': token.decode('ascii')})
    else:
        return 'Unrecoginized Provider'


@app.route('/login', methods=['POST', 'GET'])
def emailLogin():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        user = dbSession.query(User).filter_by(
            email=request.form['email']).first()
        if user:
            if user.verify_password(request.form['password']):
                session['logged_in'] = True
                return categories()
            else:
                flash('Check user password')
                return redirect(url_for('emailLogin'))
        else:
            flash('User does not exist')
            return redirect(url_for('emailLogin'))


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    if request.method == 'GET':
        return render_template('sure.html')
    if request.method == 'POST':
        session['logged_in'] = False
        return redirect(url_for('categories'))


@app.route('/signup', methods=['POST', 'GET'])
def new_user():
    if request.method == 'GET':
        return render_template('signup.html')
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email is None or password is None:
            flash('check email and password!')
            return redirect(url_for('new_user'))

        if dbSession.query(User).filter_by(email=email).first() is not None:
            user = dbSession.query(User).filter_by(email=email).first()
            flash('User already exsist!')
            return redirect(url_for('new_user'))

        user = User()
        user.email = email
        user.hash_password(password)
        dbSession.add(user)
        dbSession.commit()
        session['logged_in'] = True
        return redirect(url_for('categories'))


# HTML endpoints


@app.route('/')
def categories():
    if(session['logged_in']):
        categories = dbSession.query(Category).all()
        return render_template('categories.html', categories=categories, logged=session['logged_in'])
    else:
       return redirect(url_for('emailLogin'))     

@app.route('/catalog/new/', methods=['GET', 'POST'])
def newCategory():
    if session['logged_in']:
        if request.method == 'GET':
            return render_template('newCategory.html')
        if request.method == 'POST':
            name = request.form['name']
            newCategory = Category(name=unicode(name))
            dbSession.add(newCategory)
            dbSession.commit()
            return redirect(url_for('categories'))
    else:
        return redirect(url_for('emailLogin'))


@app.route('/catalog/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    if session['logged_in']:
        if request.method == 'GET':
            category = dbSession.query(
                Category).filter_by(id=category_id).one()
            return render_template('editCategory.html', category=category)
        if request.method == 'POST':
            category = dbSession.query(
                Category).filter_by(id=category_id).one()
            name = request.form['name']
            if name:
                category.name = name
            dbSession.add(category)
            dbSession.commit()
            return redirect(url_for('category', category_id=category_id))
    else:
        return redirect(url_for('emailLogin'))


@app.route('/catalog/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    if session['logged_in']:
        if request.method == 'GET':
            category = dbSession.query(
                Category).filter_by(id=category_id).one()
            return render_template('deleteCategory.html', category=category)
        if request.method == 'POST':
            category = dbSession.query(
                Category).filter_by(id=category_id).one()
            dbSession.delete(category)
            dbSession.commit()
            return redirect(url_for('categories'))
    else:
        return redirect(url_for('emailLogin'))


@app.route('/catalog/<int:category_id>/', methods=['GET'])
def category(category_id):
    print session['logged_in']
    if session['logged_in']:
        category = dbSession.query(Category).filter_by(id=category_id).one()
        items = dbSession.query(ListItem).filter_by(
            category_id=category.id).all()
        return render_template('category.html', category=category, items=items)
    else:
        return redirect(url_for('emailLogin'))


@app.route('/catalog/<int:category_id>/item/new/', methods=['GET', 'POST'])
def newListItem(category_id):
    if session['logged_in']:
        if request.method == 'GET':
            category = dbSession.query(
                Category).filter_by(id=category_id).one()
            return render_template('newItem.html', category=category)
        if request.method == 'POST':
            category = dbSession.query(
                Category).filter_by(id=category_id).one()
            description = request.form['description']
            name = request.form['name']
            listItem = ListItem(name=unicode(name), description=unicode(
                description), category_id=category.id)
            dbSession.add(listItem)
            dbSession.commit()
            return redirect(url_for('category', category_id=category_id))
    else:
        return redirect(url_for('emailLogin'))


@app.route('/catalog/<int:category_id>/item/<int:list_item_id>/edit/', methods=['GET', 'POST'])
def editListItem(category_id, list_item_id):
    if session['logged_in']:
        if request.method == 'GET':
            category = dbSession.query(
                Category).filter_by(id=category_id).one()
            item = dbSession.query(ListItem).filter_by(
                category_id=category.id, id=list_item_id).one()
            return render_template('editItem.html', category=category, item=item)
        if request.method == 'POST':
            category = dbSession.query(
                Category).filter_by(id=category_id).one()
            item = dbSession.query(ListItem).filter_by(
                category_id=category.id, id=list_item_id).one()
            description = request.form['description']
            name = request.form['name']
            if description:
                item.description = description
            if name:
                item.name = name
            dbSession.add(item)
            dbSession.commit()
            return redirect(url_for('category', category_id=category_id))
    else:
        return redirect(url_for('emailLogin'))


@app.route('/catalog/<int:category_id>/item/<int:list_item_id>/delete/', methods=['GET', 'POST'])
def deleteListItem(category_id, list_item_id):
    if session['logged_in']:
        category = dbSession.query(Category).filter_by(id=category_id).one()
        item = dbSession.query(ListItem).filter_by(
            category_id=category.id, id=list_item_id).one()
        if request.method == 'GET':
            category = dbSession.query(
                Category).filter_by(id=category_id).one()
            item = dbSession.query(ListItem).filter_by(
                category_id=category.id, id=list_item_id).one()
            return render_template('deleteItem.html', category=category, item=item)
        if request.method == 'POST':
            category = dbSession.query(
                Category).filter_by(id=category_id).one()
            item = dbSession.query(ListItem).filter_by(
                category_id=category.id, id=list_item_id).one()
            dbSession.delete(item)
            dbSession.commit()
            return redirect(url_for('category', category_id=category_id))
    else:
        return redirect(url_for('emailLogin'))
# JSON endpoints


@app.route('/JSON/')
def categoriesJSON():
    if session['logged_in']:
        categories = dbSession.query(Category).all()
        return jsonify({'categories': [c.serialize for c in categories]})
    else: 
         return redirect(url_for('emailLogin'))   

@app.route('/catalog/new/JSON/', methods=['POST'])
def newCategoryJSON():
    if request.method == 'POST':
        name = request.form['name']
        category = Category(name=unicode(name))
        dbSession.add(category)
        dbSession.commit()
        return redirect(url_for('categoriesJSON'))


@app.route('/catalog/<int:category_id>/edit/JSON/', methods=['POST'])
def editCategoryJSON(category_id):
    if request.method == 'POST':
        category = dbSession.query(Category).filter_by(id=category_id).one()
        name = request.form['name']
        if name:
            category.name = name
        dbSession.add(category)
        dbSession.commit()
        return redirect(url_for('categoryJSON', category_id=category_id))


@app.route('/catalog/<int:category_id>/delete/JSON/', methods=['POST'])
def deleteCategoryJSON(category_id):
    if request.method == 'POST':
        category = dbSession.query(Category).filter_by(id=category_id).one()
        dbSession.delete(category)
        dbSession.commit()
        return redirect(url_for('categoriesJSON'))


@app.route('/catalog/<int:category_id>/JSON/', methods=['GET'])
def categoryJSON(category_id):
    category = dbSession.query(Category).filter_by(id=category_id).one()
    items = dbSession.query(ListItem).filter_by(category_id=category.id).all()
    return jsonify({'category': category, 'items': [i.serialize for i in items]})


@app.route('/catalog/<int:category_id>/item/new/JSON/', methods=['POST'])
def newListItemJSON(category_id):
    if request.method == 'POST':
        category = dbSession.query(Category).filter_by(id=category_id).one()
        description = request.form['description']
        name = request.form['name']
        item = ListItem(name=unicode(name), description=unicode(
            description), category_id=category.id)
        dbSession.add(item)
        dbSession.commit()
        return redirect(url_for('categoryJSON', category_id=category_id))


@app.route('/catalog/<int:category_id>/item/<int:list_item_id>/edit/JSON/', methods=['POST'])
def editListItemJSON(category_id, list_item_id):
    if request.method == 'POST':
        category = dbSession.query(Category).filter_by(id=category_id).one()
        item = dbSession.query(ListItem).filter_by(
            category_id=category.id, id=list_item_id).one()
        description = request.form['description']
        name = request.form['name']
        if description:
            item.description = description
        if name:
            item.name = name
        dbSession.add(item)
        dbSession.commit()
        return redirect(url_for('categoryJSON', category_id=category_id))


@app.route('/catalog/<int:category_id>/item/<int:list_item_id>/delete/JSON/', methods=['POST'])
def deleteListItemJSON(category_id, list_item_id):
    category = dbSession.query(Category).filter_by(id=category_id).one()
    item = dbSession.query(ListItem).filter_by(
        category_id=category.id, id=list_item_id).one()
    if request.method == 'POST':
        category = dbSession.query(Category).filter_by(id=category_id).one()
        item = dbSession.query(ListItem).filter_by(
            category_id=category.id, id=list_item_id).one()
        dbSession.delete(item)
        dbSession.commit()
        return redirect(url_for('categoryJSON', category_id=category_id))


if __name__ == '__main__':
    app.secret_key = 'catalog'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
