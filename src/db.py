from numpy import *
from time import time
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

def Load_Data(file_name):
    data = genfromtxt(file_name, delimiter=",", usemask=True)
    return data.tolist()

print(Load_Data("data/articles.csv"))

# Base = declarative_base()

# class Price_History(Base):
#     #Tell SQLAlchemy what the table name is and if there's any table-specific arguments it should know about
#     __tablename__ = 'Price_History'
#     __table_args__ = {'sqlite_autoincrement': True}
#     #tell SQLAlchemy the name of column and its attributes:
#     id = Column(Integer, primary_key=True, nullable=False) 
#     date = Column(Date)
#     opn = Column(Float)
#     hi = Column(Float)
#     lo = Column(Float)
#     close = Column(Float)
#     vol = Column(Float)

# if __name__ == "__main__":
#     t = time()

#     #Create the database
#     engine = create_engine('sqlite:///csv_test.db')
#     Base.metadata.create_all(engine)

#     #Create the session
#     session = sessionmaker()
#     session.configure(bind=engine)
#     s = session()

#     try:
#         file_name = "t.csv" #sample CSV file used:  http://www.google.com/finance/historical?q=NYSE%3AT&ei=W4ikVam8LYWjmAGjhoHACw&output=csv
#         data = Load_Data(file_name) 

#         for i in data:
#             record = Price_History(**{
#                 'date' : datetime.strptime(i[0], '%d-%b-%y').date(),
#                 'opn' : i[1],
#                 'hi' : i[2],
#                 'lo' : i[3],
#                 'close' : i[4],
#                 'vol' : i[5]
#             })
#             s.add(record) #Add all the records

#         s.commit() #Attempt to commit all the records
#     except:
#         s.rollback() #Rollback the changes on error
#     finally:
#         s.close() #Close the connection
#     print ("Time elapsed: " + str(time() - t) + " s.")








# # from flask_sqlalchemy import SQLAlchemy

# # db = SQLAlchemy()

# # # Association table for courses and users
# # class Association(db.Model):
# #     __tablename__ = "association"
# #     course_id = db.Column(db.ForeignKey("course.id"), primary_key=True)
# #     users_id = db.Column(db.ForeignKey("user.id"), primary_key=True)
# #     type = db.Column(db.String())
# #     child = db.relationship("User")
# #     parent = db.relationship("Course")


# # # your classes here
# # class Course(db.Model):
# #     """
# #     SQLAlchemy Class for Courses, following this format when retrieved

# #     "courses": [
# #     {
# #         "id": 1,
# #         "code": "CS 1998",
# #         "name": "Intro to Backend Development",
# #         "assignments": [ <SERIALIZED ASSIGNMENT WITHOUT COURSE FIELD>, ... ],
# #         "instructors": [ <SERIALIZED USER WITHOUT COURSES FIELD>, ... ],
# #         "students": [ <SERIALIZED USER WITHOUT COURSES FIELD>, ... ]
# #     },
# #     """

# #     __tablename__ = "course"
# #     id = db.Column(db.Integer, primary_key=True)
# #     code = db.Column(db.String, nullable=False)
# #     name = db.Column(db.String, nullable=False)

# #     # Courses to assignments is a many to one relationship
# #     assignments = db.relationship("Assignment", cascade="delete")

# #     # Courses to users is a many to many relationship, need an association table
# #     users = db.relationship("Association", back_populates="parent")

# #     def __init__(self, **kwargs):
# #         self.code = kwargs.get("code", "code not provided")
# #         self.name = kwargs.get("name", "name not provided")

# #     def serialize(self):
# #         """
# #         Returns a serialization of a course, but without any relationship data
# #         """
# #         return {
# #             "id": self.id,
# #             "code": self.code,
# #             "name": self.name,
# #         }

# #     def serialize_all(self):
# #         """
# #         Returns a serialization of a course
# #         """
# #         serialization = self.serialize()
# #         serialization["assignments"] = [a.serialize() for a in self.assignments]

# #         instructors = []
# #         students = []
# #         for assoc in self.users:
# #             if assoc.type == "instructor":
# #                 instructors.append(assoc.child)
# #             else:
# #                 students.append(assoc.child)

# #         serialization["instructors"] = [u.serialize() for u in instructors]
# #         serialization["students"] = [u.serialize() for u in students]

# #         return serialization


# # class User(db.Model):
# #     """
# #     SQLAlchemy Class for Users, following this format when retrieved

# #     {
# #         "id": <ID>,
# #         "name": <USER INPUT FOR NAME>,
# #         "netid": <USER INPUT FOR NETID>,
# #         "courses": [ <SERIALIZED COURSE WITHOUT ASSIGNMENTS, STUDENT, OR INSTRUCTOR FIELDS>, ... ]
# #     }
# #     """

# #     __tablename__ = "user"
# #     id = db.Column(db.Integer, primary_key=True)
# #     name = db.Column(db.String, nullable=False)
# #     netid = db.Column(db.String, nullable=False)

# #     # Courses to users is a many to many relationship, need an association table
# #     courses = db.relationship("Association", back_populates="child")

# #     def __init__(self, **kwargs):
# #         self.name = kwargs.get("name", "no name provided")
# #         self.netid = kwargs.get("netid", "no netid provided")

# #     def serialize(self):
# #         """
# #         Returns a serialization of a course, but without any relationship data
# #         """
# #         return {"id": self.id, "name": self.name, "netid": self.netid}

# #     def serialize_all(self):
# #         """
# #         Returns a serialization of a course
# #         """
# #         serialization = self.serialize()
# #         user_courses = []
# #         for assoc in self.courses:
# #             if assoc.users_id == self.id:
# #                 user_courses.append(assoc.parent)

# #         serialization["courses"] = [c.serialize() for c in user_courses]
# #         return serialization


# # class Assignment(db.Model):
# #     """
# #     SQLAlchemy Class for Assignments, following this format when retrieved

# #     {
# #         "id": <ASSIGNMENT ID>,
# #         "title": "PA4",
# #         "due_date": 1553354209,  // in Unix time
# #         "course": {
# #             "id": {id},
# #             "code": <STORED CODE FOR COURSE WITH ID {id}>,
# #             "name": <STORED NAME FOR COURSE WITH ID {id}>
# #         }
# #     }
# #     """

# #     __tablename__ = "assignment"
# #     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
# #     title = db.Column(db.String, nullable=False)
# #     due_date = db.Column(db.Integer, nullable=False)
# #     course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)

# #     def __init__(self, **kwargs):
# #         self.title = kwargs.get("title", "No title provided")
# #         self.due_date = kwargs.get("due_date", "No due date provided")
# #         self.course_id = kwargs.get("course_id", "No course_id provided")

# #     def serialize(self):
# #         """
# #         Returns a serialization of a course, but without any relationship data
# #         """
# #         return {"id": self.id, "title": self.title, "due_date": self.due_date}

# #     def serialize_all(self):
# #         """
# #         Returns a serialization of a course
# #         """
# #         serialization = self.serialize()
# #         return serialization
