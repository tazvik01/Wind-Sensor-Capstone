import sys
from datetime import datetime
import math
import time

from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, 
    QComboBox, QLineEdit,
)

import serial 
from PyQt6.QtGui import QPixmap
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QUrl, QTimer 
import os 
import openpyxl
from PyQt6.QtWebEngineCore import QWebEngineSettings
import serial.tools.list_ports

from PyQt6.QtGui import  QPainter, QPen
from PyQt6.QtCore import QPointF, QRectF
import random




class Datalogger(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setWindowTitle("Data Logger")
        self.setFixedWidth(550)
        self.setFixedHeight(500)
        self.setStyleSheet("QWidget { background-color: #f1eeee; color: black; } QComboBox { border: 1px solid black; }")

        label_dict = {
            'running_time_avg_lbl' : 'RUNNING TIME AVERAGE:',
            'location_lbl' : 'LOCATION:',
        }

        button_layout = QVBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
        button_layout.setSpacing(150)

        data_btn = QPushButton("DATA", self)
        data_btn.setFixedSize(120,50)
        data_btn.setFixedSize(120,50)
        button_layout.addWidget(data_btn)

        self.hoverStyleSheet = (
            'QPushButton{background-color: #803dae;color:white;}'
            'QPushButton:hover{background-color: #803dae;color:white;}'
            'QPushButton:pressed{border: 5px solid rgb(135,206,250);}'
            'QToolTip {background-color: black; color: white; border: black solid 1px;}'
        )

        label_layout = QVBoxLayout()
        label_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
        label_layout.setSpacing(0)

        running_time_average_row = QHBoxLayout()
        running_time_average_row.setSpacing(20)

        location_row = QHBoxLayout()
        location_row.setSpacing(100)

        self.text_box_timeavg = QLineEdit()
        self.text_box_timeavg.setReadOnly(True)
        self.text_box_timeavg.setFixedSize(350, 20)
        self.text_box_timeavg.setPlaceholderText("Error")

        self.text_box_location = QLineEdit()
        self.text_box_location.setReadOnly(True)
        self.text_box_location.setFixedSize(350, 20)
        self.text_box_location.setPlaceholderText("Error")

        for key,val in label_dict.items():
            label = QLabel(val)
            if val == 'RUNNING TIME AVERAGE:':
                running_time_average_row.addWidget(label)
                running_time_average_row.addWidget(self.text_box_timeavg)
                label_layout.addLayout(running_time_average_row)
            elif val == 'LOCATION:':
                location_row.addWidget(label)
                location_row.addWidget(self.text_box_location)
                label_layout.addLayout(location_row)

        data_btn.setStyleSheet(self.hoverStyleSheet)
        layout.addLayout(label_layout)
        layout.addLayout(button_layout)
        data_btn.clicked.connect(self.data_btn_functionality)

    def data_btn_functionality(self):
        path = "C:\\WindSensor_DataLogger"
        path = os.path.realpath(path)
        os.startfile(path)
    
        


        # while True:
        #     i=0
        #     workbook = xlswriter.Workbook(f'C:\\WindSensor_DataLogger\\{i}.xlsx')
        #     i = i+1
        #     time.sleep(60)
class CompassWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.direction = 64.5
        self.setFixedSize(100, 100)

    def direction_update(self, angle):
        self.direction = angle
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        center = QPointF(rect.center())
        radius = min(self.width(), self.height()) / 2 - 20

        pen = QPen(Qt.GlobalColor.black, 2)
        painter.setPen(pen)
        painter.drawEllipse(center, radius, radius)

        angle = self.direction 
        needle_length = radius
        end_x = center.x() + needle_length * math.cos(math.radians(angle))
        end_y = center.y() + needle_length * math.sin(math.radians(angle))
        needle_end = QPointF(end_x, end_y)

        pen = QPen(Qt.GlobalColor.red, 3)
        painter.setPen(pen)
        painter.drawLine(center, needle_end)

       
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.drawEllipse(center, 3, 3)

        offset = 5

        # N
        rectN = QRectF(center.x() - radius, center.y() - radius - 20 - offset,
                       2*radius, 20)
        painter.drawText(rectN, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom, "N")

        # S
        rectS = QRectF(center.x() - radius, center.y() + radius + offset,
                       2*radius, 20)
        painter.drawText(rectS, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, "S")

        # E
        rectE = QRectF(center.x() + radius + offset, center.y() - radius,
                       20, 2*radius)
        painter.drawText(rectE, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "E")

        # W
        rectW = QRectF(center.x() - radius - 20 - offset, center.y() - radius,
                       20, 2*radius)
        painter.drawText(rectW, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, "W")


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.compass_widget = CompassWidget()
        
        
        self.setWindowTitle("The Wind Sensor App")
        now = datetime.now()
        self.current_time_str = now.strftime("%I:%M:%S %p")
        folder_path = f"C:\\WindSensor_DataLogger"
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

        #self.serial_start = serial.Serial('COM9', 9600, timeout= 1)
        
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        compass_layout = QVBoxLayout()
    

        compass_layout.addWidget(self.compass_widget)
        compass_layout.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)

        

        map_layout = QVBoxLayout()
        self.web_view = QWebEngineView()
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        map_file = os.path.join(os.path.dirname(__file__), "map.html")
        self.web_view.load(QUrl.fromLocalFile(map_file))
        self.web_view.setFixedSize(450, 650)
        map_layout.addWidget(self.web_view)

        map_widget = QWidget()
        map_widget.setLayout(map_layout)

        self.right_layout = QVBoxLayout()

        button_layout = QVBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        button_layout.addSpacing(5)

        self.start_btn = QPushButton("START", self)
        self.stop_btn = QPushButton("STOP", self)
        more_btn = QPushButton("MORE", self)

        self.start_btn.setFixedSize(120, 50)
        self.stop_btn.setFixedSize(120, 50)
        more_btn.setFixedSize(120, 50)

        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addWidget(more_btn)

        label_layout = QVBoxLayout()
        label_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        label_layout.setSpacing(25)

        time_layout = QVBoxLayout()
        time_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)

        self.status_lbl = QHBoxLayout()
        status = QLabel('STATUS:')

        self.icon_label = QLabel()
        self.pixmap = QPixmap("red.png")
        self.smaller_pixmap = self.pixmap.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
        self.icon_label.setPixmap(self.smaller_pixmap)
        status.setFixedSize(50, 10)

        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        self.status_lbl.addWidget(status)
        self.status_lbl.addWidget(self.icon_label)

        label_dict = {
            'Time_lbl': 'TIME:',
            'speed_lbl': 'SPEED:',
            'direction_lbl': 'DIRECTION:',
            'modes_lbl': 'MODES:',
            'health_lbl': 'HEALTH:',
            'altitude_lbl': 'ALTITUDE:', 
        }

        device_row = QHBoxLayout()
        device_row.setSpacing(20)
        device_lbl = QLabel("DEVICE:")

        real_time_row = QHBoxLayout()
        real_time_lbl = QLabel("TIME OF DAY:")

        real_time_lbl.setFixedSize(80, 20)

        self.real_time_edit = QLabel()
        self.real_time_edit.setFixedSize(70, 20)
        real_time_row.addWidget(real_time_lbl)
        real_time_row.addWidget(self.real_time_edit)

        altitude_row = QHBoxLayout()
        altitude_row.setSpacing(20)

        time_row = QHBoxLayout()
        time_row.setSpacing(20)

        speed_row = QHBoxLayout()
        speed_row.setSpacing(20)

        direction_row = QHBoxLayout()
        direction_row.setSpacing(20)

        modes_row = QHBoxLayout()
        modes_row.setSpacing(20)

        health_row = QHBoxLayout()
        health_row.setSpacing(20)

        self.device_combo = QComboBox()
        self.device_combo.setFixedSize(200, 20)
        self.device_combo.addItems(["Device 1", "Device 2", "Device 3"])

        self.text_box_time = QLineEdit()
        self.text_box_time.setReadOnly(True)
        self.text_box_time.setFixedSize(200, 20)
        self.text_box_time.setPlaceholderText("ERROR")

        self.text_box_speed = QLineEdit()
        self.text_box_speed.setReadOnly(True)
        self.text_box_speed.setFixedSize(200, 20)
        self.text_box_speed.setPlaceholderText("ERROR")

        self.text_box_direcion = QLineEdit()
        self.text_box_direcion.setReadOnly(True)
        self.text_box_direcion.setFixedSize(200, 20)
        self.text_box_direcion.setPlaceholderText("ERROR")

        self.text_box_altitude = QLineEdit()
        self.text_box_altitude.setReadOnly(True)
        self.text_box_altitude.setFixedSize(200, 20)
        self.text_box_altitude.setPlaceholderText("ERROR")

        self.modes_combo = QComboBox()
        self.modes_combo.setFixedSize(200, 20)
        self.modes_combo.addItems(["Real Time", "Time Average"])

        self.text_box_health = QLineEdit()
        self.text_box_health.setReadOnly(True)
        self.text_box_health.setFixedSize(200, 20)
        self.text_box_health.setPlaceholderText("ERROR")

        self.text_box_altitude = QLineEdit()
        self.text_box_altitude.setReadOnly(True)
        self.text_box_altitude.setFixedSize(200, 20)
        self.text_box_altitude.setPlaceholderText("ERROR")

        device_row.addWidget(device_lbl)
        device_row.addWidget(self.device_combo)

        for key, val in label_dict.items():
            label = QLabel(val)
            if val == 'TIME:':
                time_row.addWidget(label)
                time_row.addWidget(self.text_box_time)
            elif val == 'SPEED:':
                speed_row.addWidget(label)
                speed_row.addWidget(self.text_box_speed)
            elif val == "DIRECTION:":
                direction_row.addWidget(label)
                direction_row.addWidget(self.text_box_direcion)
            elif val == "MODES:":
                modes_row.addWidget(label)
                modes_row.addWidget(self.modes_combo)
            elif val == 'HEALTH:':
                health_row.addWidget(label)
                health_row.addWidget(self.text_box_health)
            elif val == 'ALTITUDE:':
                altitude_row.addWidget(label)
                altitude_row.addWidget(self.text_box_altitude)

        label_layout.addLayout(device_row)
        label_layout.addLayout(time_row)
        label_layout.addLayout(speed_row)
        label_layout.addLayout(direction_row)
        label_layout.addLayout(modes_row)
        label_layout.addLayout(health_row)
        label_layout.addLayout(altitude_row)

        # label_layout.addSpacing(-15)
        label_layout.setSpacing(25)

        time_layout.addLayout(real_time_row)
        time_layout.addSpacing(-60)

        self.right_layout.addLayout(self.status_lbl)
        self.right_layout.addLayout(button_layout)
        self.right_layout.addSpacing(20)
        self.right_layout.addLayout(label_layout)
        self.right_layout.addLayout(time_layout)
        self.right_layout.addLayout(compass_layout)

        right_widget = QWidget()
        right_widget.setLayout(self.right_layout)

        main_layout.addWidget(map_widget)
        main_layout.addWidget(right_widget)
    

        self.count = 4

        self.resize(800, 600)

        self.hoverStyleSheet = (
            'QPushButton{background-color: #803dae;color:white;}'
            'QPushButton:hover{background-color: #803dae;color:white;}'
            'QPushButton:pressed{border: 5px solid rgb(135,206,250);}'
            'QToolTip {background-color: black; color: white; border: black solid 1px;}'
        )

        more_btn.setStyleSheet(self.hoverStyleSheet)
        self.stop_btn.setStyleSheet(self.hoverStyleSheet)
        self.start_btn.setStyleSheet(self.hoverStyleSheet)
        self.setStyleSheet("""
            QWidget { background-color: #f1eeee; color: black; }
            QComboBox { border: 1px solid black; }
        """)

        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(0)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time_of_day)
        self.timer.start(1000) 

        more_btn.clicked.connect(self.more_button_functionality)
        self.prevlatitude = None
        self.prevlongitude = None
        self.connection()
        self.start_button_pressed = False
        

    def update_google_map(self, latitude: float, longitude: float):
        if (latitude, longitude) != (self.prevlatitude, self.prevlongitude):
            js_code = f'updateMap({latitude}, {longitude});'
            self.web_view.page().runJavaScript(js_code)

            self.prevlatitude = latitude
            self.prevlongitude = longitude
            

    def find_serial_port(self):
        ports = serial.tools.list_ports.comports()
        target_vid = 4292  
        target_pid = 60000 

        for port in ports:
            if port.vid == target_vid and port.pid == target_pid:
                return port.device 

        return None  

    def start_serial_connection(self):
        com_port = self.find_serial_port()
        if com_port is not None:
            try:
                self.serial_start = serial.Serial(com_port, 9600, timeout=1)
                # print(f"Connected successfully to {com_port}")
            except serial.SerialException as e:
                print(f"Error connecting to {com_port}: {e}")
        else:
            print("Device not found. Please check the connection.")

    

        # self.real_time_edit.setText(self.current_time_str)
        # self.current_time_str = datetime.now().strftime("%I:%M:%S %p")

        # locations = [
        # {'lat': 53.5461, 'lng': -113.4938},
        # {'lat': 53.5400, 'lng': -113.5000},
        # {'lat': 53.5500, 'lng': -113.4800}
        # ]

        # self.update_google_map(locations)
    def connection(self):
        comport = self.find_serial_port()
        if comport:
            self.serial_start = serial.Serial(comport, 9600, timeout=1)
            self.pixmap = QPixmap("green_processed.jpg")
            self.smaller_pixmap = self.pixmap.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
            self.icon_label.setPixmap(self.smaller_pixmap)
        else:
            print('did not work')
            self.pixmap = QPixmap("red.png")
            self.smaller_pixmap = self.pixmap.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
            self.icon_label.setPixmap(self.smaller_pixmap)


    def more_button_functionality(self):
        self.data_logging_window = Datalogger()
        self.data_logging_window.show()
    
    def start_button_clicked(self):
        self.start_button_pressed = True
        
    def stop_button_clicked(self):
        self.start_button_pressed = False
        self.stop_button_pressed = True

    def update_time_of_day(self):
        
        self.real_time_edit.setText(self.current_time_str)
        self.current_time_str = datetime.now().strftime("%I:%M:%S %p")
        

        if self.start_button_pressed:
            line = self.serial_start.readline()
            print(line)
            # if line:
            #     print(line)
            #     text = line.decode('utf-8', errors='replace').strip()
            #     if 'Wind Speed' in text:
            #         lat_index = text.find(":")
            #         latitude = text[lat_index+1:]
            #         self.text_box_speed.setText(latitude)
            #     elif 'Longitude' in text:
            #         latifinal_index = text.find(":")
            #         plus_index = text.find("+")
            #         dollar_index = text.find("$")
            #         latitude_final = text[latifinal_index+1:plus_index-1]
            #         longitude_final = text[dollar_index+1:]
            #         self.update_google_map(float(latitude_final),float(longitude_final))    
            #     elif 'Altitude' in text:
            #         alt_index = text.find(":")
            #         alt = text[alt_index+1:]
            #         self.text_box_altitude.setText(alt)
            #     elif 'Humidity' in text:
            #         humidity_index = text.find("=")
            #         humidity = text[humidity_index+1:]
            #         self.text_box_time.setText(humidity)
            #     elif 'Wind Angle' in text:
            #         print(text)
            #         humidity_index = text.find(":")
            #         humidity = text[humidity_index+1:]
            #         self.compass_widget.direction_update(float(humidity))
            #         self.text_box_direcion.setText(f'{humidity}°')

        comport = self.find_serial_port()
        # print(comport)
        

        if comport == None:
            self.connection()
            self.count = 0
        else:
            # print('connected :)')
            if self.count == 0:
                self.pixmap = QPixmap("green_processed.jpg")
                self.smaller_pixmap = self.pixmap.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio,
                                        Qt.TransformationMode.SmoothTransformation)
                self.icon_label.setPixmap(self.smaller_pixmap)
                self.count = 1
            else:

                self.count = self.count + 1
        
        # if self.count == 1:
        #     self.pixmap = QPixmap("green_processed.jpg")
        #     self.smaller_pixmap = self.pixmap.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio,
        #                                Qt.TransformationMode.SmoothTransformation)
        #     self.icon_label.setPixmap(self.smaller_pixmap)
        #     #self.connection()
    
            
        self.start_btn.clicked.connect(self.start_button_clicked)
        self.stop_btn.clicked.connect(self.stop_button_clicked)
    


       
                    
        
                

                    


def main():
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    app.exec()
    

if __name__ == "__main__":
    main()
