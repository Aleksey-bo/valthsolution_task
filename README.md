# 🔎 Name Info Service

This project implements name-based data collection using a third-party service, with the results saved to a database.  
It also includes JWT-based user authentication and a protected endpoint.  
The entire project runs in Docker containers.

---

## 🛠 Technologies

- Django / DRF  
- Docker  
- PostgreSQL  
- pytest

---

## 🚀 Running the Server

Create a `.env` file next to `docker-compose.yml` with the following variables:

```env
DB_NAME=
DB_USER=
DB_PASS=
DB_HOST=       ⚠️ Important: DB_HOST must match the name of the database service in docker-compose.yml, which is db in our case.
DB_PORT=
SECRET_KEY=
ALGORITHM=
ACCESS_TOKEN_EXPIRE_MINUTES=
```

## ⚙️ Build and start the containers:
```
docker-compose build --no-cache
docker-compose up -d
```
On the first run, you need to apply migrations. Enter the server container:
```
docker exec -it name-service /bin/sh
```
Then run the migrations:
```
python manage.py makemigrations
python manage.py migrate
```
And start server:
```
python manage.py runserver
```
After that, you can access the Swagger documentation at:
http://localhost:8000/swagger/

## ✅ Testing
```
docker-compose build --no-cache
docker-compose run --rm web sh
```
Then apply the migrations:
```
python manage.py makemigrations
```
To run the tests, use:
```
pytest
```