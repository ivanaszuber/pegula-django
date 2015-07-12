# Pegula Python/Django Backend

This Django project provides the backend Web service API for the [Pegula](https://github.com/ivanaszuber/pegula-crm) CRM web application.

To run the `pegula` server locally run the following commands:

```
git clone git@github.com:ivanaszuber/pegula-django.git pegula-django/

cd pegula-django

pip3 install -U -r requirements.txt  # install Python dependencies

python3 manage.py migrate #create the database and load initial data

python3 manage.py runserver #run the server on localhost:5050
```
