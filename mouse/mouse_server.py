import socket
import pyautogui

# Optimization: Removes the 0.1s delay between pyautogui commands
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False # Prevents crash if mouse hits screen corner

# Define connection details
UDP_IP = "0.0.0.0" # Listen on all network interfaces
UDP_PORT = 12346

# Create a UDP socket (SOCK_DGRAM)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"MOUSE SERVER (UDP) STARTED")
print(f"Listening on port {UDP_PORT}...")

while True:
    try:
        # Receive data from the client
        data, addr = sock.recvfrom(1024) 
        message = data.decode().strip()

        # Command Type 1: Movement -> "m:x,y"
        if message.startswith("m:"):
            _, coords = message.split(":")
            x, y = map(int, coords.split(","))
            pyautogui.moveTo(x, y)

        # Command Type 2: Clicks -> "c:left" or "c:right"
        elif message.startswith("c:"):
            _, button = message.split(":")
            pyautogui.click(button=button)
            print(f"Clicked: {button}")

    except Exception as e:
        print(f"Error processing data: {e}")