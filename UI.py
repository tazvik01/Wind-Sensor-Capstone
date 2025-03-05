import sys
from datetime import datetime
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


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("The Wind Sensor App")
        folder_path = "C:\\WindSensor_DataLogger"
        os.mkdir(folder_path)


        self.serial_start = serial.Serial('COM9', 9600, timeout= 1)
        
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        map_layout = QVBoxLayout()
        self.web_view = QWebEngineView()
        self.web_view.load(QUrl("https://maps.google.com"))
        self.web_view.setFixedSize(450, 650)
        map_layout.addWidget(self.web_view)

        map_widget = QWidget()
        map_widget.setLayout(map_layout)

        right_layout = QVBoxLayout()

        button_layout = QVBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        button_layout.addSpacing(-50)

        start_btn = QPushButton("START", self)
        stop_btn = QPushButton("STOP", self)
        more_btn = QPushButton("MORE", self)

        start_btn.setFixedSize(120, 50)
        stop_btn.setFixedSize(120, 50)
        more_btn.setFixedSize(120, 50)

        button_layout.addWidget(start_btn)
        button_layout.addWidget(stop_btn)
        button_layout.addWidget(more_btn)

        label_layout = QVBoxLayout()
        label_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        label_layout.setSpacing(25)

        time_layout = QVBoxLayout()
        time_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)

        status_lbl = QHBoxLayout()
        status = QLabel('STATUS:')

        icon_label = QLabel()
        pixmap = QPixmap("green_processed.jpg")
        smaller_pixmap = pixmap.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
        icon_label.setPixmap(smaller_pixmap)
        status.setFixedSize(50, 10)

        status_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        status_lbl.addWidget(status)
        status_lbl.addWidget(icon_label)

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

        time_layout.addLayout(real_time_row)

        right_layout.addLayout(status_lbl)
        right_layout.addLayout(button_layout)
        right_layout.addLayout(label_layout)
        right_layout.addLayout(time_layout)

        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        main_layout.addWidget(map_widget)
        main_layout.addWidget(right_widget)

        self.resize(800, 600)

        self.hoverStyleSheet = (
            'QPushButton{background-color: #803dae;color:white;}'
            'QPushButton:hover{background-color: #803dae;color:white;}'
            'QPushButton:pressed{border: 5px solid rgb(135,206,250);}'
            'QToolTip {background-color: black; color: white; border: black solid 1px;}'
        )

        more_btn.setStyleSheet(self.hoverStyleSheet)
        stop_btn.setStyleSheet(self.hoverStyleSheet)
        start_btn.setStyleSheet(self.hoverStyleSheet)
        self.setStyleSheet("""
            QWidget { background-color: #f1eeee; color: black; }
            QComboBox { border: 1px solid black; }
        """)

        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time_of_day)
        self.timer.start(1000) 

        more_btn.clicked.connect(self.more_button_functionality)

    def more_button_functionality(self):
        self.data_logging_window = Datalogger()
        self.data_logging_window.show()

    def update_time_of_day(self):
        now = datetime.now()
        current_time_str = now.strftime("%I:%M:%S %p")
        self.real_time_edit.setText(current_time_str)

        line = self.serial_start.readline()
        if line:
            text = line.decode('utf-8', errors='replace').strip()
            if 'Temperature' in text:
                lat_index = text.find("=")
                latitude = text[lat_index+1:]
                self.text_box_speed.setText(latitude)
                self.text_box_direcion.setText(latitude)
            elif 'Pressure' in text:
                long_index = text.find("=")
                longitude = text[long_index+1:]
                self.text_box_health.setText(longitude)
            elif 'Altitude' in text:
                alt_index = text.find("=")
                altitude = text[alt_index+1:]
                self.text_box_altitude.setText(altitude)
            elif 'Humidity' in text:
                humidity_index = text.find("=")
                humidity = text[humidity_index+1:]
                self.text_box_time.setText(humidity)
            elif 'Humidity' in text:
                humidity_index = text.find("=")
                humidity = text[humidity_index+1:]
                self.text_box_direcion.setText(humidity)

def main():
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    app.exec()
    

if __name__ == "__main__":
    main()
