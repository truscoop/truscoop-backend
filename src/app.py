from db import db
from flask import Flask, request
from db import Articles, Users, Ratings
import json
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa
from pandas import pandas
import numpy as np


app = Flask(__name__)
db_filename = "truscoop.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)


def load_articles():
        print("Loading in the Articles into the database")
        data=pandas.read_csv("data/articles.tsv", sep='\t')
        data.insert(0, 'id', range(0, len(data)))
        data["classification"] = np.nan
        data = data.rename(columns={"q3" : "genre", "primary.topic": "primary_topic", "secondary.topic" : "secondary_topic", "democrat.vote" : "democrat_vote", "republican.vote" : "republican_vote"})
        print(data)
        data.to_sql(name='Articles', con=db.engine, index=False, if_exists = 'fail')

with app.app_context():
    # Check if the engine has the table already. If not, then load in the CSV
    insp = sa.inspect(db.engine)
    if not insp.has_table("Articles"):
        load_articles()
    db.create_all()

# generalized response formats
def success_response(data, code=200):
    return json.dumps(data), code


def failure_response(message, code=404):
    return json.dumps({"error": message}), code


# -- ROUTES ------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
