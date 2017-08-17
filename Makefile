

clean:
	rm -rf *.egg-info; rm -rf boolean2/*.egg-info
	rm -rf boolean2/__pycache__; rm -f boolean2/*.pyc
	rm -rf boolean2/ply/__pycache__; rm -rf boolean2/ply/*.pyc
	rm -rf boolean2/plde/__pycache__; rm -f boolean2s/plde/*.pyc
install:
	python setup.py install

develop:
	python setup.py develop 

uninstall:
	python setup.py develop -u

test:
	python tests/test_all.py 

