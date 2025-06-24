from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
import cv2
import os
import time
from datetime import datetime

# Configuration des dossiers
output_dirs = {
    "Corps_Haut": "CH",
    "Corps_Latéral1": "CL1",
    "Corps_Latéral2": "CL2",
    "Corps_Latéral3": "CL3"
}
for path in output_dirs.values():
    os.makedirs(path, exist_ok=True)

delays = {
    "Corps_Haut": 1,
    "Corps_Latéral1": 2,
    "Corps_Latéral2": 2,
    "Corps_Latéral3": 2
}

class CaptureLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        self.image_widget = Image(size_hint=(1, 0.8))
        self.add_widget(self.image_widget)

        self.capture_button = Button(text="📸 Démarrer la capture", size_hint=(1, 0.2))
        self.capture_button.bind(on_press=self.capture_sequence)
        self.add_widget(self.capture_button)

    def clear_directory(self, directory):
        for f in os.listdir(directory):
            try:
                os.remove(os.path.join(directory, f))
            except:
                pass

    def rotate_image(self, frame, angle):
        if angle == 180:
            return cv2.rotate(frame, cv2.ROTATE_180)
        return frame

    def update_image_view(self, frame):
        buf = cv2.flip(frame, 0).tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.image_widget.texture = texture

    def capture_sequence(self, instance):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Impossible d'ouvrir la caméra.")
            return

        sequence = [
            ("Corps_Haut", False),
            ("Corps_Latéral1", True),
            ("Corps_Latéral2", True),
            ("Corps_Latéral3", True)
        ]

        for view_name, rotate in sequence:
            print(f"⏳ Capture : {view_name}")
            time.sleep(delays[view_name])
            ret, frame = cap.read()
            if not ret:
                print(f"❌ Erreur de capture : {view_name}")
                continue

            if rotate:
                frame = self.rotate_image(frame, 180)

            self.update_image_view(frame)  # Affiche dans l'appli

            output_dir = output_dirs[view_name]
            self.clear_directory(output_dir)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(output_dir, f"{view_name}_{timestamp}.jpg")
            cv2.imwrite(filename, frame)
            print(f"✅ Sauvegardée : {filename}")

        cap.release()
        print("✅ Séquence terminée.")

class CameraApp(App):
    def build(self):
        return CaptureLayout()

if __name__ == "__main__":
    CameraApp().run()

