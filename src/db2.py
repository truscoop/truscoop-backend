from numpy import *
from time import time
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from flask_sqlalchemy import create_engine
from flask_sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
engine = create_engine('sqlite:///cdb.db')
Base.metadata.create_all(engine)
with open("data/articles.csv", 'r') as file:
    data_df = pd.read_csv(file)
data_df.to_sql('tbl_name', con=engine, index=True, index_label='id', if_exists='replace')


print(data_df)
