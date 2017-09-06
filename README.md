# gae-flask-skeleton [![Circle CI Status](https://circleci.com/gh/oddball/gae-flask-skeleton.svg?style=shield&circle-token=5c12207688e1526f6cf1e8913fbed6ebfa9ee43f)](https://circleci.com/gh/oddball/gae-flask-skeleton) 

Simple setup of Google App Engine for python, using Flask and Flask-Login, with unittests, integration tests and test of task queues.

It is not a complete system, but a starting point. Add your own OAuth library.

Continous integration is running on CircleCI.


First time
----------
On MacOSX, get google-cloud-sdk
```
brew install Caskroom/cask/google-cloud-sdk
gcloud components install app-engine-python
gcloud auth login
```


From clean repo
---------------
```
make
```

Configure
---------------
```
make config_test
```

Local dev server
----------------
```
make local
```

Deploy to google
----------------
```
make deploy
```

Running the unittests
---------------------
```
make test
```

example of running single test
```
venv/bin/nosetests -vv --nologcapture --nocapture app/test/tests/testcases.py -m test_backoffice
```

