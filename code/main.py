import argparse
import base64
import picamera
import json
import time
import RPi.GPIO as GPIO
from sensor_test import * 
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_O = 25 
GPIO_TRIGGER = 23 
GPIO_ECHO = 24
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_O, GPIO.OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

BOOL_BUZZ = 0
def filenames(frames):
    frame = 0
    while frame < frames:
        yield 'Images/image%02d.jpg' % frame
        frame += 1

def callVision(frames):
	for i in range(0,frames):
			im = "Images/image" + '{:02d}'.format(i) + ".jpg" 
			
			credentials = GoogleCredentials.get_application_default()
			service = discovery.build('vision', 'v1', credentials=credentials)
			
			with open(im, 'rb') as image:
				image_content = base64.b64encode(image.read())
				service_request = service.images().annotate(body={
					'requests': [{
						'image': {
							'content': image_content.decode('UTF-8')
						},
						'features': [{
							'type': 'FACE_DETECTION',
							'maxResults': 10 
						}]
					}]
				})
				response = service_request.execute()
				
				print json.dumps(response, indent=4, sort_keys=True)	#Print it out and make it somewhat pretty.
				global BOOL_BUZZ				
				if len(response.values()[0][0])  == 0:
					BOOL_BUZZ = 0
				elif  response["responses"][0]["faceAnnotations"][0]["angerLikelihood"] == "VERY_UNLIKELY":
					BOOL_BUZZ = 1 
				else:
					BOOL_BUZZ = 0
def main():
	
	try:
		while True:
			with picamera.PiCamera() as camera:
				camera.resolution = (1024, 768)
				camera.framerate = 30
				camera.start_preview()
				time.sleep(1)
				start = time.time()
				#im = "Images/image" + '{:02d}'.format(1) + ".jpg" 
				#camera.capture(im)
				camera.capture_sequence(filenames(1), use_video_port=True)
    
			callVision(1)
			finish = time.time()
			if BOOL_BUZZ:
				dist = distance()
			else:
				dist = 201
			print ("Measured Distance = %.1f cm" % dist)
			if (dist < 200):
    				for i in xrange(4):
        				for value in [True, False]:
            					GPIO.output(GPIO_BUZZ, value)
            					time.sleep(BUZZER_DELAY)
    					time.sleep(PAUSE_TIME)
			
			time.sleep(1)
						        # Reset by pressing CTRL + C
	except KeyboardInterrupt:
		print("Measurement stopped by User")
   		GPIO.cleanup()	
	
if __name__ == '__main__':
    main()
