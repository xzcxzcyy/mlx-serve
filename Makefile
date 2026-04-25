.PHONY: run install

run:
	conda run --no-capture-output -n mlx python run.py

install:
	conda run -n mlx pip install -r requirements.txt
