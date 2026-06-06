# CameraBuffer class untuk merekam video dari RTSP stream
import cv2
import threading
import time
import os
from collections import deque
from datetime import datetime

class CameraBuffer:
    def __init__(self, rtsp_url, buffer_seconds=10, fps=25, width=1280, height=720):
        self.rtsp_url = rtsp_url
        self.buffer_seconds = buffer_seconds
        self.fps = fps
        self.width = width
        self.height = height
        self.frame_buffer = deque(maxlen=buffer_seconds * fps)
        self.recording_sessions = {}  # session_id: (writer, output_path)
        self.lock = threading.Lock()
        self.running = False
        self.cap = None
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()

    def _capture_loop(self):
        while self.running:
            try:
                if self.cap is None or not self.cap.isOpened():
                    self.cap = cv2.VideoCapture(self.rtsp_url)
                    if not self.cap.isOpened():
                        time.sleep(2)
                        continue
                ret, frame = self.cap.read()
                if not ret:
                    self.cap.release()
                    self.cap = None
                    time.sleep(1)
                    continue
                with self.lock:
                    self.frame_buffer.append(frame)
                    for session_id, (writer, _) in list(self.recording_sessions.items()):
                        try:
                            writer.write(frame)
                        except Exception:
                            pass
            except Exception:
                time.sleep(1)

    def is_connected(self):
        return self.cap is not None and self.cap.isOpened()

    def start_recording(self, session_id, output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        writer = cv2.VideoWriter(output_path, fourcc, self.fps, (self.width, self.height))
        if not writer.isOpened():
            return False
        with self.lock:
            for frame in list(self.frame_buffer):
                writer.write(frame)
            self.recording_sessions[session_id] = (writer, output_path)
        return True

    def stop_recording(self, session_id):
        with self.lock:
            entry = self.recording_sessions.pop(session_id, None)
        if entry:
            writer, output_path = entry
            writer.release()
            return output_path
        return None

    def stop_all(self):
        with self.lock:
            for session_id, (writer, _) in self.recording_sessions.items():
                writer.release()
            self.recording_sessions.clear()

    def active_sessions(self):
        with self.lock:
            return list(self.recording_sessions.keys())

    def get_current_frame(self):
        """Return latest frame from buffer, or None if buffer empty"""
        with self.lock:
            if len(self.frame_buffer) > 0:
                return self.frame_buffer[-1].copy()
            return None
