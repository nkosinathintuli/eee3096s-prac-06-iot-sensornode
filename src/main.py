#!/usr/bin/env python

import socket
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

import threading
import time
import datetime
import RPi.GPIO as GPIO

TCP_IP = ''
P2_IP = '192.168.137.6'
TCP_PORT = 5005
BUFFER_SIZE = 1024
MESSAGE = "Hello, World!"

# toggle button
toggle_btn = 23 # mode set to BCM
# sampling rates
samp_rates = [1, 5, 10]
# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
# create the cs (chip select)
cs = digitalio.DigitalInOut(board.D5)
# create the mcp object
mcp = MCP.MCP3008(spi, cs)
# create an analog input channel on pin 1,2 (CH1,CH2)
chan1 = AnalogIn(mcp, MCP.P1) # Termistor
chan2 = AnalogIn(mcp, MCP.P2) # LDR

# readings variables
temp_ADC = -1
temp_v_out = -1
LDR_ADC = -1

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
def to_temp(voltage):
  # Vout = Tc*Ta + V0c (SENSOR TRANSFER FUNCTION)
  # Sensor: MCP9700
  v_0c = 0.5 # Sensor Output Voltage at 0 degree C
  t_c = 0.01 # Temperature Coefficient
  t_a = (voltage-v_0c)/t_c # ambient temperature
  return t_a
  
# read from sensors
def read_sensors():
  global temp_ADC
  global temp_v_out
  global LDR_ADC
  temp_ADC = chan1.value
  temp_v_out = chan1.voltage
  LDR_ADC = chan2.value
  pass

# print sensor readings
def print_readings():
  global runtime
  global start
  thread = threading.Timer(samp_rates[pos], print_readings)
  thread.daemon = True  # Daemon threads exit when the program does
  thread.start()
  read_sensors()
  runtime=+(time.time()-start)
  print(f"{str(int(runtime))+'s':<7s}   {temp_ADC:<12.0f}   {to_temp(temp_v_out):<.2f} C   {LDR_ADC:<13.0f}")

def send_to_server():
	print("Sending...")
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((P2_IP, TCP_PORT))
	s.send(MESSAGE.encode())
	data = s.recv(BUFFER_SIZE)
	s.close()
	print("received data:", data)

if __name__ == "__main__":
  try:
    setup()
    send_to_server()
    #print("Runtime   Temp Reading   Temp      Light Reading")
    #print_readings() # call it once to start the thread
    # Tell our program to run indefinitely

    while True:
      send_to_server()	
      time.sleep(30)
      pass
  except Exception as e:
    print(e)
  finally:
    GPIO.cleanup()
    print("Good Bye!")
