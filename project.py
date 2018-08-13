from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
app = Flask(__name__)

from database_setup import Base, Categories, ProductType, Products, User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

# new step for authentication
from flask import session as login_session
import random
import string

# oauth library
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

import hmac
import hashlib
import os

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())[
    'web']['client_id']
APPLICATION_NAME = 'itemCatalog'

# Create session and connect to DB
engine = create_engine('sqlite:///catalognew.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = scoped_session(DBSession)


@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

# code to verify client identity


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


#authentication and authorization
# Creating log in path


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# google authentication and authorization
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1].decode('utf-8'))
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])
    print('this is user id' + str(user_id))
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output


def createUser(login_session):
    newUser = User(UserName=login_session['username'], Email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(Email=login_session['email']).one()
    return user.UserID


def getUserInfo(user_id):
    user = session.query(User).filter_by(UserID=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(Email=email).one()
        return user.UserID
    except:
        return None

# disconnects google account


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s' + access_token)
    print('User name is: ')
    print(login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session[
        'access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        flash('Successfully disconnected')
        return redirect(url_for('CategoryList'))

    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Displays all categories

@app.route('/')
@app.route('/categories')
def CategoryList():
    cat = session.query(Categories).all()
    return render_template('CategoryList.html', categotylistnew=cat)

# Display SubCategory List


@app.route('/categories/<int:category_id>/subcategories')
def ProductTypeList(category_id):
    subcat = session.query(ProductType).filter_by(
        category_id=category_id).all()
    return render_template('ProductTypeList.html', subList=subcat, category_id=category_id)

# Displays products under SubCategory


@app.route('/categories/<int:category_id>/subcategories/<int:subcategory_id>/product')
def ProductList(category_id, subcategory_id):
    prodid = session.query(ProductType).filter_by(
        category_id=category_id, ProductTypeID=subcategory_id).one()
    productfinal = session.query(Products).filter_by(
        product_id=prodid.ProductTypeID).all()
    if 'username' not in login_session:
        return render_template('ProductList-Public.html', productfinal=productfinal, category_id=category_id, subcategory_id=subcategory_id)
    else:
        return render_template('ProductList.html', productfinal=productfinal, category_id=category_id, subcategory_id=subcategory_id)


# Displays details of particular product

@app.route('/categories/<int:category_id>/subcategories/<int:subcategory_id>/product/<int:productdetail_id>/details')
def ProductDetail(category_id, subcategory_id, productdetail_id):
    prodid = session.query(ProductType).filter_by(
        category_id=category_id, ProductTypeID=subcategory_id).one()
    product_detail = session.query(Products).filter_by(
        product_id=prodid.ProductTypeID, ProductID=productdetail_id).all()
    return render_template('ProductDetail.html', product_detail=product_detail, category_id=category_id, subcategory_id=subcategory_id, productdetail_id=productdetail_id)


# Used to add products under SubCategory

@app.route('/categories/<int:category_id>/subcategories/<int:subcategory_id>/product/create', methods=['GET', 'POST'])
def AddProduct(category_id, subcategory_id):
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    prodid = session.query(ProductType).filter_by(
        category_id=category_id, ProductTypeID=subcategory_id).one()
    if request.method == 'POST':
        addnew = Products(ProductName=request.form['name'], ProductDescription=request.form[
                          'description'], product_id=prodid.ProductTypeID, user_id=login_session['user_id'])
        session.add(addnew)
        session.commit()
        flash('new item is added')
        return redirect(url_for('ProductList', category_id=category_id, subcategory_id=subcategory_id))
    else:
        return render_template('AddProduct.html', category_id=category_id, subcategory_id=subcategory_id)


# Edits the product under subcategory

@app.route('/categories/<int:category_id>/subcategories/<int:subcategory_id>/product/<int:productdetail_id>/edit', methods=['GET', 'POST'])
def EditProduct(category_id, subcategory_id, productdetail_id):
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    prodid = session.query(ProductType).filter_by(
        category_id=category_id, ProductTypeID=subcategory_id).one()
    prod_edit = session.query(Products).filter_by(
        product_id=prodid.ProductTypeID, ProductID=productdetail_id).one()
    if prod_edit.user_id != login_session['user_id']:
        return "<script>function myFunction(){alert('you are not allowed to edit this item,please make your own item');}</script><body onload = 'myFunction()'>"
    if request.method == 'POST':
        prod_edit.ProductName = request.form['name']
        prod_edit.ProductDescription = request.form['description']
        session.add(prod_edit)
        session.commit()
        flash('item edited successfully')
        return redirect(url_for('ProductList', category_id=category_id, subcategory_id=subcategory_id, productdetail_id=productdetail_id))
    else:
        return render_template('EditProduct.html', prod_edit=prod_edit, category_id=category_id, subcategory_id=subcategory_id, productdetail_id=productdetail_id)


# Delete products under subcategory

@app.route('/categories/<int:category_id>/subcategories/<int:subcategory_id>/product/<int:productdetail_id>/delete', methods=['GET', 'POST'])
def DeleteProduct(category_id, subcategory_id, productdetail_id):
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    prodid = session.query(ProductType).filter_by(
        category_id=category_id, ProductTypeID=subcategory_id).one()
    prod_delete = session.query(Products).filter_by(
        product_id=prodid.ProductTypeID, ProductID=productdetail_id).one()
    if prod_delete.user_id != login_session['user_id']:
        return "<script>function myFunction(){alert('you are not allowed to Delete this item,please make your own item');}</script><body onload = 'myFunction()'>"
    if request.method == 'POST':
        session.delete(prod_delete)
        session.commit()
        flash('item Deleted')
        return redirect(url_for('ProductList', category_id=category_id, subcategory_id=subcategory_id))
    else:
        return render_template('DeleteProduct.html', prod_delete=prod_delete, category_id=category_id, subcategory_id=subcategory_id, productdetail_id=productdetail_id)

# JSON API ENDPOINTS


@app.route('/categories/JSON/')
def CategoryListJSON():
    cat = session.query(Categories).all()
    return jsonify(categorylist=[i.serialize for i in cat])


@app.route('/categories/<int:category_id>/subcategories/JSON/')
def ProductTypeListJSON(category_id):
    subcat = session.query(ProductType).filter_by(
        category_id=category_id).all()
    return jsonify(productlist=[i.serialize for i in subcat])


@app.route('/categories/<int:category_id>/subcategories/<int:subcategory_id>/product/JSON/')
def ProductListJSON(category_id, subcategory_id):
    prodid = session.query(ProductType).filter_by(
        category_id=category_id, ProductTypeID=subcategory_id).one()
    productfinal = session.query(Products).filter_by(
        product_id=prodid.ProductTypeID).all()
    return jsonify(productdetail=[i.serialize for i in productfinal])


@app.route('/categories/<int:category_id>/subcategories/<int:subcategory_id>/product/<int:productdetail_id>/details/JSON/')
def ProductDetailJSON(category_id, subcategory_id, productdetail_id):
    if request.method == 'GET':
        prodid = session.query(ProductType).filter_by(
            category_id=category_id, ProductTypeID=subcategory_id).one()
        product_detail = session.query(Products).filter_by(
            product_id=prodid.ProductTypeID, ProductID=productdetail_id).all()
        return jsonify(product=[i.serialize for i in product_detail])


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
