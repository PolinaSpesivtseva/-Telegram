# Regular Django Example Application

## Run using Docker

```sh
docker-compose up --build
```

You should then be able to open your browser on http://localhost:8000 and see a page with links to sign in or sign up.

## Edit database
```
docker exec -it <container id> bash
python manage.py flush
...
```

# Run Locally
Assuming you use virtualenv, follow these steps to download and run the django-allauth example application in this directory:

```sh
git clone git@github.com:pennersr/django-allauth.git
cd django-allauth/examples/regular-django
virtualenv venv
. venv/bin/activate
pip install "../..[mfa,saml,socialaccount]"
```

Now we need to create the database tables and an admin user. Run the following and when prompted to create a superuser choose yes and follow the instructions:
```
python manage.py migrate
python manage.py createsuperuser
```

Finally, run the Django development server:
```
python manage.py runserver
```

You should then be able to open your browser on http://localhost:8000 and see a page with links to sign in or sign up.