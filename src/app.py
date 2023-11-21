from db import db
from flask import Flask, request
from db import Course, User, Assignment, Association
import json

app = Flask(__name__)
db_filename = "cms.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()

# generalized response formats
def success_response(data, code=200):
    return json.dumps(data), code


def failure_response(message, code=404):
    return json.dumps({"error": message}), code


# -- ROUTES ------------------------------------------------------
@app.route("/api/courses/", methods=["GET"])
def get_courses():
    """
    Request to get all courses

    Returns 200 on success
    """
    courses = [course.serialize_all() for course in Course.query.all()]
    return success_response({"courses": courses})


@app.route("/api/courses/", methods=["POST"])
def create_course():
    """
    Request to create a course, taking in a json

    Returns 201 on success and 400 on failure
    """
    body = json.loads(request.data)
    code = body.get("code")
    name = body.get("name")
    if code is None or name is None:
        return failure_response("Invalid inputs!", 400)
    new_course = Course(
        code=code,
        name=name,
    )
    db.session.add(new_course)
    db.session.commit()
    return success_response(new_course.serialize_all(), 201)


@app.route("/api/courses/<int:id>/", methods=["GET"])
def get_course(id):
    """
    Request to get a specific course, taking in an id from the url

    Returns 200 on success
    """
    course = Course.query.filter_by(id=id).first()
    if course is None:
        return failure_response("Course not found!")
    return success_response(course.serialize_all())


@app.route("/api/courses/<int:id>/", methods=["DELETE"])
def delete_course(id):
    """
    Request to delete a specific course, taking in an id from the url

    Returns 200 on success
    """
    course = Course.query.filter_by(id=id).first()
    if course is None:
        return failure_response("Course not found!")
    db.session.delete(course)
    db.session.commit()
    return success_response(course.serialize_all())


@app.route("/api/users/", methods=["POST"])
def create_user():
    """
    Request to create a new user, taking in an json as input

    Returns 201 on success
    """
    body = json.loads(request.data)
    name = body.get("name")
    netid = body.get("netid")
    if name is None or netid is None:
        return failure_response("Invalid inputs!", 400)
    new_user = User(
        name=name,
        netid=netid,
    )
    db.session.add(new_user)
    db.session.commit()
    return success_response(new_user.serialize_all(), 201)


@app.route("/api/users/<int:id>/", methods=["GET"])
def get_user(id):
    """
    Request to get a specific user, taking in id from url

    Returns 200 on success
    """
    user = User.query.filter_by(id=id).first()
    if user is None:
        return failure_response("User not found!")
    return success_response(user.serialize_all())


@app.route("/api/courses/<int:id>/add/", methods=["POST"])
def add_user_to_course(id):
    """
    Request to add a user to a course, taking in a json

    Returns 200 on success
    """
    course = Course.query.filter_by(id=id).first()
    if course is None:
        return failure_response("Course not found!")
    body = json.loads(request.data)
    user_id = body.get("user_id")
    type = body.get("type")
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found!")

    # Append the user to the course
    a = Association(type=type)
    a.child = user
    course.users.append(a)
    db.session.commit()

    return get_course(id)


@app.route("/api/courses/<int:id>/assignment/", methods=["POST"])
def create_assignment(id):
    """
    Request to create an assignment for a course

    Returns 201 on success
    """

    # Check if the course exists
    course = Course.query.filter_by(id=id).first()
    if course is None:
        return failure_response("Course not found!")

    body = json.loads(request.data)
    title = body.get("title")
    due_date = body.get("due_date")
    if title is None or due_date is None:
        return failure_response("Invalid input!", 400)

    new_assignment = Assignment(
        title=title,
        due_date=due_date,
        course_id=id,
    )

    db.session.add(new_assignment)
    db.session.commit()

    # Returning the assignment
    output = new_assignment.serialize_all()
    output["course"] = course.serialize()

    return success_response(output, 201)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
