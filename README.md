# teachrUI 
[![Build Status](https://travis-ci.org/Discovery-VSTS/teacherui.svg?branch=master)](https://travis-ci.org/Discovery-VSTS/teacherui)

Zero start build
--------------------------

Create a local PostgreSQL database with the following parameters:

```javascript
SERVER_NAME: 'travisci'
USER: 'postgres'
PASSWORD: ''
HOST: 'localhost'
PORT: [DEFAULT PORT]
```

_Feel free to edit these parameters in the settings.py file._

Create virtual environment with python 3.5+ as base interpreter

Run `pip install -r requirements.txt`

Finally, run `python manage.py migrate` and then `python manage.py runserver`

_Always make sure you are in the proper virtual environment_

Run for development
-------------------

Just run `python manage.py runserver`
