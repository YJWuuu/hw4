import paho.mqtt.client as paho
import matplotlib.pyplot as plt
import numpy as np
import serial
import time

# XBee setting
serdev = '/dev/ttyUSB0'
s = serial.Serial(serdev, 9600)

s.write("+++".encode())
char = s.read(2)
print("Enter AT mode.")
print(char.decode())

s.write("ATMY 0x150\r\n".encode())
char = s.read(3)
print("Set MY 0x150.")
print(char.decode())

s.write("ATDL 0x250\r\n".encode())
char = s.read(3)
print("Set DL 0x250.")
print(char.decode())

s.write("ATID 0x1\r\n".encode())
char = s.read(3)
print("Set PAN ID 0x1.")
print(char.decode())

s.write("ATWR\r\n".encode())
char = s.read(3)
print("Write config.")
print(char.decode())

s.write("ATMY\r\n".encode())
char = s.read(4)
print("MY :")
print(char.decode())

s.write("ATDL\r\n".encode())
char = s.read(4)
print("DL : ")
print(char.decode())

s.write("ATCN\r\n".encode())
char = s.read(3)
print("Exit AT mode.")
print(char.decode())

print("start sending RPC")

Fs = 20.0;  # sampling rate
Ts = 20.0/Fs; # sampling interval
t0 = np.arange(0,20,Ts) # time vector; create Fs samples between 0 and 1.0 sec.
num = np.arange(0,20,Ts) # signal vector; create Fs samples
x = np.arange(0,20,Ts/2) # signal vector; create Fs samples
y = np.arange(0,20,Ts/2)
z = np.arange(0,20,Ts/2)
t1 = np.arange(0,20,Ts/2)
tilt = np.arange(0,20,Ts/2)

s.write("/getNum/run\r".encode())
for i in range(7):
    s.readline()
time.sleep(1)
print("start")

for i in range(0, int(Fs)):
    s.write("/getNum/run\r".encode())
    line = s.readline() # Read an echo string from K66F terminated with '\n'
    print(line)
    num[i] = float(line)
    line = s.readline() # Read an echo string from K66F terminated with '\n'
    x[2 * i] = float(line)
    line = s.readline()
    y[2 * i] = float(line)
    line = s.readline()
    z[2 * i] = float(line)
    if (abs(x[2 * i]) >= 0.2 or abs(y[2 * i]) >= 0.2):
        tilt[2 * i] = 1
    else:
        tilt[2 * i] = 0
    line = s.readline() # Read an echo string from K66F terminated with '\n'
    x[2 * i + 1] = float(line)
    line = s.readline()
    y[2 * i + 1] = float(line)
    line = s.readline()
    z[2 * i + 1] = float(line)
    if (abs(x[2 * i + 1]) >= 0.2 or abs(y[2 * i + 1]) >= 0.2):
        tilt[2 * i + 1] = 1
    else:
        tilt[2 * i + 1] = 0
    time.sleep(1)


mqttc = paho.Client()

# Settings for connection
host = "localhost"
topic= "Mbed"
port = 1883

# Callbacks
def on_connect(self, mosq, obj, rc):
    print("Connected rc: " + str(rc))

def on_message(mosq, obj, msg):
    print("[Received] Topic: " + msg.topic + ", Message: " + str(msg.payload) + "\n");

def on_subscribe(mosq, obj, mid, granted_qos):
    print("Subscribed OK")

def on_unsubscribe(mosq, obj, mid, granted_qos):
    print("Unsubscribed OK")

# Set callbacks
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_subscribe = on_subscribe
mqttc.on_unsubscribe = on_unsubscribe

# Connect and subscribe
print("Connecting to " + host + "/" + topic)
mqttc.connect(host, port=1883, keepalive=60)
mqttc.subscribe(topic, 0)


for i in range(0, int(Fs) * 2):
    mesg = tilt[i]
    mqttc.publish(topic, mesg)
    print(mesg)
    time.sleep(0.5)


plt.plot(t0, num, color="blue")
plt.xlim(0, 20)
plt.xlabel('Time')
plt.ylabel('numAcc')
plt.show()
s.close()



"""
while True:
    # send RPC to remote

    # s.write("\r".encode())
    # line=s.readline() # Read an echo string from K66F terminated with '\n' (pc.putc())
    # print(line)
    # line=s.readline() # Read an echo string from K66F terminated with '\n' (RPC reply)
    # print(line)
    # time.sleep(1)
    # time.sleep(1)

    s.write("/getNum/run\r".encode())
    line=s.readline() # Read an echo string from K66F terminated with '\n' (pc.putc())
    print(line)
    time.sleep(1)

    # s.write("/getAcc/run\r".encode())
    # line=s.readline() # Read an echo string from K66F terminated with '\n' (pc.putc())
    # print(line)
    # line=s.readline() # Read an echo string from K66F terminated with '\n' (RPC reply)
    # print(line)
    # time.sleep(1)

    # s.write("/getAddr/run\r".encode())
    # line=s.readline() # Read an echo string from K66F terminated with '\n' (pc.putc())
    # print(line)
    # line=s.readline() # Read an echo string from K66F terminated with '\n' (RPC reply)
    # print(line)    
    # time.sleep(1)

s.close()
"""