from ultralytics import YOLO
import cv2


model = YOLO("yolov8n.pt")


image_path = r"C:\Users\Lenovo\Desktop\InterioAI\Images\img2.jpg"


results = model(image_path)


img = cv2.imread(image_path)


room_objects = ["bed", "chair", "couch", "tv", "dining table", "toilet", "sink", "window", "door"]

for r in results:
    for box in r.boxes:
        cls_id = int(box.cls[0])
        label = model.names[cls_id]
        if label in room_objects:
            coords = box.xyxy[0].cpu().numpy().astype(int)
            x1, y1, x2, y2 = coords
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

cv2.imwrite(r"C:\Users\Lenovo\Desktop\InterioAI\Outputs\detected_room.jpg", img)
cv2.imshow("Room Detection", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
