Fyyur
-----

## Introduction

Fyyur is a musical venue and artist booking site that facilitates the discovery and bookings of shows between local performing artists and venues. This site lets you list new artists and venues, discover them, and list shows with artists as a venue owner.

Your job is to build out the data models to power the API endpoints for the Fyyur site by connecting to a PostgreSQL database for storing, querying, and creating information about artists and venues on Fyyur.

## Main Files: Project Structure

  ```sh
  ├── README.md
  ├── app.py *** the main driver of the app. Includes your SQLAlchemy models.
                    "python app.py" to run after installing dependencies
  ├── config.py *** Database URLs, CSRF generation, etc
  ├── enums.py
  ├── error.log
  ├── forms.py
  ├── models.py
  ├── requirements.txt *** The dependencies we need to install with "pip3 install -r requirements.txt"
  ├── static
  │   ├── css 
  │   ├── font
  │   ├── ico
  │   ├── img
  │   └── js
  └── templates
      ├── errors
      ├── forms
      ├── layouts
      └── pages
  ```

Overall:
* Models are located in the `MODELS` section of `app.py`.
* Controllers are also located in `app.py`.
* The web frontend is located in `templates/`, which builds static assets deployed to the web server at `static/`.
* Web forms for creating data are located in `form.py`

## Development Setup

First, [install Python](https://www.python.org/downloads/) and [install PostgreSQL](https://www.postgresql.org/download/) if you haven't already.

To start and run the local development server,

1. Initialize and activate a virtual environment:

  ```
  $ cd YOUR_PROJECT_DIRECTORY_PATH/
  $ py -3 -m venv env
  $ env\Scripts\activate
  ```

2. Install the dependencies:

  ```
  $ py -m pip install -r requirements.txt
  ```

3. Configuration Keys "SQLALCHEMY_DATABASE_URI" (YOUR_PROJECT_DIRECTORY_PATH/config.py). Reference [connection URI format](https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/#connection-uri-format)

4. Flask-Migrate:

  ```
  $ flask db init
  $ flask db migrate
  $ flask db upgrade
  ```

5. Run the development server:

  ```
  $ flask --app app run
  ```

  /

  ```
  $ set FLASK_APP=app
  $ flask run
  ```

6. Verify on the Browser

  Navigate to project homepage [http://127.0.0.1:5000/](http://127.0.0.1:5000/) or [http://localhost:5000](http://localhost:5000) 
# fyyur-project-udacity
