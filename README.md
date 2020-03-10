# AHTI

:ocean: AHTI API :anchor:

## Development with Docker

1. Create a `docker-compose.env.yaml` file in the project folder:
   * You can use `docker-compose.env.yaml.template` as a base, it does not need any changes
     if you want all features enabled.
   * Change `DEBUG` and the rest of the Django settings if needed.
     * `TOKEN_AUTH_AUTHSERVER_URL`, URL for [tunnistamo](https://github.com/City-of-Helsinki/tunnistamo) authentication service
   * Set entrypoint/startup variables according to taste.
     * `CREATE_SUPERUSER`, creates a superuser with credentials `admin`:`admin` (admin@example.com)
     * `APPLY_MIGRATIONS`, applies migrations on startup
     * `IMPORT_FEATURES`, imports features from configured sources on startup

2. Run `docker-compose up`

The project is now running at [localhost:8082](http://localhost:8082)

## Development without Docker

Prerequisites:

* PostgreSQL 10
* PostGIS 2.5
* Python 3.8

### Installing Python requirements

* Run `pip install -r requirements.txt`
* Run `pip install -r requirements-dev.txt` (development requirements)

### Database

To setup a database compatible with default database settings:

Create user and database

    sudo -u postgres createuser -P -R -S ahti  # use password `ahti`
    sudo -u postgres createdb -O ahti ahti

Create extensions in the database

    sudo -u postgres psql ahti -c "CREATE EXTENSION postgis;"

Allow user to create test database

    sudo -u postgres psql -c "ALTER USER ahti CREATEDB;"

### Daily running

* Create `.env` file: `touch .env`
* Set the `DEBUG` environment variable to `1`.
* Run `python manage.py migrate`
* Run `python manage.py createsuperuser`
* Run `python manage.py runserver localhost:8082`

The project is now running at [localhost:8082](http://localhost:8082)

## Keeping Python requirements up to date

1. Install `pip-tools`:

    * `pip install pip-tools`

2. Add new packages to `requirements.in` or `requirements-dev.in`

3. Update `.txt` file for the changed requirements file:

    * `pip-compile requirements.in`
    * `pip-compile requirements-dev.in`

4. If you want to update dependencies to their newest versions, run:

    * `pip-compile --upgrade requirements.in`

5. To install Python requirements run:

    * `pip-sync requirements.txt`

## Code format

This project uses
[`black`](https://github.com/ambv/black),
[`flake8`](https://gitlab.com/pycqa/flake8) and
[`isort`](https://github.com/timothycrosley/isort)
for code formatting and quality checking. Project follows the basic
black config, without any modifications.

Basic `black` commands:

* To let `black` do its magic: `black .`
* To see which files `black` would change: `black --check .`

[`pre-commit`](https://pre-commit.com/) can be used to install and
run all the formatting tools as git hooks automatically before a
commit.
