# =================================================================
# Python Module
# - File: db_models.py
# - Flask/SQLAlchemy Class/DB Table definitions
# - Supports 'item_catalog' web-server application
# =================================================================

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base()


class User(Base):
    """Class/DB definition for local User"""
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

    @property
    def serialize(self):
        """Return object data in easily serializeable format (JSON)"""
        return {
            'name': self.name,
            'id': self.id,
            'email': self.email,
            'picture': self.picture
        }


class Category(Base):
    """Class/DB definition for Catalog Category

       Note: Class names used in relationship() calls are quoted strings,
             NOT Class Name variables, to allow ref to the Class Names before
             the Class is defined.
    """
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User")
    # --------------------------------------------------------
    # Setup relationship to drive Cascade deletion of related
    # Child records
    # --------------
    item = relationship("Item", cascade="all, delete-orphan")

    @property
    def serialize(self):
        """Return object data in easily serializeable format (JSON)"""
        return {
            'name': self.name,
            'id': self.id,
            'user_id': self.user_id
        }


class Item(Base):
    """Class/DB definition for Catalog Item

       Note: Class names used in relationship() calls are quoted strings,
             NOT Class Name variables, to allow ref to the Class Names before
             the Class is defined.
    """
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    picture = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship("Category")
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User")

    @property
    def serialize(self):
        """Return object data in easily serializeable format (JSON)"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'picture': self.picture,
            'category_id': self.category_id,
            'user_id': self.user_id
        }


engine = create_engine('sqlite:///itemcatalog.db')


Base.metadata.create_all(engine)
