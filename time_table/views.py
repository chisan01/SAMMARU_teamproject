from django.shortcuts import render, redirect
import os

# 웹캠 관련 라이브러리
from django.views.decorators import gzip
from django.http import StreamingHttpResponse
import cv2
import threading
import face_recognition
import numpy as np


class VideoCamera(object):
    def __init__(self):
        self.known_face_encodings = [np.load(f"/encodings/{path}") for path in os.listdir("/encodings")]
        self.known_face_names = [os.path.splitext(path)[0] for path in os.listdir("/encodings")]
        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.video = cv2.VideoCapture(0)
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        (self.grabbed, self.frame) = self.video.read()
        threading.Thread(target=self.update, args=()).start()

    def __del__(self):
        self.video.release()

    def get_frame(self):
        image = self.frame
        small_frame = cv2.resize(self.frame, (0, 0), fx=0.50, fy=0.50)
        rgb_small_frame = small_frame[:, :, ::-1]
        self.face_locations = face_recognition.face_locations(rgb_small_frame)
        self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)
        if len(self.face_locations):
            self.face_names = []
            for face_encoding, i in zip(self.face_encodings, range(len(self.face_encodings))):
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                if True in matches:
                    print(-1)
                    self.face_names.append(self.known_face_names[matches.index(True)])
                else:
                    self.face_names.append("Unknown");
        for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 2
            right *= 2
            bottom *= 2
            left *= 2
            # Draw a box around the face
            cv2.rectangle(self.frame, (left, top), (right, bottom), (146, 101, 57), 15)
            # Draw a label with a name below the face
            cv2.rectangle(self.frame, (left, bottom-50), (right, bottom), (146, 101, 57), cv2.FILLED)
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(self.frame, name, (left + 6, bottom - 5), font, 2, (255, 255, 255), 1)
        _, jpeg = cv2.imencode('.jpg', self.frame)
        return jpeg.tobytes()

    def update(self):
        while True:
            (self.grabbed, self.frame) = self.video.read()


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield(b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@gzip.gzip_page
def detectme(request):
    try:
        cam = VideoCamera()
        return StreamingHttpResponse(gen(cam), content_type="multipart/x-mixed-replace;boundary=frame")
    except:
        print("에러입니다")
        pass


def setting(request):
    if request.user.id is None:
        return redirect('login')
    return render(request, 'setting.html')
    # return redirect('time_table:setting')


def add_face(request):
    if request.method == "POST":
        cam = VideoCamera()
        cam.get_frame()
        if cam.face_names:
            if cam.face_names[0] == 'Unknown':
                print('등록되지 않은 얼굴입니다')
                encoding = np.array(cam.face_encodings[0])
                np.save(f"/encodings/{request.user.id}", encoding)
                print('얼굴 등록완료')
                return redirect('time_table:setting')
        else:
            return redirect('time_table:setting')
    else:
        return redirect('time_table:setting')