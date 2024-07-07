# User Management and Organization API using Flask

This is a Python API using Flask Framework that Connects the application to a Postgres database server. ORM like SQLAlchemy was used

### Base Endponit
[GET][text](https://user-auth-org.vercel.app)

### Register Endpoint
#[POST] /auth/register Registers a users and creates a default organisation Register request body:

```json
{
  "firstName": "Chinomso",
  "lastName": "Cynthia",
  "email": "chi@gmail.com",
  "password": "securepassword",
  "phone": "123-3333-8888"
}
```

### Login Endpoint
- https://user-auth-org.vercel.app/auth/login

```json
{
  "email": "elora@gmail.com",
  "password": "securepassword"
}
```

### Create Organization Endpoint
- https://user-auth-org.vercel.app/api/organisations

```json
{
  "name": "hng",
  "description": "This is an organization for hng Developers"
}
```

### Add user to organization Endpoint
- https://user-auth-org.vercel.app/api/organisations/<:orgid>/

```json
{
  "userId": "<userId>"
}
```

### Register Endpoint
- https://user-auth-org.vercel.app/auth/register

```json
{
  "firstName": "Chinomso",
  "lastName": "Cynthia",
  "email": "chi@gmail.com",
  "password": "securepassword",
  "phone": "123-3333-8888"
}
```

### Register Endpoint
- https://user-auth-org.vercel.app/auth/register

```json
{
  "firstName": "Chinomso",
  "lastName": "Cynthia",
  "email": "chi@gmail.com",
  "password": "securepassword",
  "phone": "123-3333-8888"
}
```

### Framework:
- Flask

### Python Version:
- 3.11.9

### Render is used to host the postgres DB and Vercel for deployment:
- [Render](https://dashboard.render.com/): Provides weather status based on location.
- [Vercel](https://vercel.com/): used for application deployment and hosting.



Description:

This API will serve fetch requests with the help of Flask and we will receive weather data at OpenWeatherMap, based on the city which is derived from given IP address by usign IPinfo. io. It then sends back a JSON object with their IP, city location and an introduced statement followd by the temp in that part of ith world

You can use this API for getting weather detail according to your location.
