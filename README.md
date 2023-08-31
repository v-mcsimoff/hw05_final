# Yatube social network

Social network of bloggers. Allows users to write posts and publish them in different groups, subscribe to posts, add and delete posts and comment on them.
Users also can subscribe to their favorite bloggers.
The project can be checked at: http://mcsimov.pythonanywhere.com/
The information could be also retrieved using API.

## Installation instructions
***- Clone the repository:***
```
git clone git@github.com:v-mcsimoff/hw05_final.git
```

***- Install and activate the virtual environment:***
- For MacOS
```
python3 -m venv venv
```
- For Windows
```
python -m venv venv
source venv/bin/activate
source venv/Scripts/activate
```

***- Install dependencies from requirements.txt:***
```
pip install -r requirements.txt
```

***- Apply migrations:***
```
python manage.py migrate
```

***- In the folder with the manage.py file, run the command:***
```
python manage.py runserver
```

## Technologies:
- Python 3.7
- Django 2.2
- REST API

## Author
Vladimir Maksimov
