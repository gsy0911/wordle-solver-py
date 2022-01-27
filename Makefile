MODULE_NAME := {your_module}

.PHONY: help
help:
	@printf "\033[36m%-30s\033[0m %-50s %s\n" "[Sub command]" "[Description]" "[Example]"
	@grep -E '^[/a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | perl -pe 's%^([/a-zA-Z_-]+):.*?(##)%$$1 $$2%' | awk -F " *?## *?" '{printf "\033[36m%-30s\033[0m %-50s %s\n", $$1, $$2, $$3}'


.PHONY: test-python
test-python: ## test python ## make test-python
	pytest ./test -vv --cov=./$(MODULE_NAME) --cov-report=html

.PHONY: deploy
deploy: ## deploy to PyPI ## make deploy
	twine upload dist/*

.PHONY: test-deploy
test-deploy: ## deploy to test-PyPI ## make test-deploy
	twine upload -r testpypi dist/*

.PHONY: wheel
wheel: clean ## generate wheel ## make wheel
	python setup.py sdist bdist_wheel

.PHONY: clean
clean: ## remove all files in dist ## make clean
	rm -f -r $(MODULE_NAME).egg-info/* dist/* -y

.PHONY: format
format: ## format with black ## make format
	isort $(MODULE_NAME)
	isort test
	black .

.PHONY: lint
lint: ## lint python (flake8 and mypy) ## make lint
	pflake8 $(MODULE_NAME)
	mypy $(MODULE_NAME)
	bandit --recursive src
