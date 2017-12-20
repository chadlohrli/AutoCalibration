from __future__ import print_function
import serial
import sys
import glob
import httplib2
import os
import pkg_resources

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import time
from time import gmtime, strftime, localtime


serial_port_0 = "/dev/cu.usbmodem40111"
serial_port_1 = "/dev/cu.usbmodem40121"
serial_port_2 = "/dev/cu.usbmodem40131"
serial_port_3 = "/dev/cu.usbmodem1411" #heating/cooling port
portArray = [serial_port_0,serial_port_1,serial_port_2]

baud_rate = 9600

#global params
boxNumber = 0
fileName = ""
maxReads = 15
readTemp = 20.5

#debugging
DEBUG = False
DEBUG_SHEETS = False

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = ''
APPLICATION_NAME = ''

# ------------------------------------------------------------------------------

# A list of all available serial ports
def serial_ports():
    """ Lists serial port names
        
        :raises EnvironmentError:
        On unsupported or unknown platforms
        :returns:
        A list of the serial ports available on the system
        """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')
    
    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

# ------------------------------------------------------------------------------

def readWrite():
    global fileName
    global boxNumber
    
    # Ask for port and box

    # print("\nAvailable ports: \n")

    # for port in serial_ports():
    #     print(port)

    # port = raw_input("\nPlease enter the last digits of your serial port (i.e /dev/cu.usbmodem[1441]) ");
    # serial_port = "" + port;

    box = raw_input("\nPlease enter the box you are reading from [0,1,2] ");
    boxNumber = int(box);

    if(DEBUG):
        return

    if boxNumber == 0:
        serial_port = serial_port_0
    elif boxNumber == 1:
        serial_port = serial_port_1
    elif boxNumber == 2:
        serial_port = serial_port_2  
        
        

    print(serial_port + "\n");
    ser = serial.Serial(serial_port, baud_rate);
    
    #try to fix serial port issue
    #this works, we set sensors high here instead of a seperate method
    time.sleep(2.5)
    ser.write(str("1")) 
    
    box = "box" + str(boxNumber);
    fileName = box + ".txt"
    write_to_file_path = fileName;

    # ------------------------------------------------------------------------------

    # Save output to file

    output_file = open(write_to_file_path, "w+");

    print("Please make sure the sensor is turned on");
    raw_input("Press Enter to continue...");
    print("\n")

    curr = 0

    while True:
        line = ser.readline();
        line = line.decode("utf-8"); #ser.readline returns a binary, convert to string
        if "ADC:" in line:
            dataArray = []
            for i in xrange(5):
                print(line);
                dataArray.append(line)
                line = ser.readline();
                
            curr = curr + 1
            if curr == maxReads:
                break;
                
    for data in dataArray:
        output_file.write(data);


    output_file.close();

    try:
        import argparse
        flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
    except ImportError:
        flags = None

# ------------------------------------------------------------------------------

def printData(f):
  # formatted data
  
    print("\n---------------------------")
    print(f.readline())
    print(f.readline())
    print(f.readline())
    print(f.readline())
    print(f.readline())  
    print(f.readline())     
    print("---------------------------")

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


# Upload data to Google Drive
def uploadToSheets(log):
    global fileName
    global boxNumber
    
    # api overhead
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)
    service = discovery.build('sheets', 'v4', credentials=credentials)
    # The ID of the spreadsheet to update.
    spreadsheet_id = ''
    # How the input data should be interpreted.
    value_input_option = 'USER_ENTERED'  
    # How the input data should be inserted.
    insert_data_option = 'INSERT_ROWS' 


    if(log == "S"):

        #set already created file for debug
        if(DEBUG_SHEETS):
            fileName = "box0.txt"

        print(fileName)
        dataFile = open(fileName,'r')
    
        if boxNumber == 0:
            rangeName = 'Box 1!A2:E'
            #rangeName = 'Heat/Cool!A1:E'
            #rangeName = 'Box 4 - Development!B2:I'
            dataFile = open('box0.txt','r')
        elif boxNumber == 1:
            rangeName = 'Box 2!A2:E'
            #rangeName = 'Box 4 - Development!B2:I'
            dataFile = open('box1.txt','r')
        elif boxNumber == 2:
            rangeName = 'Box 3!A2:E'
            #rangeName = 'Box 4 - Development!B2:I'
            dataFile = open('box2.txt','r')
        else:
            rangeName = 'Box 4!B2:I'
            print("please enter a valid index")

        # The A1 notation of a range to search for a logical table of data.
        # Values will be appended after the last row of the table.
        range_ = rangeName 
        
        printData(open(fileName,'r'))
        
        print('Press enter to upload the data above to the Drive for box index ' + str(boxNumber) + '...')
        
        x = raw_input()
        
        lines = dataFile.readlines()
        data = [
            (lines[0])[5:-2], # Sensor ADC
            (lines[1])[9:-2], # Sensor Voltage
            (lines[2])[12:-2], # Sensor Resistance

            (lines[3])[13:-4], # Sensor Temperature
            
            (lines[4])[13:-2], # Sensor Temperature
            ]

        value_range_body = {
            "range": rangeName,
            "majorDimension": 'ROWS',
            "values": [[strftime("%m/%d/%Y %I:%M %p", localtime()), data[0], data[1], 
            data[2], data[4], data[3]]]  
        }
    
    else:
        # Updates heating and cooling times to sheets
        rangeName ='Heat/Cool!A2:E'
        range_ = rangeName

    if(log == "H"):
        value_range_body = {
        "range": rangeName,
        "majorDimension": 'ROWS',
        "values": [["Heating: ", strftime("%m/%d/%Y %I:%M %p", localtime())]]
        }
    elif(log == "C"):
        value_range_body = {
        "range": rangeName,
        "majorDimension": 'ROWS',
        "values": [["Cooling: ", strftime("%m/%d/%Y %I:%M %p", localtime())]]
        }

    elif(log == "O"):
        value_range_body = {
        "range": rangeName,
        "majorDimension": 'ROWS',
        "values": [["Off: ", strftime("%m/%d/%Y %I:%M %p", localtime())]]
        }
   

    request = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=range_, valueInputOption=value_input_option, insertDataOption=insert_data_option, body=value_range_body)
    response = request.execute()
    
    print("Done!")


