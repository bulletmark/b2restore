NAME = $(shell basename $(CURDIR))
PYNAME = $(subst -,_,$(NAME))
SCRIPTS = $(NAME)-create-dummy-files $(NAME)-create-git

all:
	@echo "Type sudo make install|uninstall"
	@echo "or make sdist|upload|check|clean"

install:
	pip3 install -U --root-user-action=ignore .

uninstall:
	pip3 uninstall --root-user-action=ignore $(NAME)

sdist:
	rm -rf dist
	python3 setup.py sdist bdist_wheel

upload: sdist
	twine3 upload --skip-existing dist/*

check:
	shellcheck $(SCRIPTS)
	flake8 $(PYNAME).py setup.py
	vermin --no-tips -i $(PYNAME).py setup.py
	python3 setup.py check

clean:
	@rm -vrf *.egg-info build/ dist/ __pycache__/
