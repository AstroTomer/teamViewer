import socket
import tkinter
import threading
from PIL import Image, ImageTk
from io import BytesIO
import mouse as mouse_lib # renamed to avoid conflict
import keyboard

class MainController:
    def __init__(self, target_ip):
        self.target_ip = target_ip
        
        # 1. Setup GUI
        self.root = tkinter.Tk()
        self.root.title(f"Controlling: {target_ip}")
        self.label = tkinter.Label(self.root)
        self.label.pack()

        # 2. Setup Sockets
        # Keyboard (TCP)
        self.kb_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Mouse (UDP)
        self.mouse_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Screen (UDP - Receiver)
        self.screen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.screen_sock.bind(('0.0.0.0', 10000))
        self.screen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1000000)

        # 3. Connect
        try:
            self.kb_sock.connect((self.target_ip, 12345))
            print("Connected to Keyboard Server")
        except:
            print("Keyboard Server not found!")

        # 4. Start Listeners
        self.setup_hooks()
        threading.Thread(target=self.receive_screen, daemon=True).start()
        
        self.root.mainloop()

    def setup_hooks(self):
        # Keyboard Hook
        def on_key(event):
            if event.event_type == keyboard.KEY_DOWN:
                try:
                    self.kb_sock.sendall(f"k:{event.name}\n".encode())
                except: pass
        keyboard.hook(on_key)

        # Mouse Click Hooks
        mouse_lib.on_click(lambda: self.send_mouse("c:left"))
        mouse_lib.on_right_click(lambda: self.send_mouse("c:right"))

        # Mouse Movement (Throttle logic)
        threading.Thread(target=self.track_mouse, daemon=True).start()

    def send_mouse(self, msg):
        self.mouse_sock.sendto(msg.encode(), (self.target_ip, 12346))

    def track_mouse(self):
        last_pos = (0, 0)
        while True:
            curr_pos = mouse_lib.get_position()
            if curr_pos != last_pos:
                self.send_mouse(f"m:{curr_pos[0]},{curr_pos[1]}")
                last_pos = curr_pos
            threading.Event().wait(0.01) # 100Hz updates

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
    TARGET_IP = '192.168.1.176' # Change this to the target's IP
    MainController(TARGET_IP)