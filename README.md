# taximaster

# РАЗВЁРТЫВАНИЕ
Разертывание производилось на debian-10
sudo apt install docker-compose docker
sudo systemctl start docker
git clone https://github.com/andrewisakov/taximaster

# СБОРКА и ЗАПУСК
cd taximaster
docker-compose build
docker-compose up -d  (запуск)
docker-compose logs (посмотреть не упало ли что и последние строки логов)
docker-compose down

# ЛОГИ
/var/log