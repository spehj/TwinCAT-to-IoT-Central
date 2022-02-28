import pyads
from time import sleep
from timer import Timer
from multiprocessing import Process
from dotenv import load_dotenv 
from azure.iot.device.aio import IoTHubDeviceClient, ProvisioningDeviceClient
from azure.iot.device import MethodResponse 
import os, asyncio, json 


# Get connection secrets from .end file
load_dotenv()
id_scope = os.getenv('ID_SCOPE')
device_id = os.getenv('DEVICE_ID')
primary_key = os.getenv('PRIMARY_KEY')


try:

    # ADS connection
    # ADS address Raspberry Pi
    SENDER_AMS = '192.168.1.120.1.1'
    # Local IP address of TwinCAT device  
    #PLC_IP = '192.168.1.88'
    PLC_IP = '192.168.1.112'
    # Username for TwinCAT device            
    USERNAME = ''
    # Password for TwinCAT device                      
    PASSWORD = ''
    # Local IP of Raspberry Pi                        
    ROUTE_NAME = '192.168.1.120'
    # Raspberry Pi name         
    HOSTNAME = 'pi'
    # ADS address of TwinCAT device                     
    PLC_AMS_ID = '192.168.1.88.1.1'
    #PLC_AMS_ID = '192.168.1.112.1.1'

    # We open the port for communication via ADS
    pyads.open_port()
    # Set ADS address for Raspberry Pi                        
    pyads.set_local_address(SENDER_AMS)         
    print("Connecting to PLC...")                  
    plc = pyads.Connection(PLC_AMS_ID, 851, PLC_IP)
    # Open connection    
    plc.open()
    # Check connection
    print("Connected:",plc.is_open)              
    print('--------------------------------')

except:
    plc.close()
    print("PLC connection timeout...")

stateCurrent = 0
partsProduced = 0
machDesignSpeed = 0
badParts = 0

# Interval of sending messages to IoT Central in seconds
intervalPosiljanja = 120

@plc.notification(pyads.PLCTYPE_DINT)
def callbackBadParts(handle, name, timestamp, value):
    global badParts
    badParts = value
    print(f"---> Update - number of bad parts:\t{badParts}\t<---")


@plc.notification(pyads.PLCTYPE_REAL)
def callbackMachSpeed(handle, name, timestamp, value):
    global machDesignSpeed
    machDesignSpeed = value


@plc.notification(pyads.PLCTYPE_DINT)
def callbackAccCount(handle, name, timestamp, value):
    global partsProduced
    partsProduced = value





#Timer instances
#For measuring time in certain PackML state
undefinedTimer      =    Timer()     # state 0
clearingTimer       =    Timer()     # state 1
stoppedTimer        =    Timer()     # state 2
startingTimer       =    Timer()     # state 3
idleTimer           =    Timer()     # state 4
suspendedTimer      =    Timer()     # state 5
executeTimer        =    Timer()     # state 6 
stoppingTimer       =    Timer()     # state 7
abortingTimer       =    Timer()     # state 8
abortedTimer        =    Timer()     # state 9
holdingTimer        =    Timer()     # state 10
heldTimer           =    Timer()     # state 11
unholdingTimer      =    Timer()     # state 12
suspendingTimer     =    Timer()     # state 13
unsuspendingTimer   =    Timer()     # state 14
resettingTimer      =    Timer()     # state 15
completingTimer     =    Timer()     # state 16
completeTimer       =    Timer()     # state 17


