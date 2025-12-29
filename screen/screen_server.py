import socket
import tkinter
from PIL import Image, ImageTk
from io import BytesIO

class App():
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title("UDP Screen Viewer")
        self.label = tkinter.Label(self.root)
        self.label.pack()
        
        # Setup UDP Socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', 10000))
        # Increase buffer size for large image packets
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1000000)
        
        self.update_image()
        self.root.mainloop()

    def update_image(self):
        try:
            # UDP just receives whatever comes in
            # 65507 is the max size for a UDP packet
            image_bytes, addr = self.sock.recvfrom(65507)
            
            # Load and display
            image = Image.open(BytesIO(image_bytes))
            photo_image = ImageTk.PhotoImage(image)

            self.label.config(image=photo_image)
            self.label.image = photo_image
        except Exception as e:
            # If a packet is lost or corrupted, we just skip it!
            pass

        # Check for a new frame very quickly
        self.root.after(1, self.update_image)

app = App()