# InnowiseTask
REST API for Tinder-like application with DRF. Testing with pytest. Deploying to docker with docker-compose.

# Run the app

Application is deployed to docker, `Dockerfile` for the DRF app and `docker-compose.yaml` files are configured using PostgreSQL database to run the app using docker

Create `.env` file in the root directory to configure the database connection or specify the connection data in `settings.py`

#### `.env` File example

    SQL_ENGINE = django.db.backends.postgresql_psycopg2
    SQL_NAME = your_database
    SQL_USER = your_user
    SQL_PASSWORD = your_password
    SQL_HOST = db
    SQL_PORT = 5432
    
#### Run docker containers
###### Build all the containers
    docker-compose build
###### Run all the containers in background
    docker-compose up -d
###### Make migrations for the database
    docker-compose exec web python manage.py migrate
###### Create superuser for the app
    docker-compose exec web python manage.py createsuperuser

# Test the app
PyTest library is used to test the application

#### Run tests
###### Run the containers in background
    docker-compose up -d
###### Run all the tests
    docker-compose exec web pytest
###### Run one app tests
    docker-compose exec web pytest {app|activities|chat}

# Api Overview

## Register new user

Register new user with the given credentials, new profile and location objects will be created
### Request
`POST register/`

    {
      "username": "sample",
      "first_name": "John",
      "last_name": "Doe",
      "email": "sample@gmail.com",
      "password": "sample"
    }

### Response

    {
        "id": 1,
        "username": "sample",
        "first_name": "John",
        "last_name": "Doe",
        "email": "sample@gmail.com",
        "password": "pbkdf2_sha256$216000$ymiaXpROsWT7$keztaUWARcVoRqvTo/fKQlNZ+iOOxw0DzyBw6StjMjQ="
    }

## Get token to authenticate user

### Request
`POST api/token/`

    {
      "username": "sample",
      "password": "sample"
    }
    
### Response
    {
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTYxNTg4NjIxMywianRpIjoiYmQzNDY2ODBjMzQ4NGM4MDlkYzU5MTEyNGMyYTcyOGUiLCJ1c2VyX2lkIjoxfQ.unKxo3IUbmVzFDvkvcPKoSrqpgv1JAvdRAiLExDF0d8",
      "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjE0NTAzODEzLCJqdGkiOiI5MTVkYzY4MWExMjM0Y2E1YjMwYzE4NmNkZjc2NTVjMCIsInVzZXJfaWQiOjF9.Sxv8jU-Q685FMuAiPJisa9Nxnp3-B4MmWSmLary9O_M"
    }
    
#### Add Bearer token to request headers to be authenticated

    Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjE0NTAzODEzLCJqdGkiOiI5MTVkYzY4MWExMjM0Y2E1YjMwYzE4NmNkZjc2NTVjMCIsInVzZXJfaWQiOjF9.Sxv8jU-Q685FMuAiPJisa9Nxnp3-B4MmWSmLary9O_M

## Get info about current authenticated user

Profile is automatically created when user is registered, but profile info is empty
### Request

`GET api/app/profile/?me=true`

### Response

    {
        "id": 1,
        "fname": "John",
        "lname": "Doe",
        "info": "",
        "vip": false,
        "user": 1,
        "images": [],
        "location": [
            1
        ],
        "gender": ""
    }
    
## Update user info 
User can update all the fields or some of them
### Request 
`PUT api/app/profile/1/`

    {
        "info": "Hello world!",
        "gender": "M",
        "vip": "true"
    }
    
### Response

    {
        "id": 1,
        "fname": "John",
        "lname": "Doe",
        "info": "Hello world!",
        "vip": true,
        "user": 1,
        "images": [],
        "location": [
            1
        ],
        "gender": "M"
    }
    
## Get location of current authenticated user

Location is automatically created when user is registered, but location info is empty
### Request
`GET api/app/location/`

### Response
    {
        "profile": {
            "id": 1,
            "fname": "John",
            "lname": "Doe",
            "info": "Hello world!",
            "vip": true,
            "gender": "M",
            "user": 1
        },
        "location": "",
        "date": "2021-02-14T09:28:48.999390Z",
        "latitude": null,
        "longitude": null
    }
    
## Update user location 

User enters his location and coordinates are automatically calculated on the server

User can update it's location only once every two hours
### Request
`PUT api/app/location/1/`

    {
        "location": "Минск, улица Немига"
    }

### Response

    {
        "profile": {
            "id": 1,
            "fname": "John",
            "lname": "Doe",
            "info": "Hello world!",
            "vip": true,
            "gender": "M",
            "user": 1
        },
        "location": "Минск, улица Немига",
        "date": "2021-02-14T10:33:03.753587Z",
        "latitude": 53.8997424,
        "longitude": 27.545557
    }
    
If user tries to update location when two hours after last update haven't passed yet
    
    {
        "detail": "location update available only once every two hours"
    }
    
## Get current authenticated user images

### Request
`GET api/app/images/`

### Response
    [
      {
          "image": "http://localhost:8000/media/upload/profile/1af2ea74-a746-4aee-aa72-a1819e05b160.jpg",
          "profile": 1,
          "date": "2021-02-14T10:45:38.043549Z"
      }
    ]
    
## Get one image

### Request
`GET api/app/images/1/`

