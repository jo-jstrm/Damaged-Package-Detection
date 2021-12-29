.PHONY : install setup

install:
	pip install -r requirements.txt && pip install .
test:
	pytest ./tests
coverage:
	pytest --cov=./aisscv/ ./tests   
cov: coverage
documentation:	
	bash -c "cd docs && make html"
docs: documentation

setup:
	git submodule update --init --recursive
	make install
