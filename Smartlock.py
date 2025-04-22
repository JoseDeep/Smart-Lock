import network
import time
from machine import Pin, I2C, PWM
import socket
import ure
from lcd_api import LcdApi
from i2c_lcd import I2cLcd

servo = PWM(Pin(13), freq=50)
def unlock():
    servo.duty(77)
def lock():
    servo.duty(40)
lock()

i2c = I2C(0, scl=Pin(33), sda=Pin(27), freq=400000)
lcd = I2cLcd(i2c, 0x27, 2, 16)
lcd.putstr("Smart Lock Ready")

ssid = "Airtel_9840985870"
password = "Sunflower@4674"

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

lcd.move_to(0, 1)
lcd.putstr("Connecting...")
print("Connecting to WiFi...")
while not station.isconnected():
    time.sleep(1)

ip = station.ifconfig()[0]
print("\n✅ Connected with IP:", ip)
lcd.clear()
lcd.putstr("WiFi Connected")
lcd.move_to(0, 1)
lcd.putstr(ip)

users = {
    "Alice": "1234",
    "Bob": "5678",
    "Charlie": "4321"
}

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
server = socket.socket()
server.bind(addr)
server.listen(1)
print("🌐 Web server running...")

def handle_request(conn):
    request = conn.recv(1024).decode("utf-8")
    print("🔍 Request received:\n", request)

    match = ure.search("GET /login\\?username=([^&]*)&password=([^ ]*)", request)
    
    response = ""
    headers = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n"

    if match:
        username = match.group(1)
        password = match.group(2)
        print(f"🧾 Login: {username} / {password}")

        if username in users and users[username] == password:
            print("✅ Access Granted")
            lcd.clear()
            lcd.putstr("Access Granted")
            lcd.move_to(0, 1)
            lcd.putstr("Door Opened")
            unlock()
            time.sleep(5)
            lock()
            response = '{"status":"success","message":"Access Granted"}'
        else:
            print("❌ Access Denied")
            lcd.clear()
            lcd.putstr("Access Denied")
            lcd.move_to(0, 1)
            lcd.putstr("Door Locked")
            response = '{"status":"failed","message":"Access Denied"}'
    else:
        response = '{"status":"error","message":"Invalid Request"}'

    conn.send(headers)
    conn.sendall(response)
    conn.close()

while True:
    conn, addr = server.accept()
    print("📥 Connection from", addr)
    handle_request(conn)
