# taximaster

## РАЗВЁРТЫВАНИЕ
Разертывание производилось на debian-10
- sudo apt install docker-compose docker
- sudo systemctl start docker
- git clone https://github.com/andrewisakov/taximaster

## СБОРКА
- cd taximaster
- docker-compose build

## ЗАПУСК
- docker-compose up -d  (запуск)
- docker-compose logs (посмотреть не упало ли что и последние строки логов)

## ОСТАНОВ
- docker-compose down

## ЛОГИ
- /var/logsudo apt -y install g++ postgresql-server-dev-all libffi6 libffi-dev
