# Team Fox Major Group project

## Team members
The members of the team are:<br />
- Luke Polanowski (luke.polanowski@kcl.ac.uk)<br />
- Alex Rubio-Blobaum (alex.rubio_blobaum@kcl.ac.uk)<br />
- Harshit Sharma (harshit.sharma@kcl.ac.uk)<br />
- Tsz Chang (tsz.chang@kcl.ac.uk)<br />
- Mark Chester-Jude-Emmanuel (mark.chester_jude_emmanuel@kcl.ac.uk)<br />
- Ka Chun (Ivan) Chong (ka.c.chong@kcl.ac.uk)<br />
- Isabella Cowin (isabella.cowin@kcl.ac.uk)<br />
- Mohammad Abubakr Iqbal (mohammad.a.iqbal@kcl.ac.uk)<br />
- Adam Moujar-Bakhti (adam.moujar_bakhti@kcl.ac.uk)<br />
- Vaibhavkumar Patel (vaibhavkumar.patel@kcl.ac.uk)

## Project structure
The project is called `student_query_system` (Student Query System).  It currently consists of a single app `ticketing` where all functionality resides.

## Deployed version of the application
The deployed version of the application can be found at *<[https://k21003979.pythonanywhere.com/](URL)>*.

## Installation instructions
To install the software and use it in your local development environment, you must first set up and activate a local development environment.  From the root of the project:

```
$ virtualenv venv
$ source venv/bin/activate
```

Install all required packages:

```
$ pip3 install -r requirements.txt
$ pip3 install -r dev-requirements.txt
```
Run the Server:

```
$ python3 manage.py runserver
```

Migrate the database:

```
$ python3 manage.py migrate
```

Seed the development database with:

```
$ python3 manage.py seed
```

Unseed the development database with:

```
$ python3 manage.py unseed
```

Run all tests with:
```
$ python3 manage.py test
```

## Sources
The packages used by this application are specified in `requirements.txt`
The packages exclusively used by the developers are specified in `dev-requirements.txt`

## API

For the AI natural language processing, we used an API to an already trained model
The URL for the model is https://huggingface.co/facebook/bart-large-mnli
The API has been used in ticketing.nlp.ml_api.py
