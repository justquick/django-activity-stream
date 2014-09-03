clean:
	find . -name '*.pyc' -type f -delete
	find . -name __pycache__ -type d -delete

messages:
	cd actstream && django-admin.py makemessages -l en && django-admin.py compilemessages -l en && cd ..

docs:
	pip install -r docs/requirements.txt
	sphinx-build -W -b html docs/source docs/build/html
	sphinx-build -W -b linkcheck docs/source docs/build/html

dist:
	python setup.py sdist && echo "OK?" && read

.PHONY: clean messages docs dist
