import subprocess
import serial
import time

print('hi')
ino_path = "C:\\Users\\tazvi\\Documents\\Capstone_UI\\Basestation\\Basestation.ino"

board_type = 'esp32:esp32:esp32'

serial_port = 'COM8' 

baud_rate = 9600

compile_result = subprocess.run([
    'arduino-cli', 'compile', '--fqbn', board_type, ino_path
])

if compile_result.returncode != 0:
    print("Compilation failed.")
    exit(1)

upload_result = subprocess.run([
    'arduino-cli', 'upload', '-p', serial_port, '--fqbn', board_type, ino_path
])

if upload_result.returncode != 0:
    print("Upload failed.")
    exit(1)

print("Upload successful! Starting serial communication.")

ser = serial.Serial(serial_port, baud_rate, timeout=1)

time.sleep(3)
