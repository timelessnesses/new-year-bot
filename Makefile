

run:
	$(PYTHON_ENV) bot.py
beauty:
	$(PYTHON_ENV) -m isort .
	$(PYTHON_ENV) -m black .
	$(PYTHON_ENV) -m flake8 .  --exit-zero
	$(PYTHON_ENV) -m autoflake --remove-all-unused-imports --remove-unused-variables --in-place -r .
install-beautifier:
	pip install isort black flake8 autoflake
