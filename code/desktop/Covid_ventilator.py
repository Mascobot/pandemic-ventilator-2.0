import serial
import serial.tools.list_ports
from queue import Queue
import re
import threading 
import time
import simpleaudio as sa
import tk_tools
try:
    import Tkinter as tk
except:
    import tkinter as tk
from twilio.rest import Client

## Global variables
dict_data = {'PressureA':0, 'ERP1':0, 'ERP2':0, 'PressureB':0, 'PressureC':0, 'Flow':0, 'Power':0}
indicator = 0
slider_volume = 0
slider_bpm = 12
slider_o = 21
slider_ratio = 1
slider_alarm = 30
bat_in = 0
tank_in = 0

def get_port():
    ports = serial.tools.list_ports.comports()
    for i in ports:
        i = str(i)
        if 'Arduino' in i:     
            return (i.split()[0])
            
def open_serial():
    baudrate = 9600     
    timeout = 5   
    port = get_port()
    if port == None:
        return None
    else:
        ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
        if (not ser.is_open):
            ser.open()
        return ser

def play_audio(filename):
    filename = 'audio/' + filename
    wave_obj = sa.WaveObject.from_wave_file(filename)
    wave_obj.play()

def play_changed_data(change='', value=0, unit=None):
    filename = 'audio/' + change + '.wav'
    wave_obj = sa.WaveObject.from_wave_file(filename)
    play_obj = wave_obj.play()
    play_obj.wait_done()
    filename = 'audio/' + str(value) + '.wav'
    wave_obj = sa.WaveObject.from_wave_file(filename)
    play_obj = wave_obj.play()
    play_obj.wait_done()
    if unit != None:
        filename = 'audio/' + str(unit) + '.wav'
        wave_obj = sa.WaveObject.from_wave_file(filename)
        play_obj = wave_obj.play()
        play_obj.wait_done()
    else: pass

def send_sms(sms_body='', to_number='+TO_YOUR_NUMBER'):
    account_sid = 'YOUR_TWILIO_SID'
    auth_token = 'YOUR_TOKEN'
    client = Client(account_sid, auth_token)
    client.messages.create(body=sms_body,from_='+FROM_YOUR_TWILIO_NUMBER',to=to_number)

def get_serial_data():
    global dict_data, indicator
    if indicator == 0:
        serial = open_serial()
        q = Queue(maxsize=2)
        indicator = 1

    if serial == None:
        print ('USB board connection not detected')
    else:
        erp1 = 0
        erp2 = 0
        pressure_a = 0
        pressure_b = 0
        pressure_c = 0
        flow = 0
        power = 0

        while (Application.is_running): 
            if serial.inWaiting():#Wait for any serial data comes and if it comes, execute statement.
                #usbdata = serial.read(serial.inWaiting())#Save incoming data in variable 
                usbdata = serial.read(60)#Save incoming data in variable 
                usbdata = str(usbdata)
                indice = 0
                for i in usbdata:
                    try:
                        if i == "O":#EPR1
                            if len(usbdata[indice:indice+6])>=6:
                                erp1 = int(re.findall(r'\d+', usbdata[indice+2:indice+6])[0])     
                        elif i == "T":#EPR2
                            if len(usbdata[indice:indice+6])>=6:
                                erp2 = int(re.findall(r'\d+', usbdata[indice+2:indice+6])[0])    
                        elif i == "A":#Pressure sensor A
                            if len(usbdata[indice:indice+6])>=6:
                                pressure_a = int(re.findall(r'\d+', usbdata[indice+2:indice+6])[0]) 
                        elif i == "B":#Pressure sensor B
                            if len(usbdata[indice:indice+6])>=6:
                                pressure_b = int(re.findall(r'\d+', usbdata[indice+2:indice+6])[0]) 
                        elif i == "C":#Pressure sensor C
                            if len(usbdata[indice:indice+6])>=6:
                                pressure_c = int(re.findall(r'\d+', usbdata[indice+2:indice+6])[0]) 
                        elif i == "F":#Flow sensor
                            if len(usbdata[indice:indice+6])>=6:
                                flow = int(re.findall(r'\d+', usbdata[indice+2:indice+6])[0])   
                        elif i == "P":#Power monitoring
                            if len(usbdata[indice:indice+6])>=6:
                                power = int(re.findall(r'\d+', usbdata[indice+2:indice+6])[0]) 
                    except: 
                        pass
                    indice += 1
                dict_data = {'PressureA':pressure_a, 'ERP1':erp1, 'ERP2':erp2, 'PressureB':pressure_b, 'PressureC':pressure_c, 'Flow':flow, 'Power':power}
                print (dict_data) 
                   