# Callback function to track time in certain state
@plc.notification(pyads.PLCTYPE_DINT)
def trackTime(handle, name, timestamp,value):
    global stateCurrent
    prejsnje_stanje = stateCurrent
    stanje = value
    stateCurrent = stanje
    print(f"--->\tUpdate - current state:\t{stanje}\t<---")
    print(f"--->\tUpdate - previous state:\t{prejsnje_stanje}\t<---")


    # Check state
    if stanje == 0:
        print("Not defined...")

    elif stanje == 1:
        try:
            # Let’s check that the previous state was implemented
            if abortedTimer._start_time is not None:
                # Stop the timer of previous state
                abortedTimer.stop(prejsnje_stanje)

            # Check that the new state is not active
            if clearingTimer._start_time is None:     
                # We start the timer in the new state
                clearingTimer.start()
            
        except:
            print("Problem in state 1.")

    elif stanje == 2:
        try:

            if clearingTimer._start_time is not None: 
                clearingTimer.stop(prejsnje_stanje)
            if stoppingTimer._start_time is not None:
                stoppingTimer.stop(prejsnje_stanje)
        
            if stoppedTimer._start_time is None:
                stoppedTimer.start()
            
        except:
            print("Problem in state 2.")

    elif stanje == 3:
        try:

            if idleTimer._start_time is not None: 
                idleTimer.stop(prejsnje_stanje)
        
            if startingTimer._start_time is None:
                startingTimer.start()
            
        except:
            print("Problem in state 3.")

    elif stanje == 4:
        try:

            if resettingTimer._start_time is not None: 
                resettingTimer.stop(prejsnje_stanje)
        
            if idleTimer._start_time is None:
                idleTimer.start()
            
        except:
            print("Problem in state 4.")

    elif stanje == 5:
        try:

            if suspendingTimer._start_time is not None: 
                suspendingTimer.stop(prejsnje_stanje)
        
            if suspendedTimer._start_time is None:
                suspendedTimer.start()
            
        except:
            print("Problem v stanju 5.")

    elif stanje == 6:

        try:


            if startingTimer._start_time is not None: 
                    startingTimer.stop(prejsnje_stanje)
                
            if unholdingTimer._start_time is not None: 
                unholdingTimer.stop(prejsnje_stanje)

            if unsuspendingTimer._start_time is not None: 
                unsuspendingTimer.stop(prejsnje_stanje)

            if executeTimer._start_time is None:
                executeTimer.start()
                
                
        except:
            print("Problem in state.")

    elif stanje == 7:

        try:

            if idleTimer._start_time is not None: 
                    idleTimer.stop(prejsnje_stanje)

            if startingTimer._start_time is not None: 
                    startingTimer.stop(prejsnje_stanje)

            if executeTimer._start_time is not None: 
                    executeTimer.stop(prejsnje_stanje)
            
            if completingTimer._start_time is not None: 
                    completingTimer.stop(prejsnje_stanje)
            
            if completeTimer._start_time is not None: 
                    completeTimer.stop(prejsnje_stanje)
            
            if unholdingTimer._start_time is not None: 
                    unholdingTimer.stop(prejsnje_stanje)
            
            if heldTimer._start_time is not None: 
                    heldTimer.stop(prejsnje_stanje)

            if holdingTimer._start_time is not None: 
                    holdingTimer.stop(prejsnje_stanje)

            if unsuspendingTimer._start_time is not None: 
                    unsuspendingTimer.stop(prejsnje_stanje)

            if suspendedTimer._start_time is not None: 
                    suspendedTimer.stop(prejsnje_stanje)
            
            if suspendingTimer._start_time is not None: 
                    suspendingTimer.stop(prejsnje_stanje)
            
            if resettingTimer._start_time is not None: 
                    resettingTimer.stop(prejsnje_stanje)
            
            if stoppingTimer._start_time is None:
                stoppingTimer.start()
            
        
        except:
            print("Problem in state 7.")
        
    elif stanje == 8:
        try:
            if idleTimer._start_time is not None: 
                    idleTimer.stop(prejsnje_stanje)

            if startingTimer._start_time is not None: 
                    startingTimer.stop(prejsnje_stanje)

            if executeTimer._start_time is not None: 
                    executeTimer.stop(prejsnje_stanje)
            
            if completingTimer._start_time is not None: 
                    completingTimer.stop(prejsnje_stanje)
            
            if completeTimer._start_time is not None: 
                    completeTimer.stop(prejsnje_stanje)
            
            if unholdingTimer._start_time is not None: 
                    unholdingTimer.stop(prejsnje_stanje)
            
            if heldTimer._start_time is not None: 
                    heldTimer.stop(prejsnje_stanje)

            if holdingTimer._start_time is not None: 
                    holdingTimer.stop(prejsnje_stanje)

            if unsuspendingTimer._start_time is not None: 
                    unsuspendingTimer.stop(prejsnje_stanje)

            if suspendedTimer._start_time is not None: 
                    suspendedTimer.stop(prejsnje_stanje)
            
            if suspendingTimer._start_time is not None: 
                    suspendingTimer.stop(prejsnje_stanje)
            
            if resettingTimer._start_time is not None: 
                    resettingTimer.stop(prejsnje_stanje)
            
            if stoppedTimer._start_time is not None: 
                stoppedTimer.stop(prejsnje_stanje)

            if stoppingTimer._start_time is not None: 
                stoppingTimer.stop(prejsnje_stanje)

            if clearingTimer._start_time is not None: 
                clearingTimer.stop(prejsnje_stanje)

            if abortingTimer._start_time is None:
                abortingTimer.start()
            

        except:
            print("Problem in state 8.")
    
    elif stanje == 9:
        try:
            if abortingTimer._start_time is not None: 
                abortingTimer.stop(prejsnje_stanje)
            
            if abortedTimer._start_time is None:
                abortedTimer.start()
            
        except:
            print("Problem in state 9.")


    elif stanje == 10:
        try:
            if executeTimer._start_time is not None: 
                executeTimer.stop(prejsnje_stanje)

            if holdingTimer._start_time is None:
                holdingTimer.start()
            

        except:
            print("Problem in state 10.")
        
    elif stanje == 11:
        try:
            if holdingTimer._start_time is not None: 
                holdingTimer.stop(prejsnje_stanje)

            if heldTimer._start_time is None:
                heldTimer.start()
            
        except:
            print("Problem in state 11.")
        


    elif stanje == 12:
        try:
            if heldTimer._start_time is not None:
                heldTimer.stop(prejsnje_stanje)
            
            if unholdingTimer._start_time is None:
                unholdingTimer.start()
           
        except:
            print("Problem in state 12.")

    elif stanje == 13:
        try:
            if executeTimer._start_time is not None:
                executeTimer.stop(prejsnje_stanje)
            
            if suspendingTimer._start_time is None:
                suspendingTimer.start()
           
        except:
            print("Problem in state 13.")
    elif stanje == 14:
        try:
            if suspendedTimer._start_time is not None:
                suspendedTimer.stop(prejsnje_stanje)
            
            if unsuspendingTimer._start_time is None:
                unsuspendingTimer.start()
            
        except:
            print("Problem in state 14.")
    elif stanje == 15:
        try:
            if stoppedTimer._start_time is not None:
                stoppedTimer.stop(prejsnje_stanje)
            
            if completeTimer._start_time is not None:
                completeTimer.stop(prejsnje_stanje)
            
            if resettingTimer._start_time is None:
                resettingTimer.start()
            
        except:
            print("Problem in state 15.")
    elif stanje == 16:
        try:
            if executeTimer._start_time is not None:
                executeTimer.stop(prejsnje_stanje)
            
            if completingTimer._start_time is None:
                completingTimer.start()
            
        except:
            print("Problem in state 16.")
    elif stanje == 17:
        try:
            if completingTimer._start_time is not None:
                completingTimer.stop(prejsnje_stanje)
            
            if completeTimer._start_time is None:
                completeTimer.start()
            
        except:
            print("Problem in state 17.")
    else:
        print("Interruption")

        



    
