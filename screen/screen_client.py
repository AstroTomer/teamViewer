import socket
from PIL import ImageGrab
from io import BytesIO
import time

# Target 
VIEWER_IP = '192.168.1.142'
PORT = 10000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("Sending screen via UDP...")

while True:
    # 1. Capture screen
    screen = ImageGrab.grab()
    
    # 2. SHRINK IT (Essential for UDP)
    # Most UDP limits are ~65kb. We resize to 800x600 for safety.
    screen = screen.resize((800, 600))
    
    # 3. Compress to JPEG
    buffer = BytesIO()
    screen.save(buffer, format="JPEG", quality=50) # Lower quality = Higher FPS
    data = buffer.getvalue()
    
    # 4. Check size (UDP Limit)
    if len(data) < 65507:
        sock.sendto(data, (VIEWER_IP, PORT))
    else:
        print("Frame too large for UDP!")
    
    # Small sleep to control FPS (e.g. 30 FPS)
    time.sleep(0.03)