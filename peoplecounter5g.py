import cv2
import numpy as np
import torch
from ultralytics import YOLO
import time

class Tracker:
    def __init__(self, max_disappeared=30, max_distance=100):
        self.next_id = 0
        self.objects = dict()
        self.bboxes = dict()
        self.disappeared = dict()
        self.seen_ids = set()
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance

    def register(self, centroid, bbox):
        oid = self.next_id
        self.objects[oid] = centroid
        self.bboxes[oid] = bbox
        self.disappeared[oid] = 0
        self.seen_ids.add(oid)
        self.next_id += 1

    def deregister(self, oid):
        self.objects.pop(oid, None)
        self.bboxes.pop(oid, None)
        self.disappeared.pop(oid, None)

    def update(self, rects):
        if len(rects) == 0:
            for oid in list(self.disappeared.keys()):
                self.disappeared[oid] += 1
                if self.disappeared[oid] > self.max_disappeared:
                    self.deregister(oid)
            return self.bboxes.copy()

        input_centroids = np.array([[ (x1+x2)//2, (y1+y2)//2 ] for (x1,y1,x2,y2) in rects])

        if len(self.objects) == 0:
            for i, c in enumerate(input_centroids):
                self.register(c, rects[i])
            return self.bboxes.copy()

        object_ids = list(self.objects.keys())
        object_centroids = np.array([self.objects[i] for i in object_ids])
        D = np.linalg.norm(object_centroids[:, None] - input_centroids[None, :], axis=2)

        rows, cols = list(range(D.shape[0])), list(range(D.shape[1]))
        matched_rows, matched_cols, matches = set(), set(), []

        while True:
            if D.size == 0: break
            r, c = np.unravel_index(np.argmin(D, axis=None), D.shape)
            if D[r,c] > self.max_distance: break
            matches.append((r,c))
            matched_rows.add(r)
            matched_cols.add(c)
            D[r,:] = np.inf
            D[:,c] = np.inf
            if np.isinf(D).all(): break

        unmatched_rows = [r for r in rows if r not in matched_rows]
        unmatched_cols = [c for c in cols if c not in matched_cols]

        for r,c in matches:
            oid = object_ids[r]
            self.objects[oid] = input_centroids[c]
            self.bboxes[oid] = rects[c]
            self.disappeared[oid] = 0

        for r in unmatched_rows:
            oid = object_ids[r]
            self.disappeared[oid] += 1
            if self.disappeared[oid] > self.max_disappeared:
                self.deregister(oid)

        for c in unmatched_cols:
            self.register(input_centroids[c], rects[c])

        return self.bboxes.copy()

    def unique_count(self):
        return len(self.seen_ids)


def run_people_counter(camera_url, model_name="yolov8m.pt", conf_thresh=0.5, detection_interval=5):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = YOLO(model_name)
    model.overrides = {"conf": conf_thresh}

    cap = cv2.VideoCapture(camera_url, cv2.CAP_FFMPEG)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera stream: {camera_url}")

    tracker = Tracker(max_disappeared=20, max_distance=120)
    frame_count = 0
    current_bboxes = []
    prev_time, fps = time.time(), 0

    while True:
        ret, frame = cap.read()
        if not ret: break

        frame_count += 1

        if frame_count % detection_interval == 0:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = model.predict(source=rgb, imgsz=320, device=device)[0]

            bboxes = []
            if hasattr(results, "boxes") and results.boxes is not None:
                boxes = results.boxes.xyxy.cpu().numpy()
                cls_ids = results.boxes.cls.cpu().numpy().astype(int)
                confs = results.boxes.conf.cpu().numpy()

                for (x1,y1,x2,y2), clsid, conf in zip(boxes, cls_ids, confs):
                    if clsid != 0 or conf < conf_thresh: continue
                    w, h = x2-x1, y2-y1
                    if h < 50 or w/h > 0.9: continue
                    bboxes.append((int(x1), int(y1), int(x2), int(y2)))

            current_bboxes = bboxes

        objects = tracker.update(current_bboxes)

        for oid, bbox in objects.items():
            x1,y1,x2,y2 = bbox
            cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)
            cv2.putText(frame,f"ID {oid}",(x1,y1-10),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0),1)

        info = f"Unique seen: {tracker.unique_count()} | Current: {len(objects)}"
        cv2.putText(frame, info, (10,25), cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,200,255),2)

        now = time.time()
        fps = 0.9*fps + 0.1*(1.0/(now-prev_time) if now-prev_time>0 else 0)
        prev_time = now
        cv2.putText(frame,f"FPS: {fps:.1f}",(10,frame.shape[0]-10),cv2.FONT_HERSHEY_SIMPLEX,0.6,(200,200,200),1)

        cv2.imshow("People Counter", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    camera_IP=
    camera_url = rtsp://admin:admin123@<camera_IP>/avstream/channel=1/stream=0.sdp
    run_people_counter(camera_url)
  
