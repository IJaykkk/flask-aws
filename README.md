# Installation
At project root directory,

```bash
vagrant up
vagrant ssh -- -L 5000:localhost:5000
cd /vagrant/flask-aws
mv .env.bk .env
vim .env # update environment variables
flask run
```

# API
### Caveat
To use token, include "Authorization: Bearer <access_token or refresh_token>" in hearder to access endpoints.

### Token

+ Registration
    + Explaination
    
        To register a user, and then get `access_token` as well as `refresh_token` back.  
`access_token` is used to access api with person information. Default expiration time is 30 mins.  
`refresh_token` is used to get another `access_token`. Default expiration time is 30 days.  

    + Endpoint
    
        post `localhost:5000/registration`

    + Parameters
    ```bash
    {
        "username": "xxx",
        "password": "xxx"
    }
    ```

    + Response
        + Success (200)
        ```bash
        {
            "message": "User <username> was created",
            "access_token": access_token,
            "refresh_token": refresh_token
        }
        ```

        + Error (401)
        ```bash
        {
            "message": "User <username> already exists"
        }
        ```

        + Failure (500)
        ```bash
        {
            "message": "Registration went wrong"
        }
        ```

+ Login
    + Explaination
    
        Use `username` and `password` to login, and then get `access_token` as well as `refresh_token` back.
    
    + Endpoint
    
        post `localhost:5000/login`

    + Parameters
    ```bash
    {
        "username": "xxx",
        "password": "xxx"
    }
    ```

    + Response
        + Success (200)
        ```bash
        {
            "message": "Logged in as <username>",
            "access_token": access_token,
            "refresh_token": refresh_token
        }
        ```
        
        + Error (401)
        ```bash
        {
            "message": "Wrong credentials"
        }
        ```

+ Logout (access token)
    + Explaination
    
        To revoke `access_token`.
    
    + Endpoint
    
        post `localhost:5000/logout/access`
    
    + Response
        + Success (200)
        ```bash
        {
            "message": "Access token has been revoked"
        }
        ```
        
        + Failure (500)
        ```bash
        {
            "message": "Logout access went wrong"
        }
        ```


+ Logout (refresh token)
    + Explaination
    
        To revoke `refresh_token`.
    
    + Endpoint
    
        post `localhost:5000/logout/refresh`
    
    + Response
        + Success (200)
        ```bash
        {
            "message": "Refresh token has been revoked"
        }
        ```
        
        + Failure (500)
        ```bash
        {
            "message": "Logout refresh went wrong"
        }
        ```

+ Get another access token (refresh token)
    + Explaination
    
        Use `refresh_token` to get another valid `access_token`.
    
    + Endpoint
    
        post `localhost:5000/token/refresh`
    
    + Response
        + Success (200)
        ```bash
        {
            "access_token": access_token
        }
        ```

### User
+ Get users (access token)
    + Explaination:
    
        To get all users.

    + Endpoint
    
        get `localhost:5000/users`

    + Response
        + Success (200)
        ```bash
        [
            {
                "id": 1,
                "username": xxx
            },
        ]
        ```

### Group
+ Get groups (access token)
    + Explaination:
    
        To get all groups.

    + Endpoint
    
        get `localhost:5000/groups`

    + Response
        + Success (200)
        ```bash
        [
            {
                "id": 1
                "name": "NYU friends",
                "users": [
                    {
                        "id": 1,
                        "username": xxx
                    }
                ]
            },
        ]
        ```

        + Error (403)
        ```bash
        {
            "message": "User <username> does not exist"
        }
        ```

+ Get a group (access token)
    + Explaination:
    
        To get information of a group.

    + Endpoint
    
        get `localhost:5000/group/{id}`

    + Response
        + Success (200)
        ```bash
        {
            "id": 1
            "name": "NYU friends",
            "users": [
                {
                    "id": 1,
                    "username": "xxx"
                }
            ],
            "events": [
                {
                    "id": 1
                    "name": "xxx",
                    "added_date": "05/10/2020",
                    "pictures": [
                        {
                            "id": 1,
                            "class": "xxx" or null,
                            "is_bestshot": false,
                            "url": "xxx"
                        },
                    ]
                },
            ]
        }
        ```

        + Error (403)
        ```bash
        {
            "message": "User <username> does not exist"
        }
        ```

        + Error (404)
        ```bash
        {
            "message": "Group id {group_id} does not exist"
        }
        ```
        