### Response
    {
        "image": "http://localhost:8000/media/upload/profile/1af2ea74-a746-4aee-aa72-a1819e05b160.jpg",
        "profile": 1,
        "date": "2021-02-14T10:45:38.043549Z"
    }

## Upload profile image

User can upload images to his profile and they are stored on the server
### Request

`POST api/app/images/`

    {
        "image": {some image}
    }

### Response

    {
        "image": "http://localhost:8000/media/upload/profile/1af2ea74-a746-4aee-aa72-a1819e05b160.jpg",
        "profile": 1,
        "date": "2021-02-14T10:45:38.043549Z"
    }
    
## Look for users to like or dislike them

User can see people of opposite gender around him, search radius depends on user's subscription (default or vip)

Random profile will be chosen from the list and shown to user
### Request

`GET api/app/profile/`

### Response

    {
        "id": 2,
        "fname": "Jane",
        "lname": "Doe",
        "info": "Hello world!",
        "vip": false,
        "user": 2,
        "images": [
            2
        ],
        "location": [
            2
        ],
        "gender": "F"
    }

## Swipe the profile user received

User can like or dislike randomly received profile
### Request

`POST api/activities/swipe/`

    {
        "swiped": "2",
        "liked": "true"
    }

If current user liked the profile he received and the received user liked current user they are matched, and "match" field equals "true" otherwise "false"
If users are matched new chat will be created, users can start chat with each other
### Response

      {
        "match": true,
        "swipe": {
            "date": "2021-02-14T11:08:37.292099Z",
            "liked": true,
            "profile": {
                "id": 1,
                "fname": "John",
                "lname": "Doe",
                "info": "Hello world!",
                "vip": true,
                "gender": "M",
                "user": 1
            },
            "swiped": {
                "id": 2,
                "fname": "Jane",
                "lname": "Doe",
                "info": "Hello world!",
                "vip": false,
                "gender": "F",
                "user": 2
            }
        }
    }
    
## Get matches for current authenticated user

Get all matches for current authenticated user, all profiles he matched with will be shown
### Request
`GET api/activities/swipe/`

### Response

    [
        {
            "date": "2021-02-14T11:03:22.045487Z",
            "liked": true,
            "profile": {
                "id": 2,
                "fname": "Jane",
                "lname": "Doe",
                "info": "Hello world!",
                "vip": false,
                "gender": "F",
                "user": 3
            },
            "swiped": {
                "id": 1,
                "fname": "John",
                "lname": "Doe",
                "info": "Hello world!",
                "vip": true,
                "gender": "M",
                "user": 2
            }
        }
    ]
    
If user doesn't have any matches

    {
      "detail": "no matches yet"
    }
    
## Get info about matched profile

User can get info about matched profile, if users are not matched access to profile info is denied

### Request
`GET api/app/profile/2/`

### Response

    {
        "id": 2,
        "fname": "Jane",
        "lname": "Doe",
        "info": "Hello world!",
        "vip": false,
        "user": 2,
        "images": [],
        "location": [
            2
        ],
        "gender": "F"
    }
    
If user tries to get info about unmatched profile

    {
        "detail":"user can't get info about unmatched profile'"
    }
    
## Get chats of current user

User is involved in chats with the matched users and can see all these chats
### Request

`GET api/chat/chat`

### Response
    [
      {
          "id": 1,
          "user1": {
              "id": 1,
              "fname": "John",
              "lname": "Doe",
              "info": "Hello world!",
              "vip": true,
              "gender": "M",
              "user": 1
          },
          "user2": {
              "id": 2,
              "fname": "Jane",
              "lname": "Doe",
              "info": "Hello world!",
              "vip": false,
              "gender": "F",
              "user": 2
          }
      }
    ]
    
## Write new message to a chat with some user

User can chat only with matched users
### Request
`POST api/chat/chat/`

    {
        "chat": "1",
        "message": "Hello!"
    }

### Response
    {
        "id": 1,
        "message": "\"Hello!\"",
        "sender": {
            "id": 1,
            "fname": "John",
            "lname": "Doe",
            "info": "Hello world!",
            "vip": true,
            "gender": "M",
            "user": 2
        },
        "chat": {
            "id": 1,
            "date": "2021-02-14T11:08:37.313652Z",
            "user1": 1,
            "user2": 2
        }
    }
    
If user tries to send message to chat he doesn't take part in
    
    {
        "detail":"user can't chat with unmatched users"
    }
    
## Get messages from the chat that user is involved in

### Request
`GET api/chat/chat/1/`

### Response

    [
        {
            "id": 2,
            "message": "Hi",
            "sender": {
                "id": 2,
                "fname": "Jane",
                "lname": "Doe",
                "info": "Hello world!",
                "vip": false,
                "gender": "F",
                "user": 3
            },
            "chat": {
                "id": 1,
                "date": "2021-02-14T11:08:37.313652Z",
                "user1": 1,
                "user2": 2
            }
        },
        {
            "id": 1,
            "message": "\"Hello!\"",
            "sender": {
                "id": 1,
                "fname": "John",
                "lname": "Doe",
                "info": "Hello world!",
                "vip": true,
                "gender": "M",
                "user": 2
            },
            "chat": {
                "id": 1,
                "date": "2021-02-14T11:08:37.313652Z",
                "user1": 1,
                "user2": 2
            }
        }
    ]
    
If user tries to get messages from chat he doesn't take part in

    {
        "detail":"user can't get messages from a chat he is not in"
    }
