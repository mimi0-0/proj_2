from socket import socket, AF_INET, SOCK_DGRAM

HOST = '127.0.0.1'
PORT = 9000# server側で設定した番号と同じ

client = socket(AF_INET, SOCK_DGRAM)
client.sendto(b'Hello UDP', (HOST, PORT))
client.close()