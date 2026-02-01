# Hysteria 2 Server (Minimal)

## Описание
Развертывание Hysteria 2 в минимальной конфигурации.  

**Протокол:** Высокоскоростное туннелирование на базе QUIC (UDP) с агрессивным контролем перегрузки. Оптимизация для обхода блокировок, онлайн-игр и стриминга в нестабильных сетях.  

**Особенности:** отсутствие графического интерфейса (GUI) и сторонних панелей управления. Прямая работа с бинарным файлом через Docker.

## Развертывание

### 1. Подготовка сертификатов
```bash
mkdir -p hysteria/certs
openssl req -x509 -nodes -newkey rsa:2048 -keyout hysteria/certs/server.key -out hysteria/certs/server.crt -subj "/CN=bing.com" -days 3650
```

### 2. Запуск сервиса
```bash
docker-compose up -d
```

### 3. Управление пользователями
Редактирование секции `userpass` в `config.yaml` с последующим выполнением `docker-compose restart`.

## Параметры подключения
**Шаблон URI:**
`hysteria2://<LOGIN>:<PASSWORD>@<SERVER_IP>:4433/?sni=bing.com&obfs=salamander&obfs-password=h2_obfs_SecretKey_5582&insecure=1#Hysteria2`

**Пример для user1:**
`hysteria2://user1:h2_auth_StrongPass_9921@192.168.1.10:4433/?sni=bing.com&obfs=salamander&obfs-password=h2_obfs_SecretKey_5582&insecure=1#User1`