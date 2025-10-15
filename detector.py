from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
from ultralytics import YOLO
import sqlite3
from datetime import datetime
import base64
import io
from PIL import Image

app = Flask(__name__)
model = YOLO('yolov8n.pt')

# Inicializar DB
def init_db():
    conn = sqlite3.connect('detections.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS detections
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  shape TEXT,
                  count INTEGER,
                  confidence REAL)''')
    conn.commit()
    conn.close()

init_db()

def classify_shape(box):
    x1, y1, x2, y2 = box
    w, h = x2 - x1, y2 - y1
    aspect = w / h if h > 0 else 1
    return "cuadrado" if 0.8 < aspect < 1.2 else "redondo" if aspect > 1.2 else "otro"

def process_frame(frame):
    results = model(frame, conf=0.5)[0]
    shapes = {"cuadrado": 0, "redondo": 0}
    
    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = float(box.conf[0])
        shape = classify_shape([x1, y1, x2, y2])
        
        if shape in shapes:
            shapes[shape] += 1
            color = (0, 255, 0) if shape == "cuadrado" else (255, 0, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{shape} {conf:.2f}", (x1, y1-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    return frame, shapes

def save_detection(shape, count, conf):
    conn = sqlite3.connect('detections.db')
    c = conn.cursor()
    c.execute("INSERT INTO detections VALUES (NULL, ?, ?, ?, ?)",
              (datetime.now().isoformat(), shape, count, conf))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file"}), 400
    
    # Leer archivo
    file_bytes = np.frombuffer(file.read(), np.uint8)
    
    if file.filename.endswith(('.jpg', '.jpeg', '.png')):
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        processed, shapes = process_frame(img)
        
        # Guardar
        for shape, count in shapes.items():
            if count > 0:
                save_detection(shape, count, 0.9)
        
        # Encode result
        _, buffer = cv2.imencode('.jpg', processed)
        img_str = base64.b64encode(buffer).decode()
        
        return jsonify({"image": img_str, "shapes": shapes})
    
    return jsonify({"error": "Formato no soportado"}), 400

@app.route('/history')
def history():
    conn = sqlite3.connect('detections.db')
    c = conn.cursor()
    c.execute("SELECT * FROM detections ORDER BY id DESC LIMIT 50")
    rows = c.fetchall()
    conn.close()
    
    return jsonify([{
        "id": r[0],
        "timestamp": r[1],
        "shape": r[2],
        "count": r[3],
        "confidence": r[4]
    } for r in rows])

@app.route('/clear', methods=['POST'])
def clear():
    conn = sqlite3.connect('detections.db')
    c = conn.cursor()
    c.execute("DELETE FROM detections")
    conn.commit()
    conn.close()
    return jsonify({"success": True})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)