from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from database import Category, ListItem

engine = create_engine('sqlite:///catalogapp.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base = declarative_base()
Base.metadata.bind = engine


DBSession = sessionmaker(bind=engine)
# # A DBSession() instance establishes all conversations with the database
# # and represents a "staging zone" for all the objects loaded into the
# # database session object. Any change made against the objects in the
# # session won't be persisted into the database until you call
# # session.commit(). If you're not happy about the changes, you can
# # revert all of them back to the last commit by calling
# # session.rollback()
session = DBSession()

# session.query(Category).delete()
# session.query(ListItem).delete()

cat1 = Category(name="Shoes")

session.add(cat1)
session.commit()

listitem1 = ListItem(name="Sneakers", description="Great for every day use.",
                     category=cat1)

session.add(listitem1)
session.commit()


listitem2 = ListItem(name="Boots", description="Works best with dresses.",
                     category=cat1)

session.add(listitem2)
session.commit()

ListItem3 = ListItem(name="Half Boots", description="Wear it with your best jeans",
                     category=cat1)

session.add(ListItem3)
session.commit()


cat2 = Category(name="Shirts")

session.add(cat2)
session.commit()

listitem4 = ListItem(name="Dress Shirt", description="Great for work days.",
                     category=cat2)

session.add(listitem4)
session.commit()

listite5 = ListItem(name="Tshirt", description="For the summer days.",
                    category=cat2)

session.add(listite5)
session.commit()

cat3 = Category(name="Pants")

session.add(cat3)
session.commit()


listitem6 = ListItem(name="Dress pants", description="Match it with our Dress shirts.",
                     category=cat3)

session.add(listitem6)
session.commit()

listitem7 = ListItem(name="Jeans", description="for everyday uses.",
                     category=cat3)

session.add(listitem7)
session.commit()

listitem8 = ListItem(name="Baggy pants", description="For fun adventures.",
                     category=cat3)

session.add(listitem8)
session.commit()

listitem9 = ListItem(name="Shorts", description="Summer Fashion.",
                     category=cat3)

session.add(listitem9)
session.commit()

session.close()

print 'Done'
