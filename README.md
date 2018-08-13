# Project Title

Item Catalog Application

## Getting Started

This application provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.

### Prerequisites

Things to install before using web application

1.Install Vagrant and VirtualBox
2.Download or clone the project from Github,store it locally
3.Python 3.5.2

### Installing

A step by step series of examples that tell you how to get a development env running

change directory where the file is stored

```
cd {file location}
```

installing vitual system on file location

```
vagrant up
```

getting logged into virtual machine

```
vagrant ssh
```

to access folder in VM

```
cd /vagrant
```

## Deployment

To start server

```
python project.py
```

Access website on any of your browser

```
http://localhost:5000
```

## URI

1.http://localhost:5000/categories(Displays all category in list)
  note:categories can't be modified

2.http://localhost:5000/categories/<int:category_id>/subcategories(displays subcategories of category)
    note:categories can't be modified

3.http://localhost:5000/categories/<int:category_id>/subcategories/<int:subcategory_id>/product(list the products under that subcategory)

4.http://localhost:5000/categories/<int:category_id>/subcategories/<int:subcategory_id>/product/<int:productdetail_id>/details(displays detail of the particular product)

5.http://localhost:5000/categories/<int:category_id>/subcategories/<int:subcategory_id>/product/create(add product to particular subcategory)

6.http://localhost:5000/categories/<int:category_id>/subcategories/<int:subcategory_id>/product/<int:productdetail_id>/edit(edit the particular product of id)

7.http://localhost:5000/categories/<int:category_id>/subcategories/<int:subcategory_id>/product/<int:productdetail_id>/delete(delete the product of particular sub-category)


## API Endpoints

/categories/JSON/  (Return all the categories)


/categories/<int:category_id>/subcategories/<int:subcategory_id>/product/JSON/  (Returns all the subcategories)


/categories/<int:category_id>/subcategories/<int:subcategory_id>/product/<int:productdetail_id>/details/JSON/  (Displays all product details in particular list)


## Note

if having issues while logging out.Please clear cache and cookies then try again.


## Acknowledgments

* www.stackoverflow.com
