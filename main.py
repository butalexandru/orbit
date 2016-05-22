#!/usr/bin/env python

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

import bluetooth
import struct
import time
from sphero_driver import sphero_driver
import sys

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

connected = False
sphero = sphero_driver.Sphero()

while not connected:
	try:
		sphero.connect()
		sphero.set_raw_data_strm(40, 1 , 0, False)
		connected = True
	except:
		connected = False
	

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		sphero.set_rgb_led(255,0,0,0,False)
		self.write("Hello, world")

class ColorHandler(tornado.web.RequestHandler):
	def post(self,r,g,b):
		sphero.set_rgb_led(int(r),int(g),int(b),0,False)
		self.write("Hello, world")

class CircularOrbit(tornado.web.RequestHandler):
	def get(self):
		angle = 0
		speed = 110 #between 50 and 150
		radius = 10 #range should be from 3 to 15
		angle_increment = int(100/radius) #this parameter is inverse proportional with radius
		refresh_time_s = 0.2

		time.sleep(2)
		sphero.set_rgb_led(255,0,0,0,False)
		sphero.set_back_led(255, False)
		time.sleep(3);

		timeout = time.time() + 30   # 30 sec
		while True:
			if time.time() > timeout:
				break
			sphero.roll(speed, angle, 1, False)
			angle = (angle + angle_increment)%360
			print 'angle', angle
			time.sleep(refresh_time_s)

class ElipticalOrbit(tornado.web.RequestHandler):
	def get(self):
		angle = 0
		speed = 50 #between 50 and 150
		radius = 5 #range should be from 3 to 15
		angle_increment = int(100/radius) #this parameter is inverse proportional with radius
		refresh_time_s = 0.16
		excentricity = 0.8
		instant_angle_increment = angle_increment
		speed_acceleration_margin = 0.8
		speed_acceleration = 0.1; #percentage of speed that will be topped with

		time.sleep(2)
		sphero.set_rgb_led(255,0,0,0,False)
		sphero.set_back_led(255, False)
		time.sleep(3);
		timeout = time.time() + 30   # 30 sec
		while True:
			if time.time() > timeout:
				break
			print "speed", int(speed+speed*speed_acceleration), "ang", angle, speed_acceleration
			sphero.roll(int(speed+speed*speed_acceleration), angle, 1, False)
			instant_angle_increment = angle_increment-((abs((angle%180)-90))*(angle_increment*excentricity)/90)
			speed_acceleration = abs(angle-180)/180.0*speed_acceleration_margin;
			angle = int((angle + instant_angle_increment)%360)
			time.sleep(refresh_time_s)

class CustomEliptical(tornado.web.RequestHandler):
	def post(self):
		angle = 0
		speed = int(self.get_argument("speed", 50)) #between 50 and 150
		radius = int(self.get_argument("radius", 4)) #range should be from 3 to 15
		excentricity = float(self.get_argument("excentricity", 0.8))
		loop = int(self.get_argument("loop", 30))
		rrate= int(self.get_argument("rrate", 127))
		angle_increment = int(100/radius) #this parameter is inverse proportional with radius
		refresh_time_s = 0.16
		instant_angle_increment = angle_increment
		speed_acceleration_margin = 0.8
		speed_acceleration = 0.1; #percentage of speed that will be topped with

		time.sleep(2)
		sphero.set_rgb_led(255,0,0,0,False)
		sphero.set_back_led(255, False)
		time.sleep(3);
		timeout = time.time() + loop   # 30 sec
		sphero.set_rotation_rate(rrate, False)
		while True:
			if time.time() > timeout:
				break
			print "speed", int(speed+speed*speed_acceleration), "ang", angle, speed_acceleration
			sphero.roll(int(speed+speed*speed_acceleration), angle, 1, False)
			instant_angle_increment = angle_increment-((abs((angle%180)-90))*(angle_increment*excentricity)/90)
			speed_acceleration = abs(angle-180)/180.0*speed_acceleration_margin;
			angle = int((angle + instant_angle_increment)%360)
			time.sleep(refresh_time_s)


def main():
	tornado.options.parse_command_line()
	application = tornado.web.Application([
		(r"/circularorbit/", CircularOrbit),
		(r"/elipticalorbit/", ElipticalOrbit),
		(r"/customelipticalorbit/", CustomEliptical),
		(r"/color/([0-9]+)/([0-9]+)/([0-9]+)/", ColorHandler),
		(r"/", MainHandler),
	])
	http_server = tornado.httpserver.HTTPServer(application)
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
	main()
