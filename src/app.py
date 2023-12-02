from db import db
from flask import Flask, request
from db import Articles, Ratings
import json
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa
import pandas
import numpy as np
import os
from datetime import datetime

from new_article import handle_incoming_url

app = Flask(__name__)
db_filename = "truscoop.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)

rating_last_id = 1


def load_articles():
    
        here = os.path.dirname(os.path.abspath(__file__))
        parent = os.path.dirname(os.path.normpath(here))
        path = os.path.join(parent, "data/final_for_backend.csv")
        
        # Creates a dataframe of the articles
        print("Loading in the Articles into the database")
        data = pandas.read_csv(path)

        # Loop through the dataframe
        date_format = '%Y-%m-%d'
        data2 = data.replace(np.nan, '', regex=True)

        for index, row in data2.iterrows():
            article = Articles(
                    url = row["url"],
                    name = row["title"],
                    favicon = row["favicon"],
                    topImg = row["topImg"],
                    date = datetime.strptime(row["date"], date_format),
                    summary = row["summary"],
                    aiRating = "neutral" if row["aiRating"] == 1 else "conservative" if row["aiRating"] == 2 else "liberal",
                    userRating = -1.0
            )
            db.session.add(article)
        db.session.commit()


        # print(data)
        # # If we need to set a primary, then do this: https://stackoverflow.com/questions/39407254/how-to-set-the-primary-key-when-writing-a-pandas-dataframe-to-a-sqlite-database
        # data.to_sql(name='Articles', con=db.engine, index=False, if_exists = 'fail')
        
        # Make the article's id a primary key

with app.app_context():
    # Check if the engine has the table already. If not, then load in the CSV
    insp = sa.inspect(db.engine)
    if not insp.has_table("Articles"):
        db.drop_all()
        db.create_all()
        load_articles()

# generalized response formats
def success_response(data, code=200):
    return json.dumps(data), code


def failure_response(message, code=404):
    return json.dumps({"error": message}), code


# -- ROUTES ------------------------------------------------------
@app.route("/", methods=["GET"])
def base():
    """
    Endpoint base
    """
    return "base request succeeded", 200

@app.route("/api/articles/", methods=["GET"])
def get_all_articles():
    """
    Endpoint for getting all articles
    """
    articles = []
    for article in Articles.query.all():
        if article is None:
            return failure_response("Request failed serverside, invalid Article stored in database", 500)
        article.favicon = "https://www.google.com/s2/favicons?domain=" + article.url + "&sz=128" 
        print(article.ai_rating)
        articles.append(article.serialize())
    return articles, 200

@app.route("/api/articles/<int:article_id>/", methods=["GET"])
def get_article(article_id):
    """
    Endpoint for getting an article based on its id
    """
    article = Articles.query.filter_by(id=article_id).first()
    if article is None:
        return failure_response("Article not found")
    return article.serialize(), 200

@app.route("/api/articles/", methods=["POST"])
def create_article():
    """
    Endpoint for creating a new article
    """

    params = request.args
    url = params.get("url")

    if url is None:
        return failure_response("No url provided", 400)

    # is the article already in the database? if so, return the id of the article
    article = Articles.query.filter_by(url=url).first()
    if article is not None:
        print("ALREADY THERE")
        return failure_response(f"article already exists at id {article.id}", 500)

    article = handle_incoming_url(url)

    if article is None:
        return failure_response("Article not found")

    # add the article to the database
    new_article = Articles(
        url = article['url'],
        name = article['title'],
        favicon = article['favicon'],
        topImg = article['topImg'],
        date = article['date'],
        summary = article['summary'],
        aiRating = "neutral" if article["aiRating"] == 1 else "conservative" if article["aiRating"] == 2 else "liberal",
        userRating = -1
    )

    db.session.add(new_article)
    db.session.commit()

    return new_article.serialize(), 201

@app.route("/api/articles/rating/<int:article_id>/", methods=["GET"])
def get_rating(article_id):
    """
    Endpoint for getting both the user rating based on the userID 
    and the aggregated rating of all ratings based on the article_id  
    """

    params = request.args
    userID = params.get("user_id")

    if userID is not None:
        # Query for the rating first
        rating = Ratings.query.filter_by(article_id=article_id, user_id=userID).first()
        if rating is None:
            return failure_response("No rating found")
        
        # Get the aggregated rating
        ratings = [rating.rating for rating in Ratings.query.filter_by(article_id=article_id)]

        return success_response({
            "userRating": rating.rating,
            "rating" : sum(ratings) / max(1, len(ratings))
        })
    
    # If there is no userID, then just return the aggregated rating
    ratings = [rating.rating for rating in Ratings.query.filter_by(article_id=article_id)]
    if len(ratings) == 0:
        return success_response({
            "rating": -1,
            "userRating": -1
        })
    return success_response({
            "rating": sum(ratings) / len(ratings),
            "userRating": -1
        })

@app.route("/api/articles/rating/<int:article_id>/", methods=["POST"])
def post_rating(article_id):
    """
    Endpoint for posting a rating on the article based on the article_id

    userID: the unique phone identifier of the user to post rating on
    """

    params = request.args
    userID = params.get("user_id")
    rating = params.get("rating")

    # if userID or rating is not provided, return error
    if userID is None or rating is None:
        return failure_response("No userID or rating provided", 400)


    article = Articles.query.filter_by(id=article_id).first()
    if article is None:
        return failure_response("Article not found!")
    
    # If they've already rated before, then delete the previous rating
    old_rating = Ratings.query.filter_by(article_id=article_id, user_id=userID).first()
    print("old_rating", old_rating)
    if old_rating is not None:
        db.session.delete(old_rating)

    rating = Ratings(
        article_id = article_id,
        user_id = userID,
        rating = rating
    )
    db.session.add(rating)
    db.session.commit()

    # update the userRating in the Articles table to be the average of all the ratings
    ratings = [rating.rating for rating in Ratings.query.filter_by(article_id=article_id)]

    article = Articles.query.filter_by(id=article_id).first()
    
    if len(ratings) == 0:
        article.user_rating = -1
    else:
        article.user_rating = sum(ratings) / len(ratings)
    db.session.commit()

    article = Articles.query.filter_by(id=article_id).first()
    if article is None:
        return failure_response("Article not found")
    return article.serialize(), 201

@app.route("/api/articles/rating/<int:article_id>/", methods=["DELETE"])
def delete_rating(article_id):
    """
    Endpoint for deleting a rating from a specific article from the article_id

    userID: the unique phone identifier id to delete the rating from
    """
    params = request.args
    userID = params.get("user_id")

    article = Articles.query.filter_by(id=article_id).first()
    if article is None:
        return failure_response("Article not found")

    # Query for the rating first
    rating = Ratings.query.filter_by(article_id=article_id, user_id=userID).first()
    if rating is None:
        return failure_response("No rating found to delete")

    db.session.delete(rating)
    db.session.commit()

    # update the userRating in the Articles table to be the average of all the ratings
    ratings = [rating.rating for rating in Ratings.query.filter_by(article_id=article_id)]
    if len(ratings) == 0:
        article.user_rating = -1
    else:
        article.user_rating = sum(ratings) / len(ratings)

    return article.serialize(), 200

# -- MAIN ------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
