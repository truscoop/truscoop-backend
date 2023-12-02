# Specification for Backend of TruScoop

Contributors: Daniel Chuang (dc863), Satya Datla (ssd76), Peter Bidoshi (pjb294)

## Tables

Articles:

- id
- url
- name
- favicon
- top_img
- date
- summary
- aiRating
- userRating

Ratings:

- id
- articleID (foreign key to Articles)
- userID (stores iPhone's unique ID)
- rating

Comments (future idea, model implemented but other features not implemented):

- id
- articleID (foreign key to article)
- userID (stores iPhone's unique ID)

## Requests

GET /
  - Description: Base page for testing deployment
  - Success Return: "Base request succeeded", 200

GET /api/articles/
  - Description: Get all articles
  - Success Return: [Articles], 200
  - Failure Return: "Request failed serverside, invalid Article stored in database", 500

GET /api/articles/<int:article_id>/
  - Description: Get specific article
  - Success Return: Article, 200
  - Failure Return: "Article not found", 404

POST /api/articles/
  - Description: Submits an article to our AI script (!) for classification, and then adds that article to our database
  - Parameters: url
  - Success Return: Article, 201
  - Failure Return 1: "No url provided", 400
  - Failure Return 2: "Article already exists at id {article.id}", 500
  - Failure Return 3: "Article not found", 404

GET /api/articles/rating/<int:article_id>/
  - Description: Getting both the user rating based on the userID and articleID, as well as the aggregated mean rating of all ratings based on the articleID
  - Success Return: {
    "userRating" : Float in [-1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0] where -1.0 indicates no rating (we make sure this isn't aggregated),
    "rating" : Average of the ratings, Float in [0.0 to 5.0]
  }, 200
  - Failure Return: "No rating found", 404

POST /api/articles/rating/<int:article_id>/
  - Description: Adding a new rating given an articleID and userID
  - Parameters: userID, rating
  - Success Return: Article, 201
  - Failure Return 1: "No userID or rating provided", 400
  - Failure Return 2: "Article not found", 404

DELETE /api/articles/rating/<int:article_id>/
  - Description: Removing a rating given an articleID and userID
  - Parameters: userID
  - Success Return: Article, 204
  - Failure Return 1: "Article not found", 404
  - Failure Return 2: "No rating found to delete", 404