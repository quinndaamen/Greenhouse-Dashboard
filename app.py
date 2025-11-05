import serial
import threading
import time
import sensor_db
from datetime import datetime
from dateutil.parser import parse as parse_date
from flask import Flask, render_template, request, redirect
import user_db

app = Flask(__name__)

aTemp = 0
aHumidity = 0
aLight = 0
score = 0
#----
windowsOpen = False
Heater = False
Humidifier = False
deHumidifier = False

ser = serial.Serial("COM5", 9600, timeout=1)
time.sleep(2)

sensor_db.init_db()
# - main loop that does the calculations and reads the arduinos output
def read_serial():
    global aTemp, aHumidity, aLight, score
    global uTemp, uHumidity
    global windowsOpen, Heater, Humidifier, deHumidifier
    global TempDiaryEntry, HumDiaryEntry
    global HealthColour
    global formatted
    while True:
        try:
            line = ser.readline().decode('utf-8').strip()
            if not line:
                continue

            # Temp:23.7,Hum:36.0,Light:42.6
            parts = line.split(",")
            data = {}
            for part in parts:
                key, value = part.split(":")
                data[key] = value

            aTemp = float(data.get("Temp", aTemp))
            aHumidity = float(data.get("Hum", aHumidity))
            aLight = float(data.get("Light", aLight))

            latest_settings = user_db.get_latest_settings()
            if latest_settings:
                uTemp, uHumidity = latest_settings
            else:
                uTemp = 23
                uHumidity = 75

            sensor_db.insert_sensor_data(aTemp, aHumidity, aLight)

             # Temp score
            if uTemp * 0.9 <= aTemp <= uTemp * 1.1:
                    tempScore = 50
            elif uTemp * 0.875 <= aTemp <= uTemp * 1.2:
                    tempScore = 40
            elif uTemp * 0.85 <= aTemp <= uTemp * 1.3:
                    tempScore = 30
            elif uTemp * 0.825 <= aTemp <= uTemp * 1.4:
                    tempScore = 20
            elif uTemp * 0.8 <= aTemp <= uTemp * 1.5:
                tempScore = 0
            else:
                tempScore = 0

            # Hum score
            if uHumidity * 0.9 <= aHumidity <= uHumidity * 1.1:
                humScore = 50
            elif uHumidity * 0.875 <= aHumidity <= uHumidity * 1.2:
                humScore = 40
            elif uHumidity * 0.85 <= aHumidity <= uHumidity * 1.3:
                humScore = 30
            elif uHumidity * 0.825 <= aHumidity <= uHumidity * 1.4:
                humScore = 20
            elif uHumidity * 0.8 <= aHumidity <= uHumidity * 1.5:
                humScore = 0
            else:
                humScore = 0

            score = tempScore + humScore
            
            #Hum diary
            if uHumidity < aHumidity * 1.15:
                deHumidifier = True
                Humidifier = False
            if aHumidity < uHumidity * 1.15:
                deHumidifier = False
                Humidifier = True
            else:
                deHumidifier = False
                Humidifier = False  

            #Temp diary
            if uTemp < aTemp * 1.15:
                windowsOpen = True
                Heater = False
            if aTemp < uTemp * 1.15:
                Heater = False
                windowsOpen = True
            else:
                Heater = False
                windowsOpen = False  
        
            # Diary entries
            if Heater == True and windowsOpen == False:
                TempDiaryEntry = "I Turned on the heater and closed the windows because it was getting cold"
            if Heater == False and windowsOpen == True:
                TempDiaryEntry = "I Turned off the heater and opened the windows because it is getting hot now"
            else:
                TempDiaryEntry = "It is a great temperature now"
            #
            if Humidifier == True and deHumidifier == False:
                HumDiaryEntry = "And it is getting dry i turned on the Humidifier"
            if Heater == False and windowsOpen == True:
                HumDiaryEntry = "And it is getting humid I will turn on the dehumidifier "
            else:
                HumDiaryEntry = "And it is a great Humdity now"
            
            if score >= 70:
                HealthColour = "008000"  # green
            elif 40 <= score < 70:
                HealthColour = "EAA221"  # orange/yellow
            else:
                HealthColour = "CD1C18"  # red


            current_time = time.localtime()  

            # Format
            formatted = time.strftime("%H:%M", current_time)




            time.sleep(1) 
        except Exception as e:
            print("Error:", e)

threading.Thread(target=read_serial, daemon=True).start()

@app.route("/")
def main():
    return render_template("index.html", aTemp=aTemp, aHumidity=aHumidity, aLight=aLight, score=score, HumDiaryEntry=HumDiaryEntry, TempDiaryEntry=TempDiaryEntry, HealthColour=HealthColour, formatted=formatted)

@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/save-settings", methods=["POST"])
def save_settings():
    uTemp = request.form.get("uTemp", type=float)
    uHumidity = request.form.get("uHum", type=float)
    user_db.save_user_settings(uTemp, uHumidity)
    return redirect("/")  

@app.route("/graph")
def graph():
    raw_data = sensor_db.fetch_sensor_data(200) 
    clean_data_filtered = []
    

    for ts, temp, hum, light in raw_data:
        try:
            temp = float(temp)
            hum = float(hum)
            light = float(light)
            if isinstance(ts, str):
                ts = parse_date(ts)

            if not (0 < temp < 50 and 0 < hum < 100 and 0 < light < 200):
                continue

            clean_data_filtered.append([
                    ts.strftime("%a, %d %b %Y %H:%M:%S"),
                    temp, hum, light
                ])

        except Exception as e:
            print("Bad row:", e)

    return render_template("graph.html", data=clean_data_filtered, uTemp=uTemp, uHumidity=uHumidity)

if __name__ == "__main__":
    app.run(debug=False)
