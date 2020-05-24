import serial
import re
import time
from msvcrt import getch

# user parameters - please adjust this block to your settings
############################################################################
serialPort = 'COM5'     # the serial port name to the Printer
papertickness = 0.1     # the thickness of the messure object e.g. 0.1mm for paper
serialBaud = 250000     # the baudrate of the serial port
headUp = True           # head up bed and extruder before adjust
extruderTemp = 205     # the target temperature of the extruder
bedTemp = 60           # the target bed temperature
xoffset = 70           # the x offset between extruder and the probe
yoffset = 0           # the x offset between extruder and the probe
debugMode = False       # print more infos
simMode = False         # dont store any values
############################################################################

KEY_ENTER = 13
KEY_ESC = 27
KEY_UP = 65352
KEY_DOWN = 65360
KEY_LEFT = 65355
KEY_RIGHT = 65357

def writeReadSerial(ser, cmd):
    cmd = cmd + "\r\n"
    ser.write(cmd.encode("utf-8"))
    result = ""
    while True:
        response = ser.readline().decode("utf-8")
        if debugMode:
            print(response)
        if len(response) == 0:
            continue
        if response == "ok\n":
            break
        result+=response   
    return result

def waitKey():    
    while True:
        key = ord(getch())
        if key != 224: #ESC
            return key
        else: #Special keys (arrows, f keys, ins, del, etc.)
            key = ord(getch())            
            return 0xFF00|key

def inc(arr):
    arr[0] = arr[0]+1
    return arr[0]

def adjustZ():
    with serial.Serial(serialPort, serialBaud, timeout=1) as ser:  
        print("connecting to printer...")
        time.sleep(4)
        initbuffer = ser.readall();
        if debugMode:
            print(initbuffer)

        step = [0]
        oldOffset = writeReadSerial(ser,"M851")
        regex = r"echo:Probe Z Offset: (-?[\d\.]+)"
        m = re.findall(regex, oldOffset)
        if len(m) == 0:
            return
        oldOffset = float(m[0])
        print("%d. current Z Offset: Z%.2f" % (inc(step),oldOffset))


        if headUp:
            print("%d. set and wait for temperature E0:%dC Bed:%dC ..." % (inc(step),extruderTemp,bedTemp))
            writeReadSerial(ser,"M140 S%d" % bedTemp)
            writeReadSerial(ser,"M104 T0 S%d" % extruderTemp)
            # Warte bis Temperatur erreicht wurde
            writeReadSerial(ser,"M190 R%d" % bedTemp)
            writeReadSerial(ser,"M109 T0 R%d" % extruderTemp)

        print("%d. auto home XYZ" % inc(step))
        writeReadSerial(ser,"G28")

        if xoffset > 0:
            print("%d. compensate X offset" % inc(step))
            writeReadSerial(ser,"G0 X%d" % xoffset)

        if yoffset > 0:
            print("%d. compensate Y offset" % inc(step))
            writeReadSerial(ser,"G0 Y%d" % yoffset)

        print("%d. move Noozle down to Z1" % inc(step))
        writeReadSerial(ser,"G0 Z1")

        print("%d. Turn Software Endstops Off" % inc(step))
        writeReadSerial(ser,"M211 S0")


        print("Put a sheet of paper under the Noozle and change the height with the cursor keys until the Noozle scratches the paper")
        print("Cursor Keys - Left 0.01mm, Up 0.1mm\tRight -0.01mm, Down -0.1mm")
        print("Press Enter to accept the new value")
        currentZ = 1.0
        cancel = True
        while True:
            key = waitKey()
            if key == KEY_ENTER:
                cancel = False
                break
            if key == KEY_ESC:
                break
            elif key == KEY_UP:
                currentZ-=0.1
            elif key == KEY_LEFT:
                currentZ-=0.01
            elif key == KEY_DOWN:
                currentZ+=0.1
            elif key == KEY_RIGHT:
                currentZ+=0.01
            else:
                continue

            currentZ = round(currentZ,2)
            cancel = (currentZ == 0.0)
            print("current Z Offset: Z%.2f" % (oldOffset + currentZ - papertickness))
            writeReadSerial(ser,"G0 Z%.2f" % currentZ)
    
        print("%d. lift Noozle" % inc(step))
        writeReadSerial(ser,"G0 Z1")
        time.sleep(1)

        print("%d. Turn Software Endstops On" % inc(step))
        writeReadSerial(ser,"M211 S1")

        if not cancel:
            print("%d. set new Z Offset: Z%.2f" % (inc(step), oldOffset + currentZ - papertickness))
            if not simMode:
                writeReadSerial(ser,"M851 Z%.2f" % (oldOffset + currentZ - papertickness))
                writeReadSerial(ser,"M500")
                time.sleep(1)
                        
adjustZ()