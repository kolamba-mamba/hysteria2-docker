import re
import os

def parse_config(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Извлечение адреса (IP или домена) из секции ACME
    # Ищем формат: - "адрес"
    addr_match = re.search(r'acme:\s+domains:\s+-\s+"([^"]+)"', content)
    server_addr = addr_match.group(1) if addr_match else "YOUR_IP_OR_DOMAIN"
    
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
        user_matches = re.findall(r'(\w+):\s+"([^"]+)"', userpass_section.group(1))
        for u, p in user_matches:
            users.append((u, p))
            
    return server_addr, port, obfs_type, obfs_pass, users

def generate():
    config_path = 'config.yaml'
    if not os.path.exists(config_path):
        print(f"Ошибка: файл {config_path} не найден.")
        return

    addr, port, obfs_type, obfs_pass, users = parse_config(config_path)
    
    if addr == "ВАШ_IP_ИЛИ_ДОМЕН":
        print("ВНИМАНИЕ: В config.yaml не указан реальный IP адрес.")
        print("Пожалуйста, замените 'ВАШ_IP_ИЛИ_ДОМЕН' на ваш реальный IP и запустите скрипт снова.\n")

    print(f"--- ССЫЛКИ ДЛЯ СЕРВЕРА: {addr} ---\n")
    
    for user, password in users:
        # В Hysteria 2 SNI обычно совпадает с адресом сервера
        uri = f"hysteria2://{user}:{password}@{addr}:{port}/?sni={addr}"
        
        if obfs_type:
            uri += f"&obfs={obfs_type}&obfs-password={obfs_pass}"
        
        # Проверяем, активен ли блок ACME (не закомментирован)
        with open(config_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            acme_active = any(line.strip().startswith('acme:') for line in lines)
            
        if not acme_active:
            uri += "&insecure=1"
            
        uri += f"#{user}_Hysteria2"
        
        print(f"Пользователь: {user}")
        print(f"URI: {uri}\n")

if __name__ == "__main__":
    generate()