# Create device notifications for TwinCAT variables (tags)
plc.add_device_notification('GlobalVariables.PackTags.Status.StateCurrent',pyads.NotificationAttrib(4), trackTime)
plc.add_device_notification('GlobalVariables.PackTags.Admin.ProdProcessedCount[1].AccCount',pyads.NotificationAttrib(4), callbackAccCount)
plc.add_device_notification('GlobalVariables.PackTags.Admin.MachDesignSpeed',pyads.NotificationAttrib(4), callbackMachSpeed)
plc.add_device_notification('GlobalVariables.PackTags.Admin.ProdDefectiveCount[1].AccCount',pyads.NotificationAttrib(4), callbackBadParts)


async def main():

    # Connection to IoT Central
    async def register_device():
        provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
            provisioning_host='global.azure-devices-provisioning.net',
            registration_id=device_id,
            id_scope=id_scope,
            symmetric_key=primary_key)

        return await provisioning_device_client.register()
    
    # wait for results
    results = await asyncio.gather(register_device())
    # Get result info
    registration_result = results[0]
    
    # Create connection string
    conn_str='HostName=' + registration_result.registration_state.assigned_hub + \
                ';DeviceId=' + device_id + \
                ';SharedAccessKey=' + primary_key
    
    # A Client object is used to interact with Azure IoT Central
    device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)

    # Establish a connection with our client
    print('Connecting...')
    await device_client.connect()
    print('Success.')

    def calculateA():
        cas_delovanja = executeTimer.current()+holdingTimer.current()+abortingTimer.current()
        cas_v_napaki = heldTimer.current() + stoppedTimer.current() + abortedTimer.current()

        if cas_v_napaki > 1 and cas_delovanja == 0:
            a_oee = 0
        elif cas_v_napaki == 0 and cas_delovanja == 0:
            a_oee = 0
        else:
            a_oee = cas_delovanja / (cas_delovanja+cas_v_napaki)
          
        return a_oee    

    def calculateP():
        try:
            p_oee = partsProduced/ ((executeTimer._current_time/60)*(machDesignSpeed))

            return p_oee
        except:
            if executeTimer._current_time == 0:

            elif machDesignSpeed == 0:
                print("Error (P): Max speed is set to 0. Please change the speed.")
            print("P:  0.00%   ")

    def calculateQ():
        try:
            q_oee = (partsProduced - badParts)/partsProduced
            #print(f"Q:  {q_oee*100:0.2f}%   ")
            return q_oee
        except:
            print("Error (Q): No parts produced.")

    

    def calculateOEE():
        try:
            oee_a = calculateA()
            oee_p = calculateP()
            oee_q = calculateQ()
            oee = oee_a*oee_p*oee_q
            print(f"A:\t{oee_a*100:0.2f}%   ")
            print(f"P:\t{oee_p*100:0.2f}%   ")
            print(f"Q:\t{oee_q*100:0.2f}%   ")
            print(f"OEE:\t{oee*100:0.2f}%   ")
            return oee_a, oee_p, oee_q, oee
        except:
            print("Error (OEE): not enough data.")


    
    # Function to convert telemetry to JSON file
    def collectJsonData():
        try:
            
            # Record the values we monitor in the variables
            oeeA, oeeP, oeeQ, oee = calculateOEE()

            # Let's compile a JSON file to transfer the values to the cloud
            data = {
                "A" : float(oeeA)*100,
                "P"      : float(oeeP)*100,
                "Q"    : float(oeeQ)*100,
                "OEE" : float(oee)*100
            }
            
            return json.dumps(data)
        except:
            pass
            
        

        
    
    
    # Function for receiving commands from the cloud
    async def commandListener(device_client):
        try:
            global intervalPosiljanja
            while True:

                
                    # Wait for the command from the cloud application
                    method_request = await device_client.receive_method_request()

                    # Get command name
                    ukaz = method_request.name

                    # Print command name
                    print("\t>Command from IoT Central application: ", ukaz)
                    # Prepare the answer for cloud application
                    payload = {'result': True, 'command': ukaz}

                    if ukaz == 'nOdstSlabihKosov':
                        plc.write_by_name('GlobalVariables.nOdstSlabihKosov', method_request.payload, pyads.PLCTYPE_INT)
                    elif ukaz == 'nMaksHitrost':
                        plc.write_by_name('GlobalVariables.PackTags.Admin.MachDesignSpeed', method_request.payload, pyads.PLCTYPE_REAL)
                    elif ukaz == 'intervalPosiljanja':
                        intervalPosiljanja = method_request.payload
                        print(f"Nastavljen nov interval posiljanja sporocil v aplikacijo IoT Central: {intervalPosiljanja}")
                    
                    
                    
                    # We return the answer about the successfully passed command
                    method_response = MethodResponse.create_from_method_request(
                        method_request, 200, payload
                    )

                    # We are waiting for the response to be sent successfully
                    await device_client.send_method_response(method_response)

        # In the event of an interruption, stop the function
        except asyncio.CancelledError:
            print("\n")
                
    
    # Function for sending telemetry to the cloud
    async def mainLoop():
        try:

            while True:

                # Call the telemetry preparation function
                telemetry = collectJsonData()

                print(f"Telementry:\t{telemetry}")

                # Telemetry is sent to IoT Central
                await device_client.send_message(telemetry)

                # Wait 60s or so
                await asyncio.sleep(intervalPosiljanja)

        # In the event of an interruption, stop the function        
        except asyncio.CancelledError:
            print("Closing connection to IoT Cetral...")

    
    # We run a parallel wait for commands
    listeners = asyncio.gather(commandListener(device_client))
    
    # Let's take the main loop
    await mainLoop()
    
    # Let's stop waiting for orders
    listeners.cancel()

    # Disconnect from the server
    await device_client.disconnect()
    

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Connection closed.")
