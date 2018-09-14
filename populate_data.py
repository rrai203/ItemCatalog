from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Categories, Base, ProductType, Products, User

engine = create_engine('postgresql://catalog:catalog@localhost/catalog')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

profile1 = User(UserName="preeti rai", Email="preeti@gmail.com")
session.add(profile1)
session.commit()

newcategory = Categories(name="Books", user_id=profile1.UserID)
session.add(newcategory)
session.commit()

producttype1 = ProductType(ProductTypeName="Fiction Books",
                           categories=newcategory, user_id=profile1.UserID)
session.add(producttype1)
session.commit()


producttype2 = ProductType(ProductTypeName="Children's Books",
                           categories=newcategory, user_id=profile1.UserID)
session.add(producttype2)
session.commit()

producttype3 = ProductType(ProductTypeName="School Textbooks",
                           categories=newcategory, user_id=profile1.UserID)
session.add(producttype2)
session.commit()

producttype4 = ProductType(
    ProductTypeName="Used Books", categories=newcategory, user_id=profile1.UserID)
session.add(producttype2)
session.commit()


newcategory1 = Categories(name="Movie & Music", user_id=profile1.UserID)
session.add(newcategory)
session.commit()

producttype1 = ProductType(ProductTypeName="Blu-ray",
                           categories=newcategory1, user_id=profile1.UserID)
session.add(producttype1)
session.commit()


producttype2 = ProductType(ProductTypeName="English movies",
                           categories=newcategory1, user_id=profile1.UserID)
session.add(producttype2)
session.commit()

producttype3 = ProductType(ProductTypeName="Hindi movies",
                           categories=newcategory1, user_id=profile1.UserID)
session.add(producttype2)
session.commit()


print("data added")
