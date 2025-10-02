import tkinter as tk
from tkinter import *
from tkinter import ttk
import tkinter.ttk as ttk
import mysql.connector
from tkinter import messagebox
import datetime
import serial.tools.list_ports
import functools
from threading import Thread
import time
from openpyxl import Workbook
from tkinter import filedialog
import cv2
import numpy as np
import requests
import os
from PIL import Image
import imagehash
from tkinter import Button
# -------------------------------- Khai báo  ---------------------------------------

# Kết nối với sql
kn = mysql.connector.connect(user = 'root',password = 'thpttvo1969@',host = 'localhost', database='quan_li_hoc_sinh')
# Định dạng khung hình window  
screen = tk.Tk()
screen.title('Quản lí học sinh - Trung học Cơ sở' )
screen.geometry('1360x600')
screen.resizable(False,False)

# -------------------------------- Biến ---------------------------------------

uid = StringVar()
uid_f = StringVar()
ten = StringVar()
gender = StringVar()
lop = StringVar()
Face_id = StringVar()
search__uid = StringVar()
search__ten = StringVar()
search__lop = StringVar()

# -------------------------------- Label tiêu đề ---------------------------------------

Label(screen, text = "Hệ thống quản lí học sinh - Trung học Cơ sở", fg = 'blue',font=('cambria',16)).grid(row = 0, column = 0)
Label(screen, text = "Dữ liệu thông tin học sinh", fg = 'blue',font=('cambria',16)).grid(row = 0, column = 3)

# -------------------------------- Tạo ra bảng 1 ---------------------------------------

tree = ttk.Treeview(columns=('0', '1', '2', '3', '4', '5', '6', '7'),show = 'headings',height= 15,)
tree.grid(row = 1, column = 0,columnspan=2)
tree.heading(0, text = 'Ngày')
tree.heading(1, text = 'UID')
tree.heading(2, text = 'Tên')
tree.heading(3, text = 'Lớp')
tree.heading(4, text = 'Giới tính')
tree.heading(5, text = 'Khu vực')
tree.heading(6, text = 'Vô trễ')
tree.heading(7, text = 'Face ID')
tree.column(0,width = 140)
tree.column(1,width = 180)
tree.column(2,width = 250)
tree.column(3,width = 60)
tree.column(4,width = 60)
tree.column(5,width = 60)
tree.column(6,width = 50)
tree.column(7,width = 50)
query = 'select * from qlhs ORDER BY Ngay DESC '
qshow = kn.cursor()
qshow.execute(query)
row = qshow.fetchall()
# Tải sql
for k in row:
    tree.insert('','end',values=k)      
# Label phân cách
Label(screen, text = " | ").grid(row = 1, column = 2)

# -------------------------------- Tạo ra bảng 2 ---------------------------------------

# Bảng chứa data học sinh
tree1 = ttk.Treeview(columns=(1,2,3,4,5),show = 'headings',height= 15)
tree1.grid(row = 1, column = 3,columnspan=2)
tree1.heading(1, text = 'UID')
tree1.heading(2, text = 'Tên')
tree1.heading(3, text = 'Lớp')
tree1.heading(4, text = 'Giới tính')
tree1.heading(5, text = 'Face ID')
tree1.column(1,width = 120)
tree1.column(2,width = 200)
tree1.column(3,width = 50)
tree1.column(4,width = 50)
tree1.column(5,width = 50)
# Tải bảng
query = 'select * from qlhs1 ORDER BY Lop ASC '
qshow = kn.cursor()
qshow.execute(query)
row = qshow.fetchall()
# Tải sql
for k in row:
    tree1.insert('','end',values= k)

# -------------------------------- Xử lí hình ảnh ---------------------------------------

url = "http://192.168.43.225/240x176.jpg"

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
    messagebox.showinfo("Thông báo", "Thêm id " + face_id + ' thành công') 

    # Thêm ID vào set đã quét
    scanned_ids.add(face_id)

    # Tăng biến đếm ID cho mỗi khuôn mặt mới
    face_id_counter += 1

# Hàm được gọi khi nút quét được nhấn trên màn hình
def on_scan_button_click():
    # Gọi hàm để quét và lưu khuôn mặt mới
    scan_and_save_face('path/to/data/folder', url)

def xl():   # Tạo nút quét và đặt sự kiện khi nút được nhấn
    root1 = tk.Tk()
    root1.withdraw()
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
                                if hash_value - known_hash < 10:  # Điều chỉnh ngưỡng tương ứng với mô hình của bạn
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
                root1.update()   
                # screen.after(100, screen.update())
            except Exception as e:
                print(f"Error: {e}")

            # Thoát vòng lặp khi nhấn phím 'q'
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):

                break

        # Đóng cửa sổ khi thoát
    cv2.destroyAllWindows()

