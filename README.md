# besdd
A baby's eat-sleep-diaper diary.

Track your baby's sleeping, eating and relieving habits.

This started out as just a script to plot a histogram from spreadsheet data, but since
logging data via Excel/Libreoffice/whatever is tedious, uncomfortable and error prone, I
created this web app.

Consider this beta quality at best - stuff may work or not and may break unexpectedly.

### Features:

- Log sleep phases, meals and changed diapers
- Log height/weight measurements
- Log special events (like first steps, words, etc.)
- Log diary entries
- Allow other users to add+view child data
- Display the data in a summary list or in graphical form

Sleep, meals and diapers work best currently, since we're using it on a daily basis. More
stuff will be added when I find some spare time.

### Setup

To get this up and running, clone the repo and perform the following steps:

- Set up a virtual environment and activate it:

        python3 -m venv venv
        . venv/bin/activate

- Install required packages:
  
        pip3 install -r requirements.txt

- Create a private key:

        dd if=/dev/urandom count=1 bs=56 | base64 > secret_key.txt

- Run the db-migrations and start the development server:

        ./manage.py migrate
        ./manage.py runserver

- Surf to localhost:8000

Disable DEBUG in settings.py if you want to run it in production!

### Used software

(not in a particular order or complete)

- Python
- Django
- Bootstrap
- JQuery
- Vue.js
- moment.js
