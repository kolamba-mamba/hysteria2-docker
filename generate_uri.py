import re
import os
import urllib.request
import sys

# Устанавливаем UTF-8 для корректного вывода кириллицы в Windows-терминале
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def get_public_ip():
    # Используем сервис, который принудительно возвращает IPv4
    services = ['https://api4.ipify.org', 'https://v4.ident.me', 'https://checkip.amazonaws.com']
    for service in services:
        try:
            return urllib.request.urlopen(service, timeout=5).read().decode('utf-8').strip()
        except:
            continue
    return None

def parse_config(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем, активен ли блок ACME (не закомментирован)
    acme_active = False
    for line in content.splitlines():
        if line.strip().startswith('acme:'):
            acme_active = True
            break

    # Извлечение домена из ACME
    addr_match = re.search(r'acme:\s+domains:\s+-\s+"([^"]+)"', content)
    domain = addr_match.group(1) if addr_match else None
    
    # Извлечение порта
    port_match = re.search(r'listen: :(\d+)', content)
    port = port_match.group(1) if port_match else "4433"
    
    # Извлечение данных обфускации
    obfs_type_match = re.search(r'obfs:\s+type:\s+(\w+)', content)
    obfs_type = obfs_type_match.group(1) if obfs_type_match else None
    
    obfs_pass_match = re.search(r'salamander:\s+password:\s+"([^"]+)"', content)
    obfs_pass = obfs_pass_match.group(1) if obfs_pass_match else ""
    
    # Извлечение пользователей
    users = []
    userpass_section = re.search(r'userpass:\s+(.*?)(?=\n\w+:|\Z)', content, re.DOTALL)
    if userpass_section:
        for line in userpass_section.group(1).splitlines():
            stripped = line.strip()
            if stripped.startswith('#') or not stripped:
                continue
            user_match = re.match(r'(\w+):\s+"([^"]+)"', stripped)
            if user_match:
                users.append(user_match.groups())
            
    # Пытаемся найти SNI в блоке tls или комментариях (по умолчанию www.bing.com)
    sni_match = re.search(r'sni:\s+"?([^" \n]+)"?', content)
    sni = sni_match.group(1) if sni_match else "www.bing.com"
            
    return acme_active, domain, port, obfs_type, obfs_pass, users, sni

def generate():
    config_path = 'config.yaml'
    if not os.path.exists(config_path):
        print(f"Ошибка: файл {config_path} не найден.")
        return

    acme_active, domain, port, obfs_type, obfs_pass, users, config_sni = parse_config(config_path)
    
    if acme_active:
        addr = domain if domain and domain != "ВАШ_ДОМЕН" else "ВАШ_ДОМЕН"
        sni = addr
        is_insecure = False
        print(f"--- РЕЖИМ: ACME (Домен) ---")
    else:
        # Пытаемся получить IP сервера
        public_ip = get_public_ip()
        addr = public_ip if public_ip else "ВАШ_IP"
        # Для самоподписных используем найденный SNI (или дефолт)
        sni = config_sni 
        is_insecure = True
        print(f"--- РЕЖИМ: Самоподписной (IP) ---")

    print(f"Адрес сервера: {addr}\n")
    
    for user, password in users:
        uri = f"hysteria2://{user}:{password}@{addr}:{port}/?sni={sni}"
        
        if obfs_type:
            uri += f"&obfs={obfs_type}&obfs-password={obfs_pass}"
        
        if is_insecure:
            uri += "&insecure=1"
            
        uri += f"#{user}"
        
        print(f"Пользователь: {user}")
        print(f"URI: {uri}\n")

if __name__ == "__main__":
    generate()
