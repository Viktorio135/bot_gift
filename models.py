from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import inspect


import config


Base = declarative_base()
engine = create_engine(f"mysql+mysqlconnector://{config.USER}:{config.PASSWORD}@{config.HOST}/{config.DATABASE}")

class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)

class Rates(Base):
    __tablename__ = 'rates'

    id = Column(Integer, primary_key=True)
    name_category = Column(String(100), ForeignKey('category.name'))
    rate = Column(String(50))

def create_category(name_category):
    with Session(autoflush=False, bind=engine) as session:
        category = Category(name=name_category)
        session.add(category)
        session.commit()

def remove_category(name_category):
    with Session(autoflush=False, bind=engine) as session:
        category = session.query(Category).filter(Category.name == name_category).first()
        session.delete(category)
        session.commit()

def read_category():
    with Session(autoflush=False, bind=engine) as session:
        categories_list = []
        categories = session.query(Category).all()
        for category in categories:
            categories_list.append(category.name)
        return categories_list

def create_rate(rate, name_category):
    with Session(autoflush=False, bind=engine) as session:
        rate_obj = Rates(name_category=name_category, rate=rate)
        session.add(rate_obj)
        session.commit()

def read_rate(category_name):
    with Session(autoflush=False, bind=engine) as session:
        goods = session.query(Rates).filter(Rates.name_category == category_name).all()
        return goods

def remove_rate(rate, name_category):
    with Session(autoflush=False, bind=engine) as session:
        good = session.query(Rates).filter(Rates.name_category == name_category).filter(Rates.rate == rate).first()
        session.delete(good)
        session.commit()

def start_database():
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    if 'category' not in existing_tables:
        Base.metadata.create_all(bind=engine)

    # Base.metadata.create_all(bind=engine, checkfirst=False)