+ Add group (access token)
    + Explaination:
    
        To create a group.

    + Endpoint
    
        post `localhost:5000/groups`
    
    + Parameters
    ```bash
    {
        "name": "xxx",
        "user_ids": [1, 2, 3, 4]
    }
    ```

    + Response
        + Success (200)
        ```bash
        {
            "message": "Group has been created"
        }
        ```

        + Error (404)
        ```bash
        {
            "message": "user_ids must be not empty list and its element must be integer"
        }

        + Failure (500)
        ```bash
        {
            "message": "Something went wrong"
        }
        ```

### Event
+ Get events (access token)
    + Explaination:
    
        To get all events.

    + Endpoint
    
        get `localhost:5000/events`

    + Response
        + Success (200)
        ```bash
        [
            {
                "id": 1
                "name": "xxx",
                "group": {
                    "id": 1,
                    "name": "xxx"
                },
                "added_date": "05/10/2020",
                "pictures": [
                    {
                        "id": 1,
                        "class": "xxx" or null,
                        "is_bestshot": false,
                        "url": "xxx"
                    }
                ]
            },
        ]
        ```

        + Error (403)
        ```bash
        {
            "message": "User <username> does not exist"
        }
        ```

+ Get event (access token)
    + Explaination:
    
        To get information of a event.

    + Endpoint
    
        get `localhost:5000/event/{id}`

    + Response
        + Success (200)
        ```bash
        {
            "id": 1
            "name": "xxx",
            "group": {
                "id": 1,
                "name": "xxx"
            },
            "added_date": "05/10/2020",
            "pictures": [
                {
                    "id": 1,
                    "class": "xxx" or null,
                    "is_bestshot": false,
                    "url": "xxx"
                },
            ],
            "subscription": {
                "class": "people" or "landscape" or "people/landscape"
            }
        }
        ```


        + Error (403)
        ```bash
        {
            "message": "User <username> does not exist"
        }
        ```

        + Error (404)
        ```bash
        {
            "message": "Event id <event_id> does not exist"
        }
        ```

+ Create event (access token)
    + Explaination:
    
        To create a event.

    + Endpoint
    
        post `localhost:5000/events`
    
    + Parameter
    ```bash
    {
        "name": "xxx",
        "added_date": "mm/dd/yyyy",
        "group: {
            "id": 1
        },
        "pictures": [ "url1", "url2", "url3"]
    }
    ```

    + Response
        + Success (200)
        ```bash
        {
            "message": "event has been created"
        }
        ```

        + Error (404)
        ```bash
        {
            "message": "group should not be empty hash. pictures should contain urls"
        }
        ```
        
        + Error (404)
        ```bash
        {
            "message": "Group id <group_id> does not exist"
        }
        ```
        
        + Failure (500)
        ```bash
        {
            "message": "Something went wrong"
        }
        ```

### Subscription
+ Add Subscription (access token)
    + Explaination:
    
        To add a new subscription for a event.

    + Endpoint
    
        post `localhost:5000/event/{id}/subscriptions`

    + Parameter
    ```bash
    {
        "class": "people" or "landscape" or "people/landscape"
    }
    ```

    + Response
        + Success (200)
        ```bash
        {
            "message": "Subscription has been created"
        }
        ```
        
        + Error (400)
        ```bash
        {
            "message": "class field should not be empty"
        }
        ```

        + Error (404)
        ```bash
        {
            "message": "Group id <group_id> does not exist"
        }
        ```

        + Error (404)
        ```bash
        {
            "message": "Event id <event_id> does not exist"
        }
        ```
        
        + Failure (500)
        ```bash
        {
            "message": "Something went wrong"
        }
        ```
 
 
 ### Picture
 + Register picture (access token)
    + Explaination:
    
        To register the pictures that have been uploaded by the frontend in the database.

    + Endpoint
    
        post `localhost:5000/event/{id}/pictures`
    
    + Parameters
    ```bash
    {
        "pictures": [ "url1", "url2", "url3" ]
    }
    ```

    + Response
        + Success (200)
        ```bash
        {
            "message": "Pictures has been registered"
        }
        ```

        + Error (400)
        ```bash
        {
            "message": "Pictures has been registered"
        }
        ```

        + Error (404)
        ```bash
        {
            "message": "Event id <event_id> does not exist"
        }
        ```

        + Error (404)
        ```bash
        {
            "message": "Group id <group_id> does not exist"
        }
        ```

        + Failure (500)
        ```bash
        {
            "message": "Something went wrong"
        }
        ```
        
 + Update is_bestshot (refresh token) (**for yangyao**)
    + Explaination:
    
        To update `is_bestshot`  in `pictures` table.

    + Endpoint
    
        post `localhost:5000/pictures/is_bestshot`
    
    + Parameters
    ```bash
    {
        "pictures": [ "url1", "url2", "url3" ]
    }
    ```

    + Response
        + Success (200)
        ```bash
        {
            "message": "Bestshots have been updated"
        }
        ```

        + Error (400)
        ```bash
        {
            "message": "bestshots field should not be empty"
        }
        ```
        
        + Error (404)
        ```bash
        {
            "message": "Event id <event_id> does not exist"
        }
        ```

        + Failure (500)
        ```bash
        {
            "message": "Something went wrong"
        }
        ```

 + Update class (refresh token)  (**for yangyao**)
    + Explaination:
    
        To update field `class` in `pictures` table.

    + Endpoint
    
        post `localhost:5000/pictures/class`
    
    + Parameters
    ```bash
    {
        "pictures": [ "url1", "url2", "url3" ]
    }
    ```

    + Response
        + Success (200)
        ```bash
        {
            "message": "Picture class has been registered"
        }
        ```
        
        + Error (400)
        ```bash
        {
            "message": "classes field should not be empty"
        }
        ```

        + Error (404)
        ```bash
        {
            "message": "Event id <event_id> does not exist"
        }
        ```

        + Failure (500)
        ```bash
        {
            "message": "Something went wrong"
        }
        ```
