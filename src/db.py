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
    - genre
    - perceived (?)
    - primary_topic
    - secondary_topic
    - democrat_vote
    - republican_vote
    - classification
    - (future idea) have users_id be recorded when they submit an article
    }
    """

    __tablename__ = "Articles"
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    genre = db.Column(db.String, nullable=True)
    perceived = db.Column(db.Integer, nullable=False)
    primary_topic = db.Column(db.String, nullable=False)
    secondary_topic = db.Column(db.String, nullable=True)
    democrat_vote = db.Column(db.String, nullable=False)
    republican_vote = db.Column(db.String, nullable=False)
    classification = db.Column(db.String, nullable=False)

    def __init__(self, **kwargs):
        """
        Initialize an Article Object
        """
        self.url = kwargs.get("url", "")
        self.genre = kwargs.get("genre", "")
        self.perceived = kwargs.get("perceived", "")
        self.primary_topic = kwargs.get("primary_topic", "")
        self.secondary_topic = kwargs.get("secondary_topic", "")
        self.democrat_vote = kwargs.get("democrat_vote", "")
        self.republican_vote = kwargs.get("republican_vote", "")
        self.classification = kwargs.get("id", "")

    def serialize(self):
        """
        Serialize an Article Object
        """
        return {
            "url": self.url,
            "genre": self.genre,
            "perceived": self.perceived,
            "primary_topic": self.primary_topic,
            "secondary_topic": self.secondary_topic,
            "democrat_vote": self.democrat_vote,
            "republican_vote": self.republican_vote,
            "classification": self.classification

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