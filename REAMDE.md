### DO WPROWADZANIA ZMIAN W KONTENERZE:
```
docker-compose -d --build
docker-compose up
```

### Aby stworzyć bazę danych:
```
docker-compose exec web flask shell
```


### A w konsoli:

```
from app import db

db.drop_all()
db.create_all()
db.session.commit()
```

### Aby stworzyć swojego użytkownika:

```
db.session.add(User(email='abc@example.com'))
db.session.commit()
```
