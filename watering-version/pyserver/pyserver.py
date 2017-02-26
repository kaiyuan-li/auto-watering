import RPi.GPIO as GPIO
import socket
from lib_nrf24 import NRF24
import time
import spidev

host = ''
port = 12345

# initialize NRF24
GPIO.setmode(GPIO.BCM)
pipes = [[0xE8,0xE8,0xF0,0xF0,0xE1],[0xF0,0xF0,0xF0,0xF0,0xE1]]
radio = NRF24(GPIO,spidev.SpiDev())
radio.begin(0,17)
radio.setPayloadSize(32)
radio.setChannel(0x78)
radio.setDataRate(NRF24.BR_1MBPS)
radio.setPALevel(NRF24.PA_MAX)
radio.setAutoAck(True)
radio.enableDynamicPayloads()
radio.enableAckPayload()
radio.openWritingPipe(pipes[0])
radio.openReadingPipe(1,pipes[1])
radio.printDetails()

def sendMsg(radio,msg):
	msg = list(msg)
	while(len(msg)<32):
		msg.append(0)
	radio.write(msg)

def setupServer():
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	print("Socket created at port: "+str(port))
	try:
		s.bind((host,port))
	except socket.error as msg:
		print(msg)
	print("Socket bind complete")
	return s

def setupConnection():
	s.listen(1)
	connection,address = s.accept()
	print("connected to "+address[0]+":"+str(address[1]))
	return connection

def CHM(radio):
	msg = "CHM";
	print("checking moisture value")
	sendMsg(radio,msg)
	radio.startListening()
	start = time.time()
	print("sent the message:{}".format(msg))
	while not radio.available(0):
		time.sleep(1/100)
		if time.time()-start>5:
			print("did not get the moisture value within 5s")
			break
	receivedMsg = []
	radio.read(receivedMsg,radio.getDynamicPayloadSize())
	print("received:{}".format(receivedMsg))
	print("translating received msg into unicode ...")
	str = ""
	for n in receivedMsg:
		if(n>=32 and n<=126):
			str+=chr(n)
	radio.stopListening()
	return str

def WATER(radio):
	msg = "WATER";
	sendMsg(radio,msg)
	radio.startListening()
	start = time.time()
	print("sent the message:{}".format(msg))
	while not radio.available(0):
		time.sleep(1/100)
		if time.time()-start>25:
			print("did not get the moisture value within 10s")
			break
	receivedMsg = []
	radio.read(receivedMsg,radio.getDynamicPayloadSize())
	print("received:{}".format(receivedMsg))
	print("translating received msg into unicode ...")
	str = ""
	for n in receivedMsg:
		if(n>=32 and n<=126):
			str+=chr(n)
	radio.stopListening()
	return str

def handleRequest(connection):
	while True:
		data = connection.recv(1024)
		data = data.decode('utf-8')
		command = data
		print(data)

		if command == 'CHM':
			reply = CHM(radio)
		elif command == 'WATER':
			reply = WATER(radio)
		elif command == 'EXIT':
			print("client left")
		elif command == 'KILL':
			print("server is shutting down")
			s.close()
			break
		else:
			reply = 'unknown command: please specify either CHM(check moisture) or WATER'
		connection.sendall(str.encode(reply))
		print("data has been sent!")
	conn.close()


s = setupServer()

while True:
	try:
		connection = setupConnection()
		handleRequest(connection)
	except:
		break
