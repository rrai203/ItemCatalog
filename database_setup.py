import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'userDetails'
    UserID = Column(Integer, primary_key=True)
    UserName = Column(String(500), nullable=False)
    Email = Column(String(350), nullable=False)
    picture = Column(String(250))


class Categories(Base):
    __tablename__ = 'Categories_list'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('userDetails.UserID'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'category_name': self.name,
        }


class ProductType(Base):
    __tablename__ = 'producttype_list'

    ProductTypeID = Column(Integer, primary_key=True)
    ProductTypeName = Column(String(250))
    category_id = Column(Integer, ForeignKey('Categories_list.id'))
    categories = relationship("Categories")
    user_id = Column(Integer, ForeignKey('userDetails.UserID'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'id': self.ProductTypeID,
            'Subcategory_name': self.ProductTypeName,
        }


class Products(Base):
    __tablename__ = 'products_list'
    ProductID = Column(Integer, primary_key=True)
    ProductName = Column(String(250))
    ProductDescription = Column(String(350))
    product_id = Column(Integer, ForeignKey('producttype_list.ProductTypeID'))
    product_type = relationship("ProductType")
    user_id = Column(Integer, ForeignKey('userDetails.UserID'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'id': self.ProductID,
            'name': self.ProductName,
            'Description': self.ProductDescription,
        }


engine = create_engine('postgresql://catalog:catalog@localhost/catalog')


Base.metadata.create_all(engine)
