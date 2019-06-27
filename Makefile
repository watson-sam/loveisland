.PHONY: na

clean:
	rm -rf venv
	rm -rf build
	rm -rf loveisland.egg-info
	rm -rf dist

venv:
	python3 -m venv venv

wheel:
	venv/bin/pip3 install wheel

req:
	venv/bin/pip3 install -r requirements.txt -e .

build: venv wheel req

deploy:
	venv/bin/python3 setup.py bdist_wheel
	venv/bin/pip3 install loveisland

full: clean build deploy
