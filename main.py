from deepface import DeepFace
import json
import cv2
import tkinter as tk
from tkinter import Button, Label
from PIL import Image, ImageTk
import os

class WebcamApp:
    def __init__(self, window, window_title="Face Control"):
        self.window = window
        self.window.title(window_title)
        self.video_source = 0
        self.vid = cv2.VideoCapture(self.video_source)
        self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        self.canvas = tk.Canvas(window, width=self.vid.get(cv2.CAP_PROP_FRAME_WIDTH), height=self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.canvas.pack()
        self.info_label = Label(window, text="Коли ваше лице буде обведено синім квадратом, натисніть кнопку, щоб пройти контроль", font=("Helvetica", 12))
        self.info_label.pack(pady=10)
        self.btn_capture = Button(window, text="Пройти перевірку", width=20, command=self.capture)
        self.btn_capture.pack(padx=20, pady=10)
        self.result_label = Label(window, text="", font=("Helvetica", 16))
        self.result_label.pack(pady=10)
        self.close_button = Button(window, text="Закрити програму", width=20, command=window.destroy)
        self.retry_button = Button(window, text="Повторити спробу", width=20, command=self.retry_capture)
        self.update()
        self.window.mainloop()

    def capture(self):
        ret, frame = self.vid.read()
        faces = self.face_cascade.detectMultiScale(frame, scaleFactor=1.5, minNeighbors=5, minSize=(20, 20))
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        color_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if ret:
            cv2.imwrite("new.jpg", color_frame)
            print("Перевірка доступу...")
            recognized, result = self.face_verification()
            self.result_label.config(text=result)
            if recognized:
                self.show_close_button()
            else:
                self.show_retry_button()

    def retry_capture(self):
        self.result_label.config(text="")
        self.retry_button.pack_forget()
        self.close_button.pack_forget()
        self.btn_capture.config(state=tk.NORMAL)

    def show_close_button(self):
        self.close_button.pack(pady=10)
        self.btn_capture.config(state=tk.DISABLED)

    def show_retry_button(self):
        self.retry_button.pack(pady=10)
        self.close_button.pack(pady=10)
        self.btn_capture.config(state=tk.DISABLED)

    def face_verification(self):
        new_image_path = 'new.jpg'
        legit_directory = 'Other'

        for filename in os.listdir(legit_directory):
            if filename.endswith(".jpg"):
                legit_image_path = os.path.join(legit_directory, filename)
                result_dict = DeepFace.verify(img1_path=legit_image_path, img2_path=new_image_path)
                result_dict["verified"] = bool(result_dict["verified"])
                with open('result.json', 'w') as file:
                    json.dump(result_dict, file, indent=4, ensure_ascii=False)

                if result_dict.get('verified'):
                    return True, 'Контроль пройдено, ласкаво просимо!'
                return False, 'Об\'єкт не розпізнано, доступ закритий'
        return False, 'Об\'єкт не розпізнано, доступ закритий.'

    def update(self):
        ret, frame = self.vid.read()
        faces = self.face_cascade.detectMultiScale(frame, scaleFactor=1.5, minNeighbors=5, minSize=(20, 20))
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        if ret:
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.window.after(10, self.update)

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

root = tk.Tk()
app = WebcamApp(root, window_title="Face Control by 'PVV'")
root.mainloop()
