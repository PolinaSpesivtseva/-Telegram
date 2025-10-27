Это по сути агрегация наших микросервисов в один ентрипоинт запуска.

### Load

```
git clone https://git.miem.hse.ru/1655/service.git
cd service
git submodule update --init --recursive
```

### Update

```
cd service 
git submodule update --recursive --remote 
```

### Lounch

Не забудь выставить переменную дебага и основные env переменные в **.env** файле.

`docker compose up --build -d`

`docker compose restart`

### Troubleshoot

1. При попытке поменять пользователя и пароль в базе данных, возможно ничего не будет меняться
Это потому, что после инициализации mongo-db уже не будет менять эти данные. Вариант
либо удалять целиком вольюм, либо заходить в контейнер и командами управления базой
менять эти значения.
