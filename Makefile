install: venv
	venv/bin/pip install --upgrade -r requirements.txt -t app/lib

venv: requirements-dev.txt
	virtualenv -p python2.7 --setuptools venv
	venv/bin/pip install --upgrade -r requirements-dev.txt

config_test: venv
	venv/bin/python tools/generate.py -s templates/settings.py.in -c cfg/test_env.json -d app

config_prod: venv
	venv/bin/python tools/generate.py -s templates/settings.py.in -c cfg/prod.json -d app

local: config_test
	source venv/bin/activate && dev_appserver.py app

clean:
	rm -rf venv
	rm -rf app/lib/*
	find . -name "*.pyc" -exec rm {} \;

test: config_test
	venv/bin/nosetests -vv --nologcapture --nocapture app/test/

deploy:
	gcloud app deploy app/app.yaml app/index.yaml

