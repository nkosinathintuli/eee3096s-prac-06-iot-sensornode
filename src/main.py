#!/usr/bin/env python
import threading
import time
from time import sleep
import datetime
import random
TCP_IP = ''
P2_IP = '192.168.137.6'
TCP_PORT = 5005
BUFFER_SIZE = 1024
MESSAGE=''
global data
data=''


# readings variables
global temp_ADC
temp_ADC = 14000
global LDR_ADC
LDR_ADC = 17000

global counter
counter=time.time()
e=datetime.datetime.now()
global tim
tim = e.strftime("%H:%M:%S")
# op vars
runtime = 0
pos = 0
start = time.time()

# Setup pins
def setup():
  # Setup board mode
  # GPIO.setmode(GPIO.BOARD) # already set as BCM probably by the adafruit lib
  GPIO.setup(toggle_btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
  # Setup debouncing and callbacks
  GPIO.add_event_detect(toggle_btn,GPIO.FALLING,callback=toggle,bouncetime=200)
  pass

# toggle sampling rate
def toggle(channel):
  # cycle thru the list of sampling rates in asc order
  global pos
  pos = (pos+1) if pos<2 else 0
  pass

# temparature conversion

  
# read from sensors
def read_sensors():
  global temp_ADC
  global temp_v_out
  global LDR_ADC
  temp_ADC = chan1.value
  temp_v_out = chan1.voltage
  LDR_ADC = chan2.value
  pass


#create a csv file
def create():
    header = ['Date', 'Time', 'Temparature', 'LDR']
    with open('sensorlog.csv', 'w',encoding='UTF8',newline='') as csvfile: 
        writer1 = writer(csvfile) 
        writer1.writerow(header)
        csvfile.close()
#add data to 
def add(row):
    with open('sensorlog.csv', 'a',encoding='UTF8',newline='') as csvfile: 
        writer1 = writer(csvfile) 
        writer1.writerow(row)
        csvfile.close()

def send():
  e = datetime.datetime.now()
  date = e.strftime("%d/%m/%Y")
  tim = e.strftime("%H:%M:%S")
  strin=date+' '+tim+' '+str(temp_ADC)+' '+str(temp_v_out)+' '+str(LDR_ADC)
  counter=time.time()
  add(strin.split(" "))


# print sensor readings
def print_readings():
  global runtime
  global start
  thread = threading.Timer(samp_rates[pos], print_readings)
  thread.daemon = True  # Daemon threads exit when the program does
  thread.start()
  read_sensors()
  send()
  runtime=+(time.time()-start)
  #print(f"{str(int(runtime))+'s':<7s}   {temp_ADC:<12.0f}   {to_temp(temp_v_out):<.2f} C   {LDR_ADC:<13.0f}")



def send_to_server():
  print("Sending Data")
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((P2_IP, TCP_PORT))
  s.send(MESSAGE.encode())
  data = s.recv(BUFFER_SIZE)
  s.close()
  print("received data:", data)



if __name__ == '__main__':
  while 1:
    if(data=='Sensor Off'):
      break
    send_to_server()
    

  
    