class Application(tk.Tk):
    global dict_data
    t1 = threading.Thread(target=get_serial_data, name='t1') 
    t1.start()
    is_running = True
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry("1400x600")
        self.create_widgets()

    def create_widgets(self):
        self.tank_pressure_label = tk.Label(self, font='TimesNewRoman 14', text="Tank pressure:")
        self.tank_pressure_label.grid(row = 30, column = 2, )
        
        self.tank_pressure_data = tk.Text(self, wrap='word', font='TimesNewRoman 14',bg=self.cget('bg'), relief='flat', width=5, height=1)
        self.tank_pressure_data.grid(row = 30, column = 3, )

        self.input_pressure_label = tk.Label(self, font='TimesNewRoman 14', text="Inlet pressure:")
        self.input_pressure_label.grid(row = 31, column = 2, )
        
        self.input_pressure_data = tk.Text(self, wrap='word', font='TimesNewRoman 14',bg=self.cget('bg'), relief='flat', width=5, height=1)
        self.input_pressure_data.grid(row = 31, column = 3, )

        self.air_pressure_label = tk.Label(self, font='TimesNewRoman 14', text="Air pressure:")
        self.air_pressure_label.grid(row = 32, column = 2, )

        self.air_pressure_data = tk.Text(self, wrap='word', font='TimesNewRoman 14',bg=self.cget('bg'), relief='flat', width=5, height=1)
        self.air_pressure_data.grid(row = 32, column = 3,)

        self.oxygen_pressure_label = tk.Label(self, font='TimesNewRoman 14', text="Oxygen pressure:")
        self.oxygen_pressure_label.grid(row = 33, column = 2,)

        self.oxygen_pressure_data = tk.Text(self, wrap='word', font='TimesNewRoman 14',bg=self.cget('bg'), relief='flat', width=5, height=1)
        self.oxygen_pressure_data.grid(row = 33, column = 3, )

        self.breathing_pressure_label = tk.Label(self, font='TimesNewRoman 14', text="Breathing pressure:")
        self.breathing_pressure_label.grid(row = 34, column = 2, )

        self.breathing_pressure_data = tk.Text(self, wrap='word', font='TimesNewRoman 14',bg=self.cget('bg'), relief='flat', width=5, height=1)
        self.breathing_pressure_data.grid(row = 34, column = 3,)

        self.flow_label= tk.Label(self, font='TimesNewRoman 14', text="Flow:")
        self.flow_label.grid(row = 35, column = 2,)

        self.flow_data = tk.Text(self, wrap='word', font='TimesNewRoman 14',bg=self.cget('bg'), relief='flat', width=5, height=1)
        self.flow_data.grid(row = 35, column = 3, )

        self.led = tk_tools.Led(self, size=50)
        self.led.grid(row = 37, column = 2, )
        self.led.to_red()
        
        self.led_data = tk.Text(self, wrap='word', font='TimesNewRoman 14',bg=self.cget('bg'), relief='flat', width=20, height=1)
        self.led_data.grid(row = 36, column = 2,)

        self.gauge_tank = tk_tools.Gauge(self, max_value=150.0, label='Pressure', unit='PSI', bg='white')
        self.gauge_tank.grid(row = 31, column = 4)
        self.tank_label= tk.Label(self, font='TimesNewRoman 14', text="Tank Pressure")
        self.tank_label.grid(row = 32, column = 4)

        self.gauge_air = tk_tools.Gauge(self, max_value=1024.0, label='Pressure', unit='cmH2O',bg='white')
        self.gauge_air.grid(row = 31, column = 5)
        self.air_label= tk.Label(self, font='TimesNewRoman 14', text="Air Pressure")
        self.air_label.grid(row = 32, column = 5)

        self.gauge_oxygen = tk_tools.Gauge(self, max_value=1024.0, label='Pressure', unit='cmH2O',bg='white')
        self.gauge_oxygen.grid(row = 31, column = 6)
        self.oxygen_label= tk.Label(self, font='TimesNewRoman 14', text="Oxygen Pressure")
        self.oxygen_label.grid(row = 32, column = 6)

        self.gauge_breath = tk_tools.Gauge(self, max_value=1024.0, label='Pressure', unit='cmH2O',bg='white')
        self.gauge_breath.grid(row = 31, column = 7)
        self.breath_label= tk.Label(self, font='TimesNewRoman 14', text="Breath Pressure")
        self.breath_label.grid(row = 32, column = 7)
        
        self.slider_volume = tk.Scale(self, from_=255, to=0,length=300, resolution =1, troughcolor='blue', fg='red', label='Volume (ml)', width=35)
        self.slider_volume.set(0)
        self.slider_volume.grid(row = 35, column = 4,)

        self.slider_bpm = tk.Scale(self, from_=30, to=5,length=300, resolution =1, troughcolor='blue', fg='red', label='BPM', width=35)
        self.slider_bpm.set(12)
        self.slider_bpm.grid(row = 35, column = 5,)

        self.slider_o = tk.Scale(self, from_=100, to=1,length=300, resolution =1, troughcolor='blue', fg='red', label='Oxygen (%)', width=35)
        self.slider_o.set(21)
        self.slider_o.grid(row = 35, column = 6,)   

        self.slider_ratio = tk.Scale(self, from_=3, to=1,length=300, resolution = 1, troughcolor='blue', fg='red', label='I:E Ratio', width=35)
        self.slider_ratio.set(1)
        self.slider_ratio.grid(row = 35, column = 7,)

        self.slider_alarm = tk.Scale(self, from_=50, to=10,length=300, resolution =  1, troughcolor='blue', fg='red', label='Presure Alarm', width=35)
        self.slider_alarm.set(30)
        self.slider_alarm.grid(row = 35, column = 8,)     

        self.send_button = tk.Button(self, text ="Start with selected parameters", command = self.send_data, height = 2, width = 25, fg='black') 
        self.send_button.grid(row = 37, column = 6)
                
        self.t2 = threading.Thread(target=self.populate_data, name='t2') 
        self.t2.start()
    
    def send_data(self):
        global slider_volume, slider_bpm, slider_o, slider_ratio, slider_alarm
        senf = 20
        serial = open_serial()
        for i in range(senf):
            if slider_volume != self.slider_volume.get():
                dat_to_ar = 'v' + str(self.slider_volume.get()) + "\n"
                serial.write(dat_to_ar.encode())
                play_changed_data(change='volume', value=str(self.slider_volume.get()))
                slider_volume = self.slider_volume.get()
            
            if slider_bpm != self.slider_bpm.get():
                dat_to_ar = 'b' + str(self.slider_bpm.get()) + "\n"
                serial.write(dat_to_ar.encode())
                play_changed_data(change='bpm', value=str(self.slider_bpm.get()))
                slider_bpm = self.slider_bpm.get()
            
            
            if slider_o != self.slider_o.get():
                dat_to_ar = 'o' + str(self.slider_o.get()) + "\n"
                serial.write(dat_to_ar.encode())
                play_changed_data(change='oxygenpercentage', value=str(self.slider_o.get()))
                slider_o = self.slider_o.get()
            
            if slider_ratio != self.slider_ratio.get():            
                dat_to_ar = 'r' + str(self.slider_ratio.get()) + "\n"
                serial.write(dat_to_ar.encode())
                play_changed_data(change='ratio', value=str(self.slider_ratio.get()))
                slider_ratio = self.slider_ratio.get()
            
            if slider_alarm != self.slider_alarm.get():
                dat_to_ar = 'a' + str(self.slider_alarm.get()) + "\n"
                serial.write(dat_to_ar.encode())
                slider_alarm = self.slider_alarm.get()
            
            i += 1     
        
    def close_window(self):
        self.t1.join()
        self.t2.join()
        self.is_running = False
        print ('Closing window')
        self.destroy()
            
    def populate_data(self):
        global bat_in, tank_in
        while (self.is_running):
                        
            self.gauge_tank.set_value(int(dict_data['PressureA']))
            if int(dict_data['PressureA']) > 0 and tank_in == 0:
                #play_changed_data(change='tankpressure', value=dict_data['PressureA'])
                #send_sms(sms_body='Almost no pressure on Tank of ventilator number 2: ' + str(dict_data['PressureA']) + 'PSI.')
                tank_in = 1
            elif 20 < int(dict_data['PressureA']) < 35 and tank_in == 1:
                #play_changed_data(change='tankpressure', value= dict_data['PressureA'])
                #send_sms(sms_body='Low pressure on Tank: ' + str(dict_data['PressureA']) + 'PSI')
                tank_in = 2
            elif 40 < int(dict_data['PressureA']) < 55 and tank_in == 2:
                #play_changed_data(change='tankpressure', value= dict_data['PressureA'])
                tank_in = 1
            elif 65 < int(dict_data['PressureA']) < 85 and tank_in == 1:
                #play_changed_data(change='tankpressure', value= dict_data['PressureA'])
                tank_in = 2
            elif int(dict_data['PressureA']) > 90 and tank_in == 2:
                #play_changed_data(change='tankpressure', value= dict_data['PressureA'])
                tank_in = 1

            if 100 < int(dict_data['Power']) < 750:
                if bat_in == 0:
                    #play_audio('battery.wav')
                    #send_sms(sms_body='AC Power has been interrupted on ventilator number 2. It has automatically switched power to its battery.')
                    bat_in = 1
                else: pass
                self.led_data.insert('end', "RUNNING ON BATTERY")
                self.led.to_red(on=True)
            elif int(dict_data['Power'])>800 :
                bat_in = 0
                self.led_data.insert('end', "Runing on AC Power")
                self.led.to_green(on=True)

            self.gauge_air.set_value(int(dict_data['ERP1']))
            self.gauge_oxygen.set_value(int(dict_data['ERP2']))
            self.gauge_breath.set_value(int(dict_data['PressureC']))

            self.tank_pressure_data.insert('end', str(dict_data['PressureA']))# Tank pressure - Sensor A
            self.input_pressure_data.insert('end', str(dict_data['PressureB']))# Input pressure - Sensor B 
            self.air_pressure_data.insert('end', str(dict_data['ERP1']))# Air pressure EPR1 Pressure
            self.oxygen_pressure_data.insert('end', str(dict_data['ERP2']))# Oxygen pressure - EPR2 pressure
            self.breathing_pressure_data.insert('end', str(dict_data['PressureC']))# Breathing pressure - Sensor C
            self.flow_data.insert('end', str(dict_data['Flow']))# Flow
            time.sleep(1/6)
            self.tank_pressure_data.delete(1.0, 'end')    
            self.input_pressure_data.delete(1.0, 'end')   
            self.air_pressure_data.delete(1.0, 'end') 
            self.oxygen_pressure_data.delete(1.0, 'end')     
            self.breathing_pressure_data.delete(1.0, 'end')       
            self.flow_data.delete(1.0, 'end')   
            self.led_data.delete(1.0, 'end')   

application = Application()
application.title("Covilator | By Marco Mascorro")
application.mainloop()

                        
