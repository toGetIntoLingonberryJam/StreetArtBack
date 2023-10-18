# install libs
pip install -r requirements.txt

cd src

# run migrations
alembic upgrade head

# run application
uvicorn app.app:app --reload
