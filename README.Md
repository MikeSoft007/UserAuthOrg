# User Management and Organization API using Flask

This is a Python API using Flask Framework that Connects the application to a Postgres database server. ORM like SQLAlchemy was used

### Base Endponit
- (https://user-auth-org.vercel.app)

### Register Endpoint
#[POST] /auth/register Registers a users and creates a default organisation Register request body:

```json
{
	"firstName": "string",
	"lastName": "string",
	"email": "string",
	"password": "string",
	"phone": "string",
}
```

### Login Endpoint
- [POST] /auth/login : logs in a user. When you log in, you can select an organisation to interact with 

```json
{
	"email": "string",
	"password": "string",
}
```

### Get a user Organization(s) Endpoint
- [GET] /api/organisations: a user gets their own record or user record in organisations they belong to or created [PROTECTED]


### Get a single organization Endpoint
- [GET] /api/organisations/:orgId the logged in user gets a single organisation record [PROTECTED]


### Create organization Endpoint
- [POST] /api/organisations : a user can create their new organisation [PROTECTED]

```json
{
	"name": "string", // Required and cannot be null
	"description": "string",
}
```

### Add a user to a particluar organization Endpoint
- [POST] /api/organisations/:orgId/users : adds a user to a particular organisation

```json
{
	"userId": "string"
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
