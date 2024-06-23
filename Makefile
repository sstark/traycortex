
MAKEFLAGS += --no-print-directory
PROGRAM := traycotrex
PROGRAM_FULLPATH := $(shell which $(PROGRAM) 2>/dev/null)
DEBUG_PORT = 5678
VERBOSE =

all: test typecheck lint

test:
ifdef VERBOSE
	poetry run pytest -vvv
else
	@poetry run pytest
endif

typecheck:
ifdef VERBOSE
	poetry run mypy
else
	@poetry run mypy
endif

lint:
ifdef VERBOSE
	flake8
else
	@flake8
endif

debug:
	python -m debugpy --wait-for-client --listen 127.0.0.1:$(DEBUG_PORT) \
		$(PROGRAM_FULLPATH) $(OPTS)

shell:
	poetry shell

push-all: test typecheck lint
	@git remote | xargs -L1 git push --all

build: test typecheck lint
	poetry build -f wheel

coverage:
	coverage run -m pytest
	coverage report -m

release: build
	poetry publish

release-test: build
	poetry publish -r test-pypi

clean:
	rm -rf dist
	rm -rf .mypy_cache
	find . -type d -name __pycache__ -print0 | xargs -0 rm -rf
