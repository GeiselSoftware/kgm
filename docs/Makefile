.PHONY: docs

default: install

all: install build


h help:
	@grep '^[a-z]' Makefile


install:
	pip install pip --upgrade
	pip install -r requirements.txt

upgrade:
	pip install pip --upgrade
	pip install -r requirements.txt --upgrade


s serve:
	mkdocs serve -a 0.0.0.0:8000


b build:
	mkdocs build --strict

d deploy:
	mkdocs gh-deploy --strict --force
