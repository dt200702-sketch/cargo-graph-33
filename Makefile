.PHONY: test check demo

test:
	PYTHONPATH=src python3 -m unittest discover -s tests -v

check: test
	python3 -m compileall -q src tests

demo:
	./run.sh examples/test.ini
