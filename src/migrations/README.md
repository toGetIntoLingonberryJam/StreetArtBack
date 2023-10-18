
Чтобы создать миграцию
```sh
alembic revision --autogenerate -m "Migration name"
```

---

Чтобы мигрировать базу данных в последнюю версию
```sh
cd .. 

alembic upgrade head
```