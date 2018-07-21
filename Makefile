setup_test:
	pip3 install --user -r requirements_test.txt
	
test:
	pytest -vv
	
deploy:
	serverless deploy
