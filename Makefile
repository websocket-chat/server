#!/usr/bin/make

REPO_DIR = ..

build: # build all containers
	@docker build -t server:latest $(REPO_DIR)/server

rebuild: # build all containers without cache
	docker build --no-cache -t server:latest $(REPO_DIR)/server

clone: # clone all containers
	@if [ ! -d $(REPO_DIR)/server ]; then git clone git@github.com:websocket-chat/server.git $(REPO_DIR)/server; fi

pull: # pull all containers
	cd $(REPO_DIR)/server && git pull

run-bg: # run all containers in the background
	@docker-compose up -d \
		server \
		mysql \
		redis

run: # run all containers in the foreground
	@docker-compose up \
		server \
		mysql \
		redis

logs: # attach to the containers live to view their logs
	@docker-compose logs -f

test: # run the tests
	@docker-compose exec server /scripts/run-tests.sh

test-dbg: # run the tests in debug mode
	@docker-compose exec server /scripts/run-tests.sh --dbg

update-venv:
	cd $(REPO_DIR)/server && . venv/bin/activate && pip install -U pip setuptools && pip install -rrequirements{,-dev}.txt
