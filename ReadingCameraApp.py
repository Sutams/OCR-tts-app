import cv2
import kivy
import pytesseract
from gtts import tts
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.image import Image
from plyer import tts
from kivy.graphics.texture import Texture
from kivy.lang import builder

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


class KivyCamera(Image):
    def __init__(self, capture, fps, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
        self.capture = capture
        Clock.schedule_interval(self.update, 1.0 / fps)

    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            # identifying text and putting boxes around it
            hImg, wImg, _ = frame.shape
            boxes = pytesseract.image_to_data(frame)
            for z, b in enumerate(boxes.splitlines()):
                if z != 0:
                    b = b.split()
                    if len(b) == 12:
                        x, y, w, h = int(b[6]), int(b[7]), int(b[8]), int(b[9])
                        cv2.rectangle(frame, (x, y), (w + x, h + y), (0, 0, 255), 2)

            # convert it to texture
            buf1 = cv2.flip(frame, 0)
            buf = buf1.tostring()
            image_texture = Texture.create(
                size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            # display image from the texture
            self.texture = image_texture

    def on_touch_down(self, touch):
        ret, img = self.capture.read()
        self.capture.release()
        text = pytesseract.image_to_string(img)
        tts.speak(message=text)


    def on_touch_up(self, touch):
        self.capture = cv2.VideoCapture(0)



class CamApp(App):
    def build(self):
        self.capture = cv2.VideoCapture(0)
        self.my_camera = KivyCamera(capture=self.capture, fps=30)
        return self.my_camera

    def on_stop(self):
        # without this, app will not exit even if the window is closed
        self.capture.release()


if __name__ == '__main__':
    CamApp().run()
    cv2.destroyAllWindows()