# -------------------------------- Chọn cổng com ---------------------------------------

# Khai báo các biến
ports = serial.tools.list_ports.comports()
serialObj = serial.Serial()

# Biến cờ để theo dõi trạng thái mở cổng
is_serial_open = False

# Hàm kiểm tra cổng com
def initComPort(index):
    global is_serial_open
    currentPort = str(ports[index])
    comPortVar = str(currentPort.split(' ')[0])
    print(comPortVar)
    serialObj.port = comPortVar
    serialObj.baudrate = 9600
    try:
        serialObj.open()
        is_serial_open = True
    except serial.SerialException as e:
        print("Lỗi mở cổng serial:", e)
        is_serial_open = False

# Hàm hiển thị cổng com
for onePort in ports:
    comButton = Button(screen, text=onePort, font=('Calibri', '10'), height=1, width=35, command = functools.partial(initComPort, index = ports.index(onePort)))
    comButton.grid(row=ports.index(onePort) + 6, column=1)
# Hàm xử lí chính
def xuli_in():
 

    global is_serial_open

    # Chờ đến khi cổng serial được mở
    while not is_serial_open:
        time.sleep(0.1)


    while True:
        try:
            if serialObj.in_waiting > 0:
                data = serialObj.readline()
                data = serialObj.readline()
                data = str(data, 'utf8')
                data = data.strip('\r\n')
                data = data.strip(' ')
                data_in = [
                    (data,)
                ]
                daytime = (data,)
                print("Dữ liệu nhận được:", data_in)
                query = ' INSERT INTO `qlhs` (`Ngay`, `UID`) VALUES (NOW(),%s)  '
                my_data_add = kn.cursor()
                for item in data_in:
                    my_data_add.execute(query, item)
                    kq1 = kn.cursor()
                    query2 = "UPDATE qlhs SET Ten = ( SELECT Ten FROM qlhs1 WHERE qlhs.UID = qlhs1.UID), Lop = ( SELECT Lop FROM qlhs1 WHERE qlhs.UID = qlhs1.UID) , Gioi_tinh = ( SELECT Gioi_tinh FROM qlhs1 WHERE qlhs.UID = qlhs1.UID)"
                    kq1.execute(query2)
                    kn.commit()
                __time__(daytime)
                __show__()
                __face_detection__main(data)
        except serial.SerialException as e:
            pass
    
#  Chia luồng chạy song song


# -------------------------------- Hàm thời gian vô trễ ---------------------------------------

def __time__(a):
    today = datetime.datetime.now()
    dt1 = datetime.datetime(2023, 10, 17, 6, 51, 0, 0)
    if today.hour > dt1.hour : 
        print("Học sinh đã vô trễ")
        query = "UPDATE `qlhs` SET Vo_tre = 'Có' WHERE UID = %s and DATE(Ngay) = CURRENT_DATE()"
        my_data_add = kn.cursor()
        my_data_add.execute(query,a)
        kn.commit()
    else: 
        print("Học sinh vô đúng giờ")
        query = "UPDATE `qlhs` SET Vo_tre = 'Không' WHERE UID = %s and DATE(Ngay) = CURRENT_DATE() "
        my_data_add = kn.cursor()
        my_data_add.execute(query,a)
        kn.commit()

# -------------------------------- Hàm Xóa thông tin học sinh ---------------------------------------

def __delete__():
    sel = tree1.selection()[0]
    uid = tree1.item(sel)['values'][0]
    query1 = ' delete from qlhs1 where UID=%s'
    data=(uid,)
    q_del = kn.cursor()
    q_del.execute(query1,data)
    kn.commit()
    tree1.delete(sel)
    messagebox.showinfo("Thông báo", "Xóa thành công") 

# -------------------------------- Hàm thêm thông tin học sinh ---------------------------------------

def __add__():
    ss = ['','','']
    
    sosanh = [uid.get(),ten.get(),lop.get(),gender.get(),]
    
    hs = [
        (uid.get(),ten.get(),lop.get(),gender.get(),Face_id.get())
    ]
    
    if sosanh [0] != ss[0] and sosanh[1] != ss[1]:
        for p in hs:
            tree1.insert('','end',values=p) 
        query = ' INSERT INTO `qlhs1` (`UID`, `Ten`,`Lop`,`Gioi_tinh`,`Face_ID`) VALUES (%s,%s,%s,%s,%s)  '
        my_data_add = kn.cursor()
        for item in hs:
            my_data_add.execute(query, item)
        kn.commit()
        messagebox.showinfo("Thông báo", "Thêm thành công") 
    else:
        messagebox.showerror("Lỗi", "Bạn đã nhập thiếu") 

