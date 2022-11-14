PYTHON_ENV=C:\Users\moopi\AppData\Local\pypoetry\Cache\virtualenvs\new_year_bot-8OIMA0hq-py3.9\Scripts\python

run:
	$(PYTHON_ENV) bot.py
beauty:
	$(PYTHON_ENV) -m isort .
	$(PYTHON_ENV) -m black .
	$(PYTHON_ENV) -m flake8 .  --exit-zero
	$(PYTHON_ENV) -m autoflake --remove-all-unused-imports --remove-unused-variables --in-place -r .
install-beautifier:
	pip install isort black flake8 autoflake
