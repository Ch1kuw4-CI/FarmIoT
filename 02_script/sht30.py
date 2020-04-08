#!/usr/bin/env python
#coding: utf-8

import time
import smbus

def tempChanger(msb, lsb):
    global mlsb
    mlsb = ((msb << 8) | lsb)                                             # P1
    return (-45 + 175 * int(str(mlsb), 10) / (pow(2, 16) - 1))            # P2

def humidChanger(msb, lsb):
    global mlsb
    mlsb = ((msb << 8) | lsb)
    return (100 * int(str(mlsb), 10) / (pow(2, 16) - 1))


global i2c
i2c = smbus.SMBus(1)
global i2c_addr
i2c_addr = 0x44                                                           # P3
i2c.write_byte_data(i2c_addr, 0x21, 0x30)                                 # P4
time.sleep(0.5)

def main_d():
    i2c.write_byte_data(i2c_addr, 0xE0, 0x00)                             # P5
    global data
    data = i2c.read_i2c_block_data(i2c_addr, 0x00, 6)                     # P6
    return str('{:.4g}'.format(tempChanger(data[0], data[1]))), str('{:.4g}'.format(humidChanger(data[3], data[4])))



