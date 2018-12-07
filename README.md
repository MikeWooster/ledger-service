[![Build Status](https://travis-ci.org/MikeWooster/ledger-service.svg?branch=master)](https://travis-ci.org/MikeWooster/ledger-service)

# Ledger Service

Providing a ledger as a service.

# Developing

Run the dependencies using docker-compose
```
docker-compose up -d
```

Install the requirements
```
pip install -e .[dev]
```

Run the application
```
flask run
```

### Database Migrations
Migrations are managed using `flask-migrate`, a flask extension that handles SQLAlchemy migrations using Alembic.

Apply the migrations
```
flask db upgrade
```

When making database changes, new migrations can be generated with
```
flask db migrate
```
