import socket
import mouse 
import time

SERVER_IP = '192.168.1.142'
PORT = 12346

# UDP Socket
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("MOUSE UDP CONTROLLER ACTIVE")

def send_udp(msg):
    client.sendto(msg.encode(), (SERVER_IP, PORT))

# Click hooks
mouse.on_click(lambda: send_udp("c:left"))
mouse.on_right_click(lambda: send_udp("c:right"))

last_pos = (0, 0)
while True:
    curr_pos = mouse.get_position()
    if curr_pos != last_pos:
        # Just send the coordinates directly
        send_udp(f"m:{curr_pos[0]},{curr_pos[1]}")
        last_pos = curr_pos
    
    # We can go much faster with UDP! 
    time.sleep(0.005)