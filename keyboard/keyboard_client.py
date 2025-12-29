import socket
import keyboard

SERVER_IP = '192.168.1.142' 
PORT = 12345

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client_socket.connect((SERVER_IP, PORT))
    print("connected")
    
    while True:
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN:
            if event.name == 'esc': 
                client_socket.sendall("esc\n".encode())
                break
            client_socket.sendall((event.name + "\n").encode())
            
except Exception as e:
    print(f"error: {e}")
finally:
    client_socket.close()