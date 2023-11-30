from db import db
from flask import Flask, request
from db import Articles, Ratings
import json
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa
import pandas
import numpy as np


app = Flask(__name__)
db_filename = "truscoop.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)

rating_last_id = 1


def load_articles():
        
        # Creates a dataframe of the articles
        print("Loading in the Articles into the database")
        data = pandas.read_csv("/data/final_for_backend.csv")

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
    body = json.loads(request.data)
    user_id = body.get("user_id")

    # Query for the rating first
    rating = Ratings.query.filter_by(article_id=article_id, user_id = user_id).first()
    if rating is None:
        return failure_response("No rating found")
    
    # Get the aggregated rating
    ratings = [rating.rating for rating in Ratings.query.filter_by(article_id=article_id)]

    return success_response({
        "user_rating": rating.rating,
        "rating" : sum(ratings) / len(ratings)
        })

@app.route("/api/articles/rating/<int:article_id>/", methods=["POST"])
def post_rating(article_id):
    """
    Endpoint for posting a rating on the article based on the article_id

    user_id: the unique phone identifier of the user to post rating on
    """
    body = json.loads(request.data)
    user_id = body.get("user_id")
    
    # If they've already rated before, then delete the previous rating
    old_rating = Ratings.query.filter_by(article_id=article_id, user_id = user_id).first()
    if old_rating is not None:
        db.session.delete(old_rating)

    rating = Ratings(
        article_id = article_id,
        user_id = user_id,
        rating = body.get("rating")
    )

    db.session.add(rating)
    db.session.commit()
    return success_response({"success": f"Rating on article {article_id} of {rating} by user {user_id} submitted"})

@app.route("/api/articles/rating/<int:article_id>/", methods=["DELETE"])
def delete_rating(article_id):
    """
    Endpoint for deleting a rating from a specific article from the article_id

    user_id: the unique phone identifier id to delete the rating from
    """
    body = json.loads(request.data)
    user_id = body.get("user_id")

    # Query for the rating first
    rating = Ratings.query.filter_by(article_id=article_id, user_id = user_id).first()
    if rating is None:
        return failure_response("No rating found to delete")
    
    db.session.delete(rating)
    db.session.commit()
    return success_response({"success": "Rating deleted successfully!"})


# @app.route("/api/articles/", methods=["POST"])
# def create_article():
#     """
#     Endpoint for creating a new article
#     """


# -- MAIN ------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
