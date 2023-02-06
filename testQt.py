import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMessageBox
from open_camera import Ui_MainWindow
import numpy as np
import cv2
import  datetime

from random import uniform
from PyQt5.Qt import *
import sqlite3
from time import *
import datetime
import gc
from multiprocessing import Process, Queue
global images

from threading import Lock, Thread

lock_video_writer = Lock()



class Open_Camera(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(Open_Camera, self).__init__()
        self.setupUi(self)  # 创建窗体对象
        self.init()
        self.cap = cv2.VideoCapture()  # 初始化摄像头
        self.video_writer = None
        self.photo_flag = 0
        self.label.setScaledContents(True)  # 图片自适应
        self.num=0

    def init(self):
        # 定时器让其定时读取显示图片
        self.camera_show_timer = QTimer()
        self.camera_show_timer.timeout.connect(self.show_image)
        # 打开摄像头
        self.pushButton.clicked.connect(self.open_camera)
        # 拍照
        self.pushButton_3.clicked.connect(self.taking_pictures)
        # 关闭摄像头
        self.pushButton_2.clicked.connect(self.close_camera)
        #存入视频
        self.video_writer_timer = QTimer()
        self.video_writer_timer.timeout.connect(self.new_video_writer)
        self.write_video_frame_timer = QTimer()
        self.write_video_frame_timer.timeout.connect(self.write_video_frame)
        self.pushButton_4.clicked.connect(self.save)
        # 导入图片
        self.pushButton_5.clicked.connect(self.loadphoto)

    '''开启摄像头'''

    def open_camera(self):
        self.cap = cv2.VideoCapture(0)
        #self.cap = cv2.VideoCapture("rtsp://admin:toybrick123456@192.168.1.64:554/h265/ch1/main/av_stream")  # 摄/像头
        self.camera_show_timer.start(30)
        # 每40毫秒读取一次，即刷新率为25帧
        self.show_image()

    '''显示图片'''

    def show_image(self):
        flag, image = self.cap.read()  # 从视频流中读取图片
        if flag is False:
            print("show_image cap read error")
            sys.pause()
        image_show = cv2.resize(image, (1280, 720))  # 把读到的帧的大小重新设置为 600*360
        width, height = image_show.shape[:2]  # 行:宽，列:高
        image_show = cv2.cvtColor(image_show, cv2.COLOR_BGR2RGB)  # opencv读的通道是BGR,要转成RGB
        image_show = cv2.flip(image_show, 1)  # 水平翻转，因为摄像头拍的是镜像的。
        # 把读取到的视频数据变成QImage形式(图片数据、高、宽、RGB颜色空间，三个通道各有2**8=256种颜色)
        self.showImage = QtGui.QImage(image_show.data, height, width, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(self.showImage))  # 往显示视频的Label里显示QImage
        # self.label.setScaledContents(True) #图片自适应

    '''拍照'''

    def taking_pictures(self):
           # FName = fr"images/cap{time.strftime('%Y%m%d%H%M%S', time.localtime())}"
            #print(FName)
           # QMessageBox.information(self,"Information","开始存储",QMessageBox.Ok)

        while (self.cap.isOpened()):
            ret, frame = self.cap.read()
            if frame is None:  # 防止后面卡死 或 视频最后为空
                break
            conn = sqlite3.connect('myInfo.db')
            # 在数据库中创建一个表（序号，图片）
            cursor = conn.cursor()
            array_bytes = self.image.tobytes()
            c = localtime()
            d = strftime('%Y%m%d%H%M%S', c)
            # print("数据类型：", type(array_bytes))
            cursor.execute("INSERT into myInfo values(?,?);", (d, array_bytes))  # 存储为图像，图像以当前时间命名
            conn.commit()
            if cv2.waitKey(1):
                continue
        else:
            QMessageBox.critical(self, '错误', '摄像头未打开！')
            return None

    '''关闭摄像头'''

    def close_camera(self):
        self.camera_show_timer.stop()  # 停止读取
        self.cap.release()  # 释放摄像头
        self.label.clear()  # 清除label组件上的图片
        self.label.setText("摄像头")
        self.flag=False
        # self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # 摄像头
    '''视频到本地'''

    def new_video_writer(self):
        print("in new_video_writer")
        # fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')   # mp4
        fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')  # avi
        size = (int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        frame_s = int(20)
        lock_video_writer.acquire()
        if self.video_writer is not None:
            self.video_writer.release()
        i = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = 'D:\\Project\\RK3399Pro\\CrowdCounting_ByteTrack\\Qt_display\\' + str(i) + '.avi'
        self.video_writer = cv2.VideoWriter(filename, fourcc, frame_s, size, True)  # 参数：视频文件名，格式，每秒帧数，宽高，是否灰度
        lock_video_writer.release()
        self.write_video_frame_timer.start(0)
        self.video_writer_timer.start(5000)


    def write_video_frame(self):
        print("in write_video_frame")
        lock_video_writer.acquire()
        flag, image = self.cap.read()
        if flag is False:
            print("write_video_frame cap read error")
            sys.pause()
        self.video_writer.write(image)
        lock_video_writer.release()
        self.write_video_frame_timer.start(50)

    def save(self):
        # self.cap = cv2.VideoCapture(0)
        # self.cap = cv2.VideoCapture("rtsp://admin:toybrick123456@192.168.1.64:554/h265/ch1/main/av_stream")  # 摄/像
        #self.camera_timer.start(30)#每40毫秒读取一次，即刷新率为25帧
        print("in save")
        self.video_writer_timer.start(0)
        # self.save_mp4()

    def save_mp4(self):
        while (self.cap_write.isOpened()):
            # frame_s = self.cap.get(5)
            # fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')   # mp4
            fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')    # avi
            size = (int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            frame_s = int(20)
            time_frame = frame_s * 5
            video_writer = None
            # sys.pause()
            # num = 0
            while self.flag:
                if self.num % time_frame == 0 or self.num == 0:
                    if video_writer is not None:
                        video_writer.release()
                    i = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                    filename = 'D:\\Project\\RK3399Pro\\CrowdCounting_ByteTrack\\Qt_display\\' + str(i) + '.avi'
                    # print(filename)
                    video_writer = cv2.VideoWriter(filename, fourcc, frame_s, size, True)  # 参数：视频文件名，格式，每秒帧数，宽高，是否灰度
                    print("hello")
                # if cv2.waitKey(1) & 0xff == ord('q'):
                #     print("in here")
                #     break
                # print(self.num)
                # images = self.image
                # mutex.acquire()
                # images = self.write_images[0]
                # print(images)
                # self.write_images.pop(0)
                # mutex.release()
                flag_write, images = self.cap_write.read()
                if flag_write:
                    video_writer.write(images)
                    self.num = self.num+1
                else:
                    print("flag_write not ok")
        else:
            QMessageBox.critical(self, '错误', '摄像头未打开！')
            return None

    # 导入图片
    def loadphoto(self):
        fname, _ = QFileDialog.getOpenFileName(self, '选择图片', '../', 'Image files(*.jpg *.gif *.png*.bmp)')
        self.showImage = fname


if __name__ == '__main__':
    from PyQt5 import QtCore
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)  # 自适应分辨率
    app = QtWidgets.QApplication(sys.argv)
    ui = Open_Camera()
    ui.show()
    sys.exit(app.exec_())
