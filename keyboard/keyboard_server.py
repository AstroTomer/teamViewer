import socket
import keyboard

# Setup
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 12345))
server.listen(1)

print("--- REMOTE READY ---")
conn, addr = server.accept()
print(f"Connected to Controller: {addr}")

buffer = ""
try:
    while True:
        data = conn.recv(1024).decode()
        if not data: break
        
        buffer += data
        while "\n" in buffer:
            key, buffer = buffer.split("\n", 1)
            if key:
                # We removed the print(key) to keep the terminal clean
                keyboard.press_and_release(key)
                
                if key == 'esc':
                    print("\nConnection closed by Controller.")
                    exit()
finally:
    conn.close()