# ----------------Command Functions--------------

#def HCO(state):
    #ser = serial.Serial(serial_port_3, baud_rate);
    #time.sleep(2.5)
    #ser.write(state)
    #uploadToSheets(state)

def heating():

    if(not DEBUG):
        ser = serial.Serial(serial_port_3, baud_rate);
        time.sleep(2.5)
        ser.write("0")
        uploadToSheets("H")
    else:
        print("heating..")
        if(DEBUG_SHEETS):
            uploadToSheets("H")

def cooling():

    if(not DEBUG):
        ser = serial.Serial(serial_port_3, baud_rate);
        time.sleep(2.5)
        ser.write("1")
        uploadToSheets("C")
    else:
        print("cooling..")
        if(DEBUG_SHEETS):
            uploadToSheets("C")


def off():

    if(not DEBUG):
        ser = serial.Serial(serial_port_3, baud_rate);
        time.sleep(2.5)
        ser.write("2")
        uploadToSheets("O")
    else:
        print("off..")
        if(DEBUG_SHEETS):
            uploadToSheets("O")


def sensorState(state):
    
    if(not DEBUG):
        for i in range(len(portArray)):
            ser = serial.Serial(portArray[i], baud_rate);
            time.sleep(2.5)
            ser.write(str(state))
            print(portArray[i])
    else:
        print(state)
        print("changed sensor state to: ",state)

def checkTemps():

    if(not DEBUG):
        while True:
            if (is_in_range(serial_port_0,0) and is_in_range(serial_port_1,1) and is_in_range(serial_port_2,2)):
                break;
    
            print("continue")
            time.sleep(5);
    else:
        print("checking temps")


# -----------------------------------------------

# checkTemps() helper function
def is_in_range(port,boxNum):
    
    ser = serial.Serial(port, baud_rate)
    
    while True:
        line = ser.readline();
        line = line.decode("utf-8") #ser.readline returns a binary, convert to string
            
        # If string starts with temperature
        if (line[:12] == "Temperature:"):
            print('BoxNumber: ' + str(boxNum) + ' | '  + str(line));
            # Upper bound of temperature
            if (float(line[13:-4]) <= readTemp):
                return True            

def main():

    # --------Command List------------------------
    #  [H]eat : turn on lamps, turns off fans
    #  [C]ool : turn on fans, turns off lamps
    #  [O]ff  : turn off lamps + fans
    #  
    #  [SH]   : sensors high[on] (custom + theta)
    #  [SL]   : sensors low[off] ' '
    #
    #  [T]emp : check temperatures 
    # --------------------------------------------
    
    command = ""

    if len(sys.argv) == 2:
        command = sys.argv[1]
        print(command)

    if command == "H":
        heating()
        return
    elif command == "C":
        cooling()
        return
    elif command == "O":
        off()
        return
    elif command == "SH":
        sensorState("1")
        return
    elif command == "SL":
        sensorState("0")
        return
    elif command == "T":
        checkTemps()
        return

    #if no command specified, run data collection
    if(not DEBUG):
        readWrite()
        uploadToSheets("S")
    else:
        print("collecting data...")
        readWrite()
        if(DEBUG_SHEETS):
            uploadToSheets("S")


if __name__ == '__main__':
    main()
