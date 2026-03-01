import socket
import struct
import io
from PIL import Image
import threading
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener , Key
from time import sleep
import numpy as np
import cv2

def ScreenShot_Recieve(client_socket):
   while True:
      raw_size = b""
      while len(raw_size) < 4:
            raw_size += client_socket.recv(4 - len(raw_size))  
      frame_size = struct.unpack(">L", raw_size)[0]

      data = b""
      while len(data) < frame_size:
            chunk = client_socket.recv(min(4096, frame_size - len(data)))
            data += chunk

      frame=Image.open(io.BytesIO(data))
      frame = cv2.cvtColor(np.array(frame),cv2.COLOR_RGB2BGR)
      cv2.imshow("Remote Desktop", frame)
      if cv2.waitKey(1) == 27:
            break
   cv2.destroyAllWindows()
   
def keyboard_thread(client_socket):
      def send_keyboard_click(key):
        try:
            client_socket.send(f"key,{key.char}\n".encode()) 
        except AttributeError:
            special = {
                Key.space: "space",
                Key.backspace: "backspace",
                Key.enter: "enter",
                Key.tab: "tab",
                Key.shift: "shift",
                Key.ctrl_l: "ctrl",
                Key.alt_l: "alt",
                Key.delete: "delete",
                Key.esc: "esc",
            }
            if key in special:
                client_socket.send(f"special,{special[key]}\n".encode())
      with KeyboardListener(on_press=send_keyboard_click) as listener:
            listener.join()

def mouse_thread(client_socket):
      def on_move(x, y):
        client_socket.send(f"move,{x},{y}\n".encode())
    
      def on_click(x, y, button, pressed):
        if pressed:
            client_socket.send(f"click,{x},{y},{button}\n".encode())
    
      with MouseListener(on_move=on_move, on_click=on_click) as listener:
        listener.join()

if __name__ == "__main__":
      screenshot_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      screenshot_server.bind(("10.0.0.22", 1337))
      screenshot_server.listen(1)
      commands_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      commands_server.bind(("10.0.0.22", 1338))
      commands_server.listen(1)
      screenshot_client, _ = screenshot_server.accept()
      commands_client, _ = commands_server.accept()
      threading.Thread(target=ScreenShot_Recieve, args=(screenshot_client,), daemon=True).start()
      threading.Thread(target=keyboard_thread, args=(commands_client,), daemon=True).start()
      threading.Thread(target=mouse_thread, args=(commands_client,), daemon=True).start()
      input("Press Enter to stop...\n")


