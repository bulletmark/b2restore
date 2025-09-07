NAME = $(shell basename $(CURDIR))
PYNAME = $(subst -,_,$(NAME))
PYFILES = $(PYNAME).py
SHFILES = $(NAME)-create-git $(NAME)-create-dummy-files

check::
	shellcheck $(SHFILES)
	ruff check $(PYFILES)
	mypy $(PYFILES)
	pyright $(PYFILES)
	vermin -vv --no-tips -i $(PYFILES)

build::
	rm -rf dist
	uv build

upload: build
	uv-publish

format::
	ruff check --select I --fix $(PYFILES) && ruff format $(PYFILES)

clean::
	@rm -vrf *.egg-info .venv/ build/ dist/ __pycache__/
