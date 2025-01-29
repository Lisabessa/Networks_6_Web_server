import socket
import os
from datetime import datetime


def get_content(file_path):
    try:
        with open(file_path, 'rb') as f:
            return f.read(), "200 OK"
    except FileNotFoundError:
        return "<h1>404 Not Found</h1>".encode('utf-8'), "404 Not Found"


def handle_request(request, working_dir):
    # Парсинг первой строки запроса
    lines = request.split("\r\n")
    if not lines:
        return b"HTTP/1.1 400 Bad Request\r\n\r\n", "400 Bad Request"

    request_line = lines[0]
    method, path, _ = request_line.split(" ")

    # Обработка только метода GET
    if method != "GET":
        return b"HTTP/1.1 405 Method Not Allowed\r\n\r\n", "405 Method Not Allowed"

    # По умолчанию - index.html
    if path == "/":
        path = "/index.html"

    # Абсолютный путь к файлу
    file_path = os.path.join(working_dir, path.lstrip("/"))
    content, status = get_content(file_path)

    # Добавляем основные заголовки
    headers = [
        f"HTTP/1.1 {status}",
        f"Date: {datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')}",
        "Content-Type: text/html; charset=utf-8",
        "Server: ElizavetaWebServer",
        f"Content-Length: {len(content)}",
        "Connection: close",
        "",
        ""
    ]

    # Формируем ответ
    response = "\r\n".join(headers).encode('utf-8') + content
    return response, status


def run_server(host, port, working_dir):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f"Сервер HTTP на {host} порту {port}...")

        while True:
            conn, addr = server_socket.accept()
            with conn:
                print(f"Подключение с {addr}")
                data = conn.recv(8192)

                if not data:
                    continue

                request = data.decode('utf-8')
                response, status = handle_request(request, working_dir)

                print(f"Статус ответа: {status}")
                conn.sendall(response)


run_server('localhost', 8080, os.path.join(os.getcwd(), "working_dir"))