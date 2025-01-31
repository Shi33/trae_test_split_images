import os
import cv2
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# 配置上传文件夹
UPLOAD_FOLDER = 'uploads'
FRAMES_FOLDER = 'frames'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(FRAMES_FOLDER, exist_ok=True)

@app.route('/enhance', methods=['POST'])
def enhance_image():
    if 'image' not in request.files:
        return jsonify({'error': '没有找到图片文件'}), 400
    
    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400

    # 保存上传的图片
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    input_path = os.path.join(UPLOAD_FOLDER, f'input_{timestamp}.jpg')
    output_path = os.path.join(UPLOAD_FOLDER, f'output_{timestamp}.jpg')
    image_file.save(input_path)

    try:
        # 读取图片
        img = cv2.imread(input_path, cv2.IMREAD_COLOR)
        if img is None:
            return jsonify({'error': '无法读取图片文件'}), 400

        # 图像增强处理
        # 1. 调整亮度和对比度
        alpha = 1.2  # 对比度增强因子
        beta = 10    # 亮度增强因子
        img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)

        # 2. 应用锐化滤波器
        kernel = np.array([[-1,-1,-1],
                          [-1, 9,-1],
                          [-1,-1,-1]])
        img = cv2.filter2D(img, -1, kernel)

        # 3. 使用双边滤波减少噪声同时保持边缘清晰
        img = cv2.bilateralFilter(img, 9, 75, 75)

        # 保存处理后的图片
        cv2.imwrite(output_path, img)

        # 将处理后的图片转换为base64
        with open(output_path, 'rb') as img_file:
            img_data = base64.b64encode(img_file.read()).decode('utf-8')

        # 清理临时文件
        os.remove(input_path)
        os.remove(output_path)

        return jsonify({
            'enhanced_image': f'data:image/jpeg;base64,{img_data}'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        # 确保清理临时文件
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': '没有找到视频文件'}), 400
    
    video_file = request.files['video']
    if video_file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400

    # 保存视频文件
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    video_path = os.path.join(UPLOAD_FOLDER, f'video_{timestamp}.mp4')
    video_file.save(video_path)

    def generate():
        try:
            # 打开视频文件
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                yield '{"error": "无法打开视频文件"}\n'
                return

            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_count = 0
            batch_size = 50  # 每批次处理的帧数
            current_batch = []
            batch_number = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # 保存帧为图片
                frame_path = os.path.join(FRAMES_FOLDER, f'frame_{timestamp}_{frame_count}.jpg')
                cv2.imwrite(frame_path, frame)

                # 将图片转换为base64
                with open(frame_path, 'rb') as img_file:
                    img_data = base64.b64encode(img_file.read()).decode('utf-8')
                    current_batch.append(f'data:image/jpeg;base64,{img_data}')

                frame_count += 1
                progress = int((frame_count / total_frames) * 100)
                
                # 每处理5帧返回一次进度
                if frame_count % 5 == 0:
                    yield f'{{"type": "progress", "progress": {progress}}}\n'

                # 当达到批次大小时，返回当前批次数据
                if len(current_batch) >= batch_size:
                    batch_response = {
                        "type": "batch",
                        "batch_number": batch_number,
                        "total_batches": (total_frames + batch_size - 1) // batch_size,
                        "frames": current_batch
                    }
                    yield json.dumps(batch_response) + '\n'
                    current_batch = []
                    batch_number += 1

            # 返回最后一批数据
            if current_batch:
                batch_response = {
                    "type": "batch",
                    "batch_number": batch_number,
                    "total_batches": (total_frames + batch_size - 1) // batch_size,
                    "frames": current_batch,
                    "is_last": True
                }
                yield json.dumps(batch_response) + '\n'

        except Exception as e:
            yield f'{{"error": "{str(e)}"}}\n'

        finally:
            if 'cap' in locals():
                cap.release()
            if os.path.exists(video_path):
                os.remove(video_path)
            for frame_path in os.listdir(FRAMES_FOLDER):
                if frame_path.startswith(f'frame_{timestamp}'):
                    try:
                        os.remove(os.path.join(FRAMES_FOLDER, frame_path))
                    except OSError as e:
                        print(f'清理临时文件失败: {e}')

    return app.response_class(generate(), mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True, port=5001)