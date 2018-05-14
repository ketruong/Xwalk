import time
import picamera

with picamera.PiCamera() as camera:
    camera.resolution = (1024, 768)
    camera.framerate = 30
    camera.start_preview()
    time.sleep(2)
    camera.capture_sequence([
        'Images/image1.jpg',
        'Images/image2.jpg',
        'Images/image3.jpg',
        'Images/image4.jpg',
        'Images/image5.jpg',
        ])
