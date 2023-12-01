from numpy import *
from time import time
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from pprint import pprint
from pandas import pandas
##from eralchemy import render_er

db = SQLAlchemy()

class Articles(db.Model):
    """
    SQLAlchemy Class for Articles, following this format when retrieved

    {
        - id
        - url
        - title
        - favicon
        - top_img
        - date
        - summary
        - ai_rating
        - user_rating
        - (future idea) have users_id be recorded when they submit an article
    }
    """

    __tablename__ = "Articles"
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    favicon = db.Column(db.String, nullable=False)
    top_img = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    summary = db.Column(db.String, nullable=False)
    ai_rating = db.Column(db.String, nullable=False)
    user_rating = db.Column(db.Integer, nullable=False)

    def __init__(self, **kwargs):
        """
        Initialize an Article Object
        """
        self.url = kwargs.get("url", "")
        self.name = kwargs.get("name", "")
        self.favicon = kwargs.get("favicon", "")
        self.top_img = kwargs.get("top_img", "")
        self.date = kwargs.get("date", "")
        self.summary = kwargs.get("summary", "")
        self.ai_rating = kwargs.get("ai_rating", "")
        self.user_rating = kwargs.get("user_rating", "")

    def serialize(self):
        """
        Serialize an Article Object
        """
        dateformat = '%Y-%m-%d %H:%M:%S'

        return {
            "id": str(self.id),
            "url": self.url,
            "name": self.name,
            "favicon": self.favicon,
            "topImg": self.top_img,
            "date": self.date.isoformat() + "Z",
            "summary": self.summary,
            "aiRating": self.ai_rating,
            "userRating": float(self.user_rating)
        }

# class Users(db.Model):
#     """
#     SQLAlchemy Class for Users, following this format when retrieved

#     The id will be based off of the iPhone's unique identifier

#     {
#     - id
#     }
#     """

#     __tablename__ = "Users"
#     id = db.Column(db.Integer, primary_key=True)

class Ratings(db.Model):
    """
    SQLAlchemy Class for Ratings, following this format when retrieved

    {
    - id
    - article_id (foreign key to Articles)
    - user_id (foreign key to user)
    - rating
    }
    """

    __tablename__ = "Ratings"
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.ForeignKey("Articles.id"))
    user_id = db.Column(db.String, nullable = False)
    rating = db.Column(db.Integer, nullable = False) # should be a float [0-5]

    def __init__(self, **kwargs):
        """
        Initialize an Article Object
        """
        self.article_id = kwargs.get("article_id")
        self.user_id = kwargs.get("user_id")
        self.rating = kwargs.get("rating")

class Comments(db.Model):
    """
    SQLAlchemy Class for Comments, following this format when retrieved

    {
    - id
    - article_id (foreign key to Articles)
    - user_id (foreign key to user)
    - comment
    }
    """

    __tablename__ = "Comments"
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.ForeignKey("Articles.id"))
    # user_id = db.Column(db.ForeignKey("Users.id"))
    user_id = db.Column(db.String, nullable = False)
    comment = db.Column(db.String, nullable = False)