import socket
import tkinter

from PIL import ImageGrab, Image, ImageTk
from io import BytesIO

class App():
    def __init__(self):
        self.root = tkinter.Tk()
        self.label = tkinter.Label(self.root)
        self.label.pack()
        self.init_connection()
        self.update_image()
        self.root.mainloop()

    def init_connection(self):
        # create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # bind the socket to a local address
        server_address = ('0.0.0.0', 10000)
        print('starting up on {} port {}'.format(*server_address))
        sock.bind(server_address)

        # listen for incoming connections
        sock.listen(1)

        # accept a connection
        print('waiting for a connection')
        connection, client_address = sock.accept()
        self.connection = connection

    def update_image(self):
        # receive the size of the screenshot
        size_bytes = self.connection.recv(4)    
        size = int.from_bytes(size_bytes, byteorder='big')    

        # receive the screenshot
        image_bytes = self.connection.recv(size)
            
        try:
            # display the screenshot
            image = Image.open(BytesIO(image_bytes))

            photo_image=ImageTk.PhotoImage(image)

            self.label.config(image=photo_image)
            self.label.image = photo_image
            self.label.pack()
        except:            
            pass

        self.root.after(10, self.update_image)

app=App()