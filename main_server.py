import socket
import keyboard
import pyautogui
import threading
import time
from PIL import ImageGrab
from io import BytesIO

# --- CONFIGURATION ---
# Replace this with the IP of your CONTROLLER computer
CONTROLLER_IP = '192.168.1.142'
KB_PORT = 12345
MOUSE_PORT = 12346
SCREEN_PORT = 10000

# Optimization: Fastest possible interaction
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

# 1. KEYBOARD SERVER (TCP)
def kb_handler():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('0.0.0.0', KB_PORT))
        sock.listen(1)
        print(f"TCP: Keyboard listening on {KB_PORT}...")
        conn, addr = sock.accept()
        buffer = ""
        while True:
            data = conn.recv(1024).decode()
            if not data: break
            buffer += data
            while "\n" in buffer:
                cmd, buffer = buffer.split("\n", 1)
                if cmd.startswith("k:"):
                    keyboard.press_and_release(cmd[2:])
    except Exception as e:
        print(f"KB Error: {e}")

# 2. MOUSE SERVER (UDP)
def mouse_handler():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', MOUSE_PORT))
        print(f"UDP: Mouse listening on {MOUSE_PORT}...")
        while True:
            data, _ = sock.recvfrom(1024)
            msg = data.decode()
            if msg.startswith("m:"):
                coords = msg[2:].split(",")
                pyautogui.moveTo(int(coords[0]), int(coords[1]))
            elif msg.startswith("c:"):
                pyautogui.click(button=msg[2:])
    except Exception as e:
        print(f"Mouse Error: {e}")

# 3. SCREEN SENDER (UDP)
def screen_streamer():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print(f"UDP: Sending Screen to {CONTROLLER_IP}:{SCREEN_PORT}...")
        while True:
            # Capture and Resize (Must fit in UDP packet < 65kb)
            img = ImageGrab.grab().resize((800, 600))
            buf = BytesIO()
            img.save(buf, format="JPEG", quality=30) # Low quality = High speed
            data = buf.getvalue()
            
            if len(data) < 65507:
                sock.sendto(data, (CONTROLLER_IP, SCREEN_PORT))
            
            time.sleep(0.05) # ~20 FPS
    except Exception as e:
        print(f"Screen Error: {e}")

if __name__ == "__main__":
    # Run everything at once
    threading.Thread(target=kb_handler, daemon=True).start()
    threading.Thread(target=mouse_handler, daemon=True).start()
    # Screen streamer stays in main thread
    screen_streamer()