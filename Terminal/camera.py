from picamera2 import Picamera2


class Camera:
    def __init__(self, resolution=(640, 480), format="RGB888"):
        self.picam2 = Picamera2()
        self.configuration = self.picam2.create_preview_configuration(main={"format": format, "size": resolution})
        self.picam2.configure(self.configuration)

    def start(self):
        self.picam2.start()

    def stop(self):
        self.picam2.stop()

    def capture_frame(self):
        return self.picam2.capture_array()