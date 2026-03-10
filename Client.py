import socket
import pyautogui
import io
import struct
import threading
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController , Key
from time import sleep

def ScreenShot_thread(client_socket):
   while True:
      frame_buffer = io.BytesIO()
      screenshot = pyautogui.screenshot()
      screenshot.save(frame_buffer , format="JPEG")
      frame_Data = frame_buffer.getvalue()
      frame_size = len(frame_Data)

      client_socket.sendall(struct.pack(">L",frame_size))
      client_socket.sendall(frame_Data)
      sleep(1/30)

def commands_thread(commands_socket):
    mouse = MouseController()
    keyboard = KeyboardController()
    buffer = ""

    special_keys = {
        "space": Key.space,
        "backspace": Key.backspace,
        "enter": Key.enter,
        "tab": Key.tab,
        "shift": Key.shift,
        "ctrl": Key.ctrl_l,
        "alt": Key.alt_l,
        "delete": Key.delete,
        "esc": Key.esc,
    }
    
    while True:
        try:
            buffer += commands_socket.recv(1024).decode()
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if not line:
                    continue
                parts = line.split(",")
                cmd = parts[0]
                    
                if cmd == "move":
                    try:
                        x, y = int(float(parts[1])), int(float(parts[2]))
                        mouse.position = (x, y)
                    except:
                        pass 
                
                elif cmd == "click":
                    try:
                        x, y = int(float(parts[1])), int(float(parts[2]))
                        mouse.position = (x, y)
                        mouse.click(Button.left)
                    except:
                        pass
                    
                elif cmd == "key":
                    try:
                        keyboard.press(parts[1])
                        keyboard.release(parts[1])
                    except:
                        pass
                    
                elif cmd == "special":
                    try:
                        key = special_keys.get(parts[1])
                        if key:
                            keyboard.press(key)
                            keyboard.release(key)
                    except:
                        pass
        except Exception as e:
            print(f"Command error: {e}")
            break

if __name__ == "__main__":
    screenshot_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    screenshot_socket.connect(("127.0.0.1", 1337))
    commands_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    commands_socket.connect(("127.0.0.1", 1338))

    threading.Thread(target=ScreenShot_thread, args=(screenshot_socket,), daemon=True).start()
    threading.Thread(target=commands_thread, args=(commands_socket,), daemon=True).start()
    
    threading.Event().wait()
