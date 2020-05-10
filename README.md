## Installation
At project root directory,

```bash
vagrant up
vagrant ssh -- -L 5000:localhost:5000
cd /vagrant/flask-aws
flask run
```

## Token

### Registration

#### Explaination
To register a user, and then get `access_token` as well as `refresh_token` back.  
`access_token` is used to access api with person information. Default expiration time is 30 mins.  
`refresh_token` is used to get another `access_token`. Default expiration time is 30 days.  

#### Endpoint
post `localhost:5000/registration`

#### Parameters
1. username
2. password

#### Response
1. Success (200)
```bash
{
    'message': 'User <username> was created',
    'access_token': access_token,
    'refresh_token': refresh_token
}
```

1. Failure (500)
```bash
{
    'message': 'Something went wrong'

}
```


---


### Login

#### Explaination
Use `username` and `password` to login, and then get `access_token` as well as `refresh_token` back.

#### Endpoint
post `localhost:5000/login`

#### Header
Require "Authorization: Bearer <access_token>" in hearder.

#### Response
1. Success (200)
```bash
{
    'message': 'Logged in as <username>',
    'access_token': access_token,
    'refresh_token': refresh_token
}
```

2. Failure (200)
```bash
{
    'message': 'Wrong credentials'
}
```


---


### Logout access token

#### Explaination
To revoke `access_token`.

#### Endpoint
post `localhost:5000/logout/access`

#### Header
Require "Authorization: Bearer <access_token>" in hearder.

#### Response
1. Success (200)
```bash
{
    'message': 'Access token has been revoked'
}
```

2. Failure (500)
```bash
{
    'message': 'Logout access went wrong'
}
```


---


### Logout refresh token

#### Explaination
To revoke `refresh_token`.

#### Endpoint
post `localhost:5000/logout/refresh`

#### Header
Require "Authorization: Bearer <refresh_token>" in hearder.

#### Response
1. Success (200)
```bash
{
    'message': 'Refresh token has been revoked'
}
```

2. Failure (500)
```bash
{
    'message': 'Logout refresh went wrong'
}
```

---


### Get another access token

#### Explaination
Use `refresh_token` to get another valid `access_token`.

#### Endpoint
post `localhost:5000/token/refresh`

#### Header
Require "Authorization: Bearer <refresh_token>" in hearder.

#### Response
1. Success (200)
```bash
{
    'access_token': access_token
}
```
