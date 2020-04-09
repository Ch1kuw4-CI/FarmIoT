#!/usr/bin/ python
# -*- coding: utf-8 -*-

import serial
import time
import datetime
import sys

import pprint
import json
import requests
from pytz import timezone


# serial settings
global portName
portName		= "/dev/ttyUSB_SOIL"
global waitTime
waitTime		= 0.5
global scanTime
scanTime		= 14

global addressList
addressList		= []						# Searched address list.
global typeList
typeList		= []						# Searched type list.
global data

def now_utc_str():
	return datetime.datetime.now(timezone('UTC')).strftime("%Y-%m-%d %H:%M:%S")


def product_to_number(product):
	if product == "5WT":
		return 2
	elif product == "5WET":
		return 3
	elif product == "5WTA":
		return 5
	else:
		return 0


def scan_device():
	address=0
	while address<10:
		try:
			sdi.reset_input_buffer()
			sdi.reset_output_buffer()
			#Break Send
			sdi.sendBreak(0.02)
			time.sleep(0.02)
			request = str(address) + "I!"
			sdi.write( request.encode() )
			time.sleep(waitTime)
			#Write Check
			response = sdi.readline()
			#Parse
			length = len(response)
			if length == 34:
				sdi_ver = response[5:7].decode('Shift_JIS')
				company = response[7:15].decode('Shift_JIS').strip()
				product = response[15:21].decode('Shift_JIS').strip()
				version = response[21:24].decode('Shift_JIS')
				option  = response[24:length-2].decode('Shift_JIS').strip()
				if response[4:5].decode('Shift_JIS') != str(address):
					address = address + 1
					continue
				if sdi_ver != "13":
					address = address + 1
					continue
				addressList.append(address)
				typeList.append(product_to_number(product))
				now = now_utc_str()
			address = address + 1
		except KeyboardInterrupt:
			print("Measurement has been cancelled.")
			break


def measure(address,type):
	sdi.reset_input_buffer()
	sdi.reset_output_buffer()
	#Break Send
	sdi.sendBreak(0.02)
	time.sleep(0.02)
	request = str(address) + "M!"
	sdi.write( request.encode() )
	time.sleep(waitTime)
	#Write Check
	response = sdi.readline()
	response = response.rstrip()			# 謾ｹ陦梧枚蟄怜炎髯､
	# <BR>0M!00013<CR><LF>
	resAddress = response[4:5].decode('Shift_JIS')
	resInterval = response[5:8].decode('Shift_JIS')
	resItemCount = response[8:9].decode('Shift_JIS')
	if 	str(address) != resAddress:
		print("Request failed:Address error.")
		return
	if 	str(type) != resItemCount:
		print("Request failed:Item Count is different.")
		return
	time.sleep(int(resInterval))
	dummyRead = sdi.readline()
	sdi.reset_input_buffer()
	sdi.reset_output_buffer()

	#Break Send
	sdi.sendBreak(0.02)
	time.sleep(0.02)
	request = str(address) + "D0!"
	sdi.write(request.encode())
	time.sleep(waitTime)
	global measure
	measured = sdi.readline()
	d = datetime.datetime.now()
	dt = d.strftime('%Y/%m/%d %H:%M:%S')
	# <BR>0D0!0
	if measured[1:6].decode('Shift_JIS') == str(address) + "D0!"+ str(address):
		measured = measured.rstrip().decode('Shift_JIS')			# 謾ｹ陦梧枚蟄怜炎髯､
		replaced = measured.replace('+',',')
		replaced = replaced.replace('-',',-')
		global data
		data = replaced.split(',')
		global now
		now = now_utc_str()

	else:
		print("Response invalid")
		d = datetime.datetime.now()
		dt = d.strftime('%Y/%m/%d %H:%M:%S')
		print(dt)

#Main Loop
def main_c():
	global sdi
	global port
	global baudrate
	global bytesize
	global parity
	global stopbits
	global timeout
	global write_timeout
	try:
		sdi = serial.Serial(
			port = portName,
			baudrate = 1200,
			bytesize = serial.SEVENBITS,
			parity = serial.PARITY_EVEN,
			stopbits = serial.STOPBITS_ONE,
			timeout = 0,
			write_timeout = 0)

		sdi.reset_input_buffer()
		sdi.reset_output_buffer()

		addressList.clear()
		typeList.clear()

		period = 1

		#Power On
		sdi.setRTS(True)
		time.sleep(0.05)
		scan_device()
		for i in range(len(addressList)):
			measure(addressList[i],typeList[i])
		sdi.close()
		#Power Off
		sdi.setRTS(False)
		#Wait for sampling period
		deviceCount = len(addressList)
		if len(data) == 3:
			return data[1],data[2]
		elif len(data) == 4:		#水分含有量,EC,温度
			return data[1], data[2], data[3]
		elif len(data) == 6:
			return data[1], data[2], data[3], data[4], data[5]


	except:
		print("Serial Port " + portName + " Not Exist!")

#main_c()
