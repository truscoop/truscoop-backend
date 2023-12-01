# Specification for Backend of TruScoop

## Tables

Articles:

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

Users:

- id

Ratings:

- id
- article_id (foreign key to Articles)
- user_id (foreign key to user)
- rating

Comments:

- id
- article_id (foreign key to article)
- user_id (foreign key to user)

## TODO

1. Add in the CSV into the database programmatically

2. Add in the article labels programmatically, with the foreign key links

3. Create get request for article that returns both

## Requests

GET ALL ARTICLES
GET /api/articles/
articles : list of articles

GET SPECIFIC ARTICLE
GET /api/articles/id/
article : { - id,

- url,
- type,
- perceived (?),
- primary_topic,
- secondary_topic,
- democrat_vote,
- republican_vote,
- text,
- classification,  
  }

GET USER RATING AND AGGREGATED RATING OF SPECIFIC ARTICLE AND USER
GET /api/articles/rating/id/
rating???: {

- userRating,
- rating
  }

POST RATING IN SPECIFIC ARTICLE WITH SPECIFIC USER
POST /api/articles/rating/id/
success : {
Rating on article {article_id} of {rating} by user {user_id} submitted
}

DELETE RATING IN SPECIFIC ARTICLE OF SPECIFIC USER
DELETE /api/articles/rating/id/
{"success":
"Rating deleted successfully!"}