# -------------------------------- Hàm hiển thị của bảng 1 ------------------------------------------
 
def __show__():
    tree.delete(*tree.get_children())
    query = 'select * from qlhs ORDER BY Ngay DESC '
    qshow = kn.cursor()
    qshow.execute(query)
    row = qshow.fetchall()
    for k in row:
         tree.insert('','end', values =  k )

def __show__search(x):
    tree.delete(*tree.get_children())
    x1 = (x,)
    query = 'select * from qlhs Where Lop = %s ORDER BY Lop ASC  '
    qshow = kn.cursor()
    qshow.execute(query,x1)
    row1 = qshow.fetchall()
    
    tree1.delete(*tree1.get_children())
    query1 = 'select * from qlhs1 Where Lop = %s ORDER BY Lop ASC  '
    qshow = kn.cursor()
    qshow.execute(query1,x1)
    row = qshow.fetchall()
    
    if row == []:
         messagebox.showerror("Lỗi", "Không có dữ liệu") 
         print(x)
    else:
        for k in row:
            tree1.insert('','end', values =  k )
        for k1 in row1:
            tree.insert('','end', values =  k1 )

# -------------------------------- Hàm hiển thị của bảng 2 ------------------------------------------
   
def __show__1(x):
    for item in x.get_children():
      x.delete(item)
    query = 'select * from qlhs1'
    qshow = kn.cursor()
    qshow.execute(query)
    row = qshow.fetchall()
    for k in row:
         x.insert('','end', values =  k )

# -------------------------------- Hàm hiển thị bảng lên màn hình ---------------------------------------
         
def si_show():
    __show__1(tree1)
    messagebox.showinfo("Thông báo", "Đã tải lại") 
    
# -------------------------------- Hàm tìm kiếm dữ liệu học sinh ------------------------------------------

def __search__():
    data__search__none = ['','','']

    data__search = [
        search__uid.get(),search__ten.get(),search__lop.get()
    ]

    uid = search__uid.get()
    ten = search__ten.get()
    data__uid = (uid,)
    data__ten = (ten,)
    Search = kn.cursor()
    
    if data__search[0] != data__search__none[0] and data__search[1] == data__search__none[1]:
        query1 = 'SELECT * FROM qlhs where UID =%s'
        Search.execute(query1,data__uid)
        Show__search = Search.fetchall()
        kn.commit()
        if Show__search != []:
            __show_search__(Show__search)
        else:
            messagebox.showerror("Lỗi", "Dữ liệu tìm kiếm không tồn tại") 
            
    elif data__search[1] != data__search__none[1] and data__search[0] == data__search__none[0]:
        query2 = 'SELECT * FROM qlhs where Ten =%s'
        Search.execute(query2,data__ten)
        Show__search = Search.fetchall()
        
        kn.commit()
        if Show__search != []:
            __show_search__(Show__search)
        else:
            messagebox.showerror("Lỗi", "Dữ liệu tìm kiếm không tồn tại")
            
    elif data__search == data__search__none:
        messagebox.showerror("Lỗi", "Dữ liệu tìm kiếm không tồn tại") 
        __show__()

    return Show__search
    
# Hiển thị thông tin tìm kiến 
def __show_search__(a):
    tree.delete(*tree.get_children())
    for i in a:
        tree.insert('','end',values=i)
    
        
# -------------------------------- Xuất excel thông tin tìm kiếm ------------------------------------------

def __export_excel__(a):
    Search = kn.cursor()
    Show__search = __search__()
    wb = Workbook()
    ws = wb.active
    ws.title = 'Vô Trễ'
    for row in Show__search :
        ws.append(row)
    wb.save(a)
    messagebox.showinfo("Thông báo", "Đã xuất file")
        
def __export_excel__path():
    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
    if file_path:
        __export_excel__(file_path)
# -------------------------------- Hàm xuất file Excel ---------------------------------------

def __out_excel__(a):
    
    # today = datetime.datetime.now()
    # data = (today.year, today.month, today.day)
    cur = kn.cursor()
    query = "SELECT * FROM qlhs WHERE DATE(Ngay) = CURRENT_DATE();"
    print(query)
    cur.execute(query)
    result = cur.fetchall()
    table_name = [i[0] for i in cur.description]
    wb = Workbook()
    ws = wb.active
    ws.title = 'Vô Trễ'
    ws.append(table_name)
    for row in result:
        ws.append(row)
    wb.save(a)
    messagebox.showinfo("Thông báo", "Đã xuất file")

        
