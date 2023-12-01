from db import db
from flask import Flask, request
from db import Articles, Ratings
import json
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa
import pandas
import numpy as np
import os

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
        for index, row in data.iterrows():
            article = Articles(
                    url = row["url"],
                    title = row["title"],
                    favicon = row["favicon"],
                    top_img = row["top_img"],
                    date = row["date"],
                    summary = row["summary"],
                    ai_rating = row["ai_rating"],
                    user_rating = row["user_rating"]
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
    return success_response({"success": "base request succeeded!"})

@app.route("/api/articles/<int:article_id>/", methods=["GET"])
def get_article(article_id):
    """
    Endpoint for getting an article based on its id
    """
    article = Articles.query.filter_by(id=article_id).first()
    if article is None:
        return failure_response("Task not found!")
    return success_response(article.serialize())

@app.route("/api/articles/", methods=["GET"])
def get_all_articles():
    """
    Endpoint for getting all articles
    """
    articles = []
    for article in Articles.query.all():
        if article is None:
            return failure_response("Invalid article!")
        articles.append(article.serialize())
    return success_response({"articles": articles})

@app.route("/api/articles/rating/<int:article_id>/", methods=["GET"])
def get_rating(article_id):
    """
    Endpoint for getting both the user rating based on the user_id 
    and the aggregated rating of all ratings based on the article_id  
    """

    params = request.args
    user_id = params.get("user_id")

    if user_id is not None:
        # Query for the rating first
        rating = Ratings.query.filter_by(article_id=article_id, user_id = user_id).first()
        if rating is None:
            return failure_response("No rating found")
        
        # Get the aggregated rating
        ratings = [rating.rating for rating in Ratings.query.filter_by(article_id=article_id)]

        return success_response({
            "user_rating": rating.rating,
            "rating" : sum(ratings) / max(1, len(ratings))
        })
    
    # If there is no user_id, then just return the aggregated rating
    ratings = [rating.rating for rating in Ratings.query.filter_by(article_id=article_id)]
    if len(ratings) == 0:
        return success_response({"rating": None})
    return success_response({"rating": sum(ratings) / len(ratings)})

@app.route("/api/articles/rating/<int:article_id>/", methods=["POST"])
def post_rating(article_id):
    """
    Endpoint for posting a rating on the article based on the article_id

    user_id: the unique phone identifier of the user to post rating on
    """

    body = None

    try:
        # check if there is a provided body
        body = json.loads(request.data)
    except:
        return failure_response("Please provide a json body")

    user_id = body.get("user_id")
    rating = body.get("rating")

    # if user_id or rating is not provided, return error
    if user_id is None or rating is None:
        return failure_response("No user_id or rating provided")


    article = Articles.query.filter_by(id=article_id).first()
    if article is None:
        return failure_response("Invalid article!")
    
    # If they've already rated before, then delete the previous rating
    old_rating = Ratings.query.filter_by(article_id=article_id, user_id = user_id).first()
    print("old_rating", old_rating)
    if old_rating is not None:
        db.session.delete(old_rating)

    rating = Ratings(
        article_id = article_id,
        user_id = user_id,
        rating = rating
    )

    db.session.add(rating)
    db.session.commit()

    # update the user_rating in the Articles table to be the average of all the ratings
    ratings = [rating.rating for rating in Ratings.query.filter_by(article_id=article_id)]
    if len(ratings) == 0:
        article.user_rating = None
    else:
        article.user_rating = sum(ratings) / len(ratings)
    db.session.commit()

    return success_response({"success": f"Rating on article {article_id} of {rating} by user {user_id} submitted"})

@app.route("/api/articles/rating/<int:article_id>/", methods=["DELETE"])
def delete_rating(article_id):
    """
    Endpoint for deleting a rating from a specific article from the article_id

    user_id: the unique phone identifier id to delete the rating from
    """
    params = request.args
    user_id = params.get("user_id")

    article = Articles.query.filter_by(id=article_id).first()
    if article is None:
        return failure_response("Invalid article!")

    # Query for the rating first
    rating = Ratings.query.filter_by(article_id=article_id, user_id = user_id).first()
    if rating is None:
        return failure_response("No rating found to delete")

    db.session.delete(rating)
    db.session.commit()

    # update the user_rating in the Articles table to be the average of all the ratings
    ratings = [rating.rating for rating in Ratings.query.filter_by(article_id=article_id)]
    if len(ratings) == 0:
        article.user_rating = None
    else:
        article.user_rating = sum(ratings) / len(ratings)

    db.session.commit()
    return success_response({"success": "Rating deleted successfully!"})

@app.route("/api/articles/", methods=["POST"])
def create_article():
    """
    Endpoint for creating a new article
    """

    body = json.loads(request.data)
    url = body.get("url")
    if url is None:
        return failure_response("No url provided")

    # is the article already in the database? if so, return the id of the article
    article = Articles.query.filter_by(url=url).first()
    if article is not None:
        return success_response({"message": "article already exists","id": article.id})

    article = handle_incoming_url(url)
    if article is None:
        return failure_response("Error: article not found")

    # add the article to the database
    new_article = Articles(
        url = article['url'],
        title = article['title'],
        favicon = article['favicon'],
        top_img = article['top_img'],
        date = article['date'],
        summary = article['summary'],
        ai_rating = article['ai_rating'],
        user_rating = article['user_rating']
    )

    db.session.add(new_article)
    db.session.commit()



    return success_response({"success": "Article added successfully!"})

# -- MAIN ------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
