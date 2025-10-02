import cv2
import numpy as np
import requests
import os
from PIL import Image
import imagehash
import tkinter as tk
from tkinter import Button

# URL của ESP32-CAM
url = "http://192.168.1.225/400x296.jpg"

# Load mô hình nhận dạng khuôn mặt của OpenCV sử dụng DNN
model_path = 'C:\\Users\\dccb1\\OneDrive\\Documents\\QLHS\\opencv_face_detector_uint8.pb'
config_path = 'C:\\Users\\dccb1\\OneDrive\\Documents\\QLHS\\opencv_face_detector.pbtxt'
net = cv2.dnn.readNetFromTensorflow(model_path, config_path)

# Biến đếm để gán ID cho mỗi khuôn mặt
face_id_counter = 0

# Set để lưu trữ các ID đã quét
scanned_ids = set()

# Dictionary để lưu trữ khuôn mặt và mã hash tương ứng
face_dict = {}

# Hàm để đọc mã hash từ các hình ảnh đã biết trong thư mục và lưu vào face_dict
def load_known_faces(data_folder):
    global face_dict

    for folder_name in os.listdir(data_folder):
        folder_path = os.path.join(data_folder, folder_name)
        if os.path.isdir(folder_path):
            hash_values = []
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                if os.path.isfile(file_path):
                    face_encoding = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
                    hash_value = imagehash.average_hash(Image.fromarray(face_encoding))
                    hash_values.append(hash_value)

            if hash_values:
                # Lưu trữ mã hash của tất cả các hình ảnh khuôn mặt trong một thư mục
                face_dict[folder_name] = hash_values

# Gọi hàm để đọc mã hash từ các hình ảnh đã biết
load_known_faces('path/to/data/folder')

def scan_and_save_face(data_folder, url):
    global face_id_counter

    # Kiểm tra xem ID đã tồn tại chưa
    while face_id_counter in scanned_ids:
        face_id_counter += 1

    # Kiểm tra xem ID đã tồn tại trong thư mục data_folder hay chưa
    while os.path.exists(os.path.join(data_folder, str(face_id_counter))):
        face_id_counter += 1

    # Lấy dữ liệu hình ảnh từ ESP32-CAM
    response = requests.get(url)
    img_array = np.array(bytearray(response.content), dtype=np.uint8)
    img = cv2.imdecode(img_array, -1)

    # Chuẩn bị ảnh để đưa vào mô hình
    blob = cv2.dnn.blobFromImage(img, 1.0, (300, 300), [104, 117, 123], False, False)

    # Đưa ảnh vào mô hình
    net.setInput(blob)
    faces = net.forward()

    # Lưu thư mục mới cho khuôn mặt
    face_id = str(face_id_counter)
    face_folder = os.path.join(data_folder, face_id)
    os.makedirs(face_folder, exist_ok=True)

    # Quét và lưu 25 lần ảnh từ khuôn mặt hiện tại
    for j in range(25):
        # Lấy dữ liệu hình ảnh từ ESP32-CAM
        response = requests.get(url)
        img_array = np.array(bytearray(response.content), dtype=np.uint8)
        img = cv2.imdecode(img_array, -1)

        # Tính toán face encoding (đặc trưng của khuôn mặt)
        face_encoding = img[0:300, 0:300]  # Define the region of interest (ROI)

        # Chuẩn bị ảnh để lưu
        face_image_path = os.path.join(face_folder, f'face_{j}.png')
        cv2.imwrite(face_image_path, face_encoding)

        # Đợi một khoảng thời gian ngắn (đơn vị: milliseconds) để lấy các ảnh khác nhau
        cv2.waitKey(40)

    # Trích xuất khuôn mặt từ faces và lưu mã hash vào face_dict
    face_hashes = []
    for i in range(faces.shape[2]):
        confidence = faces[0, 0, i, 2]
        if confidence > 0.5:
            box = faces[0, 0, i, 3:7] * np.array([img.shape[1], img.shape[0], img.shape[1], img.shape[0]])
            (startX, startY, endX, endY) = box.astype(int)

            # Kiểm tra giá trị tọa độ
            startX = max(0, startX)
            startY = max(0, startY)
            endX = min(img.shape[1], endX)
            endY = min(img.shape[0], endY)

            # Tính toán face encoding (đặc trưng của khuôn mặt)
            face_encoding = img[startY:endY, startX:endX]

            # Chuyển đổi face_encoding thành hình ảnh và tính toán mã hash
            face_image = Image.fromarray(face_encoding)
            hash_value = imagehash.average_hash(face_image)

            # Lưu mã hash vào danh sách
            face_hashes.append(hash_value)

    # Lưu danh sách mã hash của các khuôn mặt vào face_dict
    face_dict[face_id] = face_hashes

    print(f"Face ID {face_id} saved successfully.")

    # Thêm ID vào set đã quét
    scanned_ids.add(face_id)

    # Tăng biến đếm ID cho mỗi khuôn mặt mới
    face_id_counter += 1

# Hàm được gọi khi nút quét được nhấn trên màn hình
def on_scan_button_click():
    # Gọi hàm để quét và lưu khuôn mặt mới
    scan_and_save_face('path/to/data/folder', url)

# Tạo cửa sổ giao diện đồ họa
root = tk.Tk()
root.title("Face Recognition")

# Tạo nút quét và đặt sự kiện khi nút được nhấn
scan_button = Button(root, text="Scan Face", command=on_scan_button_click)
scan_button.pack()

while True:
    try:
        # Lấy dữ liệu hình ảnh từ ESP32-CAM
        response = requests.get(url)
        img_array = np.array(bytearray(response.content), dtype=np.uint8)
        img = cv2.imdecode(img_array, -1)

        # Kiểm tra kích thước ảnh
        if img is None or img.shape[0] == 0 or img.shape[1] == 0:
            continue

        # Chuẩn bị ảnh để đưa vào mô hình
        blob = cv2.dnn.blobFromImage(img, 1.0, (300, 300), [104, 117, 123], False, False)

        # Đưa ảnh vào mô hình
        net.setInput(blob)
        faces = net.forward()

        # Hiển thị kết quả
        for i in range(faces.shape[2]):
            confidence = faces[0, 0, i, 2]
            if confidence > 0.5:  # Chỉ hiển thị kết quả có độ chính xác cao hơn 50%
                box = faces[0, 0, i, 3:7] * np.array([img.shape[1], img.shape[0], img.shape[1], img.shape[0]])
                (startX, startY, endX, endY) = box.astype(int)

                # Kiểm tra giá trị tọa độ
                startX = max(0, startX)
                startY = max(0, startY)
                endX = min(img.shape[1], endX)
                endY = min(img.shape[0], endY)

                # Tính toán face encoding (đặc trưng của khuôn mặt)
                face_encoding = img[startY:endY, startX:endX]

                # Tạo mã hash từ khuôn mặt
                hash_value = imagehash.average_hash(Image.fromarray(face_encoding))

                # Tìm xem khuôn mặt đã được nhận diện trước đó chưa
                match_id = None
                for known_id, known_hashes in face_dict.items():
                    for known_hash in known_hashes:
                        # So sánh mã hash để xem liệu khuôn mặt đã biết có giống khuôn mặt mới không
                        if hash_value - known_hash < 30:  # Điều chỉnh ngưỡng tương ứng với mô hình của bạn
                            match_id = known_id
                            break
                    if match_id:
                        break

                # Hiển thị ID màu xanh hoặc màu đỏ
                if match_id:
                    cv2.rectangle(img, (startX, startY), (endX, endY), (0, 255, 0), 2)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(img, f'ID: {match_id}', (startX + 6, endY - 6), font, 0.5, (255, 255, 255), 1)
                else:
                    cv2.rectangle(img, (startX, startY), (endX, endY), (0, 0, 255), 2)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(img, 'Unknown', (startX + 6, endY - 6), font, 0.5, (255, 255, 255), 1)

        # Hiển thị ảnh với khuôn mặt đã được đánh dấu
        cv2.imshow('Face Detection', img)

        # Đợi một khoảng thời gian ngắn (đơn vị: milliseconds) để tăng độ mượt
        cv2.waitKey(10)

        # Cập nhật giao diện đồ họa
        root.update()

    except Exception as e:
        print(f"Error: {e}")

    # Thoát vòng lặp khi nhấn phím 'q'
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

# Đóng cửa sổ khi thoát
cv2.destroyAllWindows()