def __out_excel__path():
    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
    if file_path: 
        __out_excel__(file_path)
        
# -------------------------------- Thiết lập nút ------------------------------------------

button = Frame(screen)
button1 = Frame(screen)
button2 = Frame(screen)

# -------------------------------- Bảng 2 ------------------------------------------

Label(screen, text = "UID :").grid(row = 2, column = 3,sticky = W )
Label(screen, text = "Họ và Tên :").grid(row = 3, column = 3,sticky = W)
Label(screen, text = "Lớp :").grid(row = 4, column = 3,sticky = W)
Label(screen, text = "Giới tính :").grid(row = 5, column = 3,sticky = W)
Label(screen, text = "Face ID :").grid(row = 6, column = 3,sticky = W)

Entry(screen,width = 30, textvariable= uid).grid(row = 2, column = 3)
Entry(screen,width = 30, textvariable = ten).grid(row = 3, column = 3)
Entry(screen,width = 30, textvariable = lop).grid(row = 4, column = 3)
Entry(screen,width = 30, textvariable = gender).grid(row = 5, column = 3)
Entry(screen,width = 30, textvariable = Face_id).grid(row = 6, column = 3)

# -------------------------------- Bảng 1 ------------------------------------------

Label(screen, text = "--Tìm kiếm--").grid(row = 2, column = 0,sticky = W )
Label(screen, text = "UID :").grid(row = 3, column = 0,sticky = W )
Label(screen, text = "Họ và Tên :").grid(row = 4, column = 0,sticky = W)


Entry(screen,width = 30, textvariable=  search__uid).grid(row = 3, column = 0)
Entry(screen,width = 30, textvariable = search__ten).grid(row = 4, column = 0)

Button(button1 , text = '--Tìm kiếm--',command= __search__ ).pack(side=RIGHT)
Button(button1 , text = '--Xuất Excel--',command=lambda: __export_excel__("Search.xlsx") ).pack(side=RIGHT)
button1.grid(row= 5 , column = 0)

# -------------------------------- Nút --------------------------------------------

Button(button,text = ' Xóa',command= __delete__ ).pack(side=LEFT)
Button(button,text = ' Thêm',command= __add__, ).pack(side=LEFT)
Button(button,text = ' Tải lại ',command= si_show ).pack(side=LEFT)
Button(button2,text = '--Xuất Excel học sinh vô trễ--',command=lambda: __out_excel__("QLHS.xlsx") ).pack(side=LEFT)
button.grid(row= 7 , column = 3)
button2.grid(row= 6 , column = 0)

# -------------------------------- Xử lí hình ảnh  --------------------------------------------

def __face_detection__main(a):
        try:
            # Lấy dữ liệu hình ảnh từ ESP32-CAM
            response = requests.get(url)
            img_array = np.array(bytearray(response.content), dtype=np.uint8)
            img = cv2.imdecode(img_array, -1)

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
                            if hash_value - known_hash < 10:  # Điều chỉnh ngưỡng tương ứng với mô hình của bạn
                                match_id = known_id
                                break
                        if match_id:
                            break
                    if match_id:
                        a1 = (a,)
                        query = "SELECT * FROM qlhs1 Where UID = %s and Face_ID = %s "
                        kq = kn.cursor()
                        data_in = [
                            (a,match_id,)
                            ]
                        for i in data_in:
                            kq.execute(query,i)
                            l = kq.fetchall()
                            print('1',l)
                        if l != []:
                            query1 = "UPDATE qlhs SET Face_id = 'OK' WHERE UID = %s "
                            kq.execute(query1,a1)
                        else:
                            query2 = "UPDATE qlhs SET Face_id = 'NO' WHERE UID = %s"
                            kq.execute(query2,a1)

                    
            
            # screen.after(100, screen.update())
        except Exception as e:
            print(f"Error: {e}")
            
            
def face_detection():
    root = tk.Tk()
    root.title("Face Recognition")
    scan_button = Button(root, text="Scan Face", command=on_scan_button_click)
    scan_button.grid(column= 0, row = 0)
    root.geometry('150x150')


    

# -------------------------------- Menu Bar ---------------------------------------

def _quit():
    screen.quit()
    screen.destroy()

menubar = Menu(screen)
screen.config(menu=menubar)

file_menu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Xuất file EXCEL", command= __out_excel__path)
file_menu.add_command(label="Xuất file tìm kiếm", command=__export_excel__path)
file_menu.add_command(label="Quit", command=_quit)

Camera = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Camera", menu=Camera)
Camera.add_command(label= "Thêm khuôn mặt",command=face_detection)

DS = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Danh sách", menu=DS)

DS_khoi6 = Menu(DS , tearoff=0)
DS_khoi6.add_command(label="Lớp 6/1", command=lambda: __show__search('6/1'))
DS_khoi6.add_command(label="Lớp 6/2", command=lambda: __show__search('6/2'))
DS_khoi6.add_command(label="Lớp 6/3", command=lambda: __show__search('6/3'))
DS_khoi6.add_command(label="Lớp 6/4", command=lambda: __show__search('6/4'))
DS_khoi6.add_command(label="Lớp 6/5", command=lambda: __show__search('6/5'))
DS_khoi6.add_command(label="Lớp 6/6", command=lambda: __show__search('6/6'))
DS_khoi6.add_command(label="Lớp 6/7", command=lambda: __show__search('6/7'))
DS_khoi6.add_command(label="Lớp 6/8", command=lambda: __show__search('6/8'))
DS_khoi6.add_command(label="Lớp 6/9", command=lambda: __show__search('6/9'))

DS_khoi7 = Menu(DS , tearoff=0)
DS_khoi7.add_command(label="Lớp 7/1", command=lambda: __show__search('7/1'))
DS_khoi7.add_command(label="Lớp 7/2", command=lambda: __show__search('7/2'))
DS_khoi7.add_command(label="Lớp 7/3", command=lambda: __show__search('7/3'))
DS_khoi7.add_command(label="Lớp 7/4", command=lambda: __show__search('7/4'))
DS_khoi7.add_command(label="Lớp 7/5", command=lambda: __show__search('7/5'))
DS_khoi7.add_command(label="Lớp 7/6", command=lambda: __show__search('7/6'))
DS_khoi7.add_command(label="Lớp 7/7", command=lambda: __show__search('7/7'))
DS_khoi7.add_command(label="Lớp 7/8", command=lambda: __show__search('7/8'))
DS_khoi7.add_command(label="Lớp 7/9", command=lambda: __show__search('7/9'))

DS_khoi8 = Menu(DS , tearoff=0)
DS_khoi8.add_command(label="Lớp 8/1", command=lambda: __show__search('8/1'))
DS_khoi8.add_command(label="Lớp 8/2", command=lambda: __show__search('8/2'))
DS_khoi8.add_command(label="Lớp 8/3", command=lambda: __show__search('8/3'))
DS_khoi8.add_command(label="Lớp 8/4", command=lambda: __show__search('8/4'))
DS_khoi8.add_command(label="Lớp 8/5", command=lambda: __show__search('8/5'))
DS_khoi8.add_command(label="Lớp 8/6", command=lambda: __show__search('8/6'))
DS_khoi8.add_command(label="Lớp 8/7", command=lambda: __show__search('8/7'))
DS_khoi8.add_command(label="Lớp 8/8", command=lambda: __show__search('8/8'))
DS_khoi8.add_command(label="Lớp 8/9", command=lambda: __show__search('8/9'))

DS_khoi9 = Menu(DS , tearoff=0)
DS_khoi9.add_command(label="Lớp 9/1", command=lambda: __show__search('9/1'))
DS_khoi9.add_command(label="Lớp 9/2", command=lambda: __show__search('9/2'))
DS_khoi9.add_command(label="Lớp 9/3", command=lambda: __show__search('9/3'))
DS_khoi9.add_command(label="Lớp 9/4", command=lambda: __show__search('9/4'))
DS_khoi9.add_command(label="Lớp 9/5", command=lambda: __show__search('9/5'))
DS_khoi9.add_command(label="Lớp 9/6", command=lambda: __show__search('9/6'))
DS_khoi9.add_command(label="Lớp 9/7", command=lambda: __show__search('9/7'))
DS_khoi9.add_command(label="Lớp 9/8", command=lambda: __show__search('9/8'))
DS_khoi9.add_command(label="Lớp 9/9", command=lambda: __show__search('9/9'))

DS.add_cascade(label="Khối 6", menu = DS_khoi6 )
DS.add_cascade(label="Khối 7", menu = DS_khoi7 )
DS.add_cascade(label="Khối 8", menu = DS_khoi8 )
DS.add_cascade(label="Khối 9", menu = DS_khoi9 )
DS.add_cascade(label="Khối 10")
DS.add_cascade(label="Khối 11")
DS.add_cascade(label="Khối 12")


thread1 = Thread(target = xuli_in)
thread1.start()  
thread2 = Thread(target = xl)
thread2.start() 
screen.mainloop()   