# Knjiznica PyAds
import pyads
from time import sleep
from timer import Timer
from multiprocessing import Process
from dotenv import load_dotenv 
from azure.iot.device.aio import IoTHubDeviceClient, ProvisioningDeviceClient
from azure.iot.device import MethodResponse 
import os, asyncio, json 


# Pridobimo povezovalne kljuce 
load_dotenv()
id_scope = os.getenv('ID_SCOPE')
device_id = os.getenv('DEVICE_ID')
primary_key = os.getenv('PRIMARY_KEY')


try:

    # Vzpostavitev ADS povezave
    # ADS naslov Raspberry Pi
    SENDER_AMS = '192.168.1.120.1.1'
    # Lokalni IP naslov racunalnika s TwinCat okoljem    
    #PLC_IP = '192.168.1.88'
    PLC_IP = '192.168.1.112'
    # Uporabnisko ime za dostop do TwinCat naprave (ce je v uporabi)            
    USERNAME = ''
    # Geslo za dostop do TwinCat naprave (ce je v uporabi)                        
    PASSWORD = ''
    # Lokalni IP Raspberry Pi                        
    ROUTE_NAME = '192.168.1.120'
    # Ime Raspberry Pi        
    HOSTNAME = 'pi'
    # ADS naslov TwinCat naprave                     
    PLC_AMS_ID = '192.168.1.88.1.1'
    #PLC_AMS_ID = '192.168.1.112.1.1'

    # Odpremo vrata za komunikacijo preko ADS
    pyads.open_port()
    # Nastavimo ADS naslov Raspberry Pi                        
    pyads.set_local_address(SENDER_AMS)         
    print("Povezovanje s PLK...")
    # Shranimo instanco povezave v spremenljivko plc                       
    plc = pyads.Connection(PLC_AMS_ID, 851, PLC_IP)
    # Odpremo povezavo     
    plc.open()
    # Preverimo povezavo
    print("Povezava vzpostavljena:",plc.is_open)              
    print('--------------------------------')

except:
    plc.close()
    print("Cas je potekel. Ni povezave s PLK...")

stateCurrent = 0
partsProduced = 0
machDesignSpeed = 0
badParts = 0
#Interval posiljanja sporocil v IoT Central v sekundah
intervalPosiljanja = 120

@plc.notification(pyads.PLCTYPE_DINT)
def callbackBadParts(handle, name, timestamp, value):
    global badParts
    badParts = value
    print(f"---> Posodobitev - stevilo slabih kosov:\t{badParts}\t<---")


@plc.notification(pyads.PLCTYPE_REAL)
def callbackMachSpeed(handle, name, timestamp, value):
    global machDesignSpeed
    machDesignSpeed = value
    print(f"---> Posodobitev - ciljna hitrost stroja:\t{machDesignSpeed}\t<---")


@plc.notification(pyads.PLCTYPE_DINT)
def callbackAccCount(handle, name, timestamp, value):
    global partsProduced
    partsProduced = value
    #print(f"---> Posodobitev - stevilo kosov:\t{partsProduced}\t<---")




#Deklaracija casovnikov
undefinedTimer      =    Timer()     # stanje 0
clearingTimer       =    Timer()     # stanje 1
stoppedTimer        =    Timer()     # stanje 2
startingTimer       =    Timer()     # stanje 3
idleTimer           =    Timer()     # stanje 4
suspendedTimer      =    Timer()     # stanje 5
executeTimer        =    Timer()     # stanje 6 
stoppingTimer       =    Timer()     # stanje 7
abortingTimer       =    Timer()     # stanje 8
abortedTimer        =    Timer()     # stanje 9
holdingTimer        =    Timer()     # sanje 10
heldTimer           =    Timer()     # stanje 11
unholdingTimer      =    Timer()     # stanje 12
suspendingTimer     =    Timer()     # stanje 13
unsuspendingTimer   =    Timer()     # stanje 14
resettingTimer      =    Timer()     # stanje 15
completingTimer     =    Timer()     # stanje 16
completeTimer       =    Timer()     # stanje 17

@plc.notification(pyads.PLCTYPE_DINT)
def trackTime(handle, name, timestamp,value):
    global stateCurrent
    prejsnje_stanje = stateCurrent
    stanje = value
    stateCurrent = stanje
    print(f"--->\tPosodobitev - trenutno stanje:\t{stanje}\t<---")
    print(f"--->\tPosodobitev - prejsnje stanje:\t{prejsnje_stanje}\t<---")


    # Preverimo stanje
    if stanje == 0:
        print("Nedefinirano stanje 0...")

    elif stanje == 1:
        try:
            # Preverimo, da se je prejsnje stanje izvedlo
            if abortedTimer._start_time is not None:
                # Ustavimo casovnik prejsnjega stanja 
                abortedTimer.stop(prejsnje_stanje)

            # Preverimo, da novo stanje ni aktivno
            if clearingTimer._start_time is None:
                # Zazenemo casovnik v novem stanju
                clearingTimer.start()
            
        except:
            print("Problem v stanju 1.")

    elif stanje == 2:
        try:

            if clearingTimer._start_time is not None: 
                clearingTimer.stop(prejsnje_stanje)
            if stoppingTimer._start_time is not None:
                stoppingTimer.stop(prejsnje_stanje)
        
            if stoppedTimer._start_time is None:
                stoppedTimer.start()
            
        except:
            print("Problem v stanju 2.")

    elif stanje == 3:
        try:

            if idleTimer._start_time is not None: 
                idleTimer.stop(prejsnje_stanje)
        
            if startingTimer._start_time is None:
                startingTimer.start()
            
        except:
            print("Problem v stanju 3.")

    elif stanje == 4:
        try:

            if resettingTimer._start_time is not None: 
                resettingTimer.stop(prejsnje_stanje)
        
            if idleTimer._start_time is None:
                idleTimer.start()
            
        except:
            print("Problem v stanju 4.")

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
                print("Stroj v pogonu!")
                
        except:
            print("Problem v stanju 6.")

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
            print("Problem v stanju 7.")
        
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
            print("Problem v stanju 8")
    
    elif stanje == 9:
        try:
            if abortingTimer._start_time is not None: 
                abortingTimer.stop(prejsnje_stanje)
            
            if abortedTimer._start_time is None:
                abortedTimer.start()
            
        except:
            print("Problem v stanju 9")


    elif stanje == 10:
        try:
            if executeTimer._start_time is not None: 
                executeTimer.stop(prejsnje_stanje)

            if holdingTimer._start_time is None:
                holdingTimer.start()
            

        except:
            print("Problem v stanju 10.")
        
    elif stanje == 11:
        try:
            if holdingTimer._start_time is not None: 
                holdingTimer.stop(prejsnje_stanje)

            if heldTimer._start_time is None:
                heldTimer.start()
            
        except:
            print("Problem v stanju 11.")
        


    elif stanje == 12:
        try:
            if heldTimer._start_time is not None:
                heldTimer.stop(prejsnje_stanje)
            
            if unholdingTimer._start_time is None:
                unholdingTimer.start()
           
        except:
            print("Problem v stanju 12")

    elif stanje == 13:
        try:
            if executeTimer._start_time is not None:
                executeTimer.stop(prejsnje_stanje)
            
            if suspendingTimer._start_time is None:
                suspendingTimer.start()
           
        except:
            print("Problem v stanju 13")
    elif stanje == 14:
        try:
            if suspendedTimer._start_time is not None:
                suspendedTimer.stop(prejsnje_stanje)
            
            if unsuspendingTimer._start_time is None:
                unsuspendingTimer.start()
            
        except:
            print("Problem v stanju 14")
    elif stanje == 15:
        try:
            if stoppedTimer._start_time is not None:
                stoppedTimer.stop(prejsnje_stanje)
            
            if completeTimer._start_time is not None:
                completeTimer.stop(prejsnje_stanje)
            
            if resettingTimer._start_time is None:
                resettingTimer.start()
            
        except:
            print("Problem v stanju 15")
    elif stanje == 16:
        try:
            if executeTimer._start_time is not None:
                executeTimer.stop(prejsnje_stanje)
            
            if completingTimer._start_time is None:
                completingTimer.start()
            
        except:
            print("Problem v stanju 16")
    elif stanje == 17:
        try:
            if completingTimer._start_time is not None:
                completingTimer.stop(prejsnje_stanje)
            
            if completeTimer._start_time is None:
                completeTimer.start()
            
        except:
            print("Problem v stanju 17")
    else:
        print("Prekinitev")

        



    

plc.add_device_notification('GlobalVariables.PackTags.Status.StateCurrent',pyads.NotificationAttrib(4), trackTime)
plc.add_device_notification('GlobalVariables.PackTags.Admin.ProdProcessedCount[1].AccCount',pyads.NotificationAttrib(4), callbackAccCount)
plc.add_device_notification('GlobalVariables.PackTags.Admin.MachDesignSpeed',pyads.NotificationAttrib(4), callbackMachSpeed)
plc.add_device_notification('GlobalVariables.PackTags.Admin.ProdDefectiveCount[1].AccCount',pyads.NotificationAttrib(4), callbackBadParts)


async def main():

    # Povezava z IoT Central
    async def register_device():
        provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
            provisioning_host='global.azure-devices-provisioning.net',
            registration_id=device_id,
            id_scope=id_scope,
            symmetric_key=primary_key)

        return await provisioning_device_client.register()
    
    # Pocakamo na rezultate povezave
    results = await asyncio.gather(register_device())
    # Pridobimo rezultate o nasi IoT Central aplikaciji
    registration_result = results[0]
    
    # Sestavimo povezovalni niz
    conn_str='HostName=' + registration_result.registration_state.assigned_hub + \
                ';DeviceId=' + device_id + \
                ';SharedAccessKey=' + primary_key
    
    # Za interakcijo z Azure IoT Central se uporabi Client objekt
    device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)

    # Vzpostavimo povezavo z nasim klientom
    print('Povezovanje s klientom...')
    await device_client.connect()
    print('Povezava s klientom vzpostavljena.')

    def calculateA():
        cas_delovanja = executeTimer.current()+holdingTimer.current()+abortingTimer.current()
        #print(f"Cas delovanja:  {cas_delovanja:0.1f} sekund")
        cas_v_napaki = heldTimer.current() + stoppedTimer.current() + abortedTimer.current()
        #print(f"Cas v napaki:   {cas_v_napaki:0.1f} sekund")

        if cas_v_napaki > 1 and cas_delovanja == 0:
            a_oee = 0
        elif cas_v_napaki == 0 and cas_delovanja == 0:
            a_oee = 0
        else:
            a_oee = cas_delovanja / (cas_delovanja+cas_v_napaki)
        
        #print(f"A:  {a_oee*100:0.2f}%   ")    
        return a_oee    

    def calculateP():
        try:
            p_oee = partsProduced/ ((executeTimer._current_time/60)*(machDesignSpeed))
            #print(f"P:  {p_oee*100:0.2f}%   ")
            return p_oee
        except:
            if executeTimer._current_time == 0:
                print("Napaka (P): Stroj se ni bil v stanju izvrsevanja.")
            elif machDesignSpeed == 0:
                print("Napaka (P): Maksimalna hitrost kosov na minuto je nastavljena na 0. Prosim popravi vrednost.")
            print("P:  0.00%   ")

    def calculateQ():
        try:
            q_oee = (partsProduced - badParts)/partsProduced
            #print(f"Q:  {q_oee*100:0.2f}%   ")
            return q_oee
        except:
            print("Napaka (Q): Ni proizvedenih izdelkov.")

    

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
            print("Napaka (OEE): OEE nima dovolj podatkov za izracun.")


    # Funkcija za pretvorbo telemetrije v JSON datoteko
    def collectJsonData():
        try:
            # Zapisemo vrednosti, ki jih spremljamo v spremenljivke
            oeeA, oeeP, oeeQ, oee = calculateOEE()

            #print("OEE: ",calculateOEE())
            # Sestavimo JSON datoteko za prenos vrednosti v oblak
            data = {
                "A" : float(oeeA)*100,
                "P"      : float(oeeP)*100,
                "Q"    : float(oeeQ)*100,
                "OEE" : float(oee)*100
            }
            
            return json.dumps(data)
        except:
            pass
            
        

        
    
    # Funkcija za sprejem ukazov iz oblaka
    async def commandListener(device_client):
        try:
            global intervalPosiljanja
            while True:

                
                    # Cakamo na ukaz iz aplikacije 
                    method_request = await device_client.receive_method_request()

                    # Pridobimo ime prejetega ukaza
                    ukaz = method_request.name

                    # Izpis ukaza
                    print("\t>Sprejet ukaz iz IoT Central aplikacije: ", ukaz)
                    # Pripravimo odgovor na prejet ukaz
                    payload = {'result': True, 'command': ukaz}

                    if ukaz == 'nOdstSlabihKosov':
                        plc.write_by_name('GlobalVariables.nOdstSlabihKosov', method_request.payload, pyads.PLCTYPE_INT)
                    elif ukaz == 'nMaksHitrost':
                        plc.write_by_name('GlobalVariables.PackTags.Admin.MachDesignSpeed', method_request.payload, pyads.PLCTYPE_REAL)
                    elif ukaz == 'intervalPosiljanja':
                        intervalPosiljanja = method_request.payload
                        print(f"Nastavljen nov interval posiljanja sporocil v aplikacijo IoT Central: {intervalPosiljanja}")
                    
                    
                    # Vrnemo odgovor o uspesno sprejetem ukazu
                    method_response = MethodResponse.create_from_method_request(
                        method_request, 200, payload
                    )

                    # Pocakamo da je odgovor uspesno poslan
                    await device_client.send_method_response(method_response)

        # V primeru da pride do prekinitve prenehamo z izvajanjem funkcije
        except asyncio.CancelledError:
            print("\n")
                
    # Funkcija za posiljanje telemetrije v oblak
    async def mainLoop():
        try:

            while True:

                # Klic funkcije za pripravo telemetrije
                telemetry = collectJsonData()

                print(f"Poslana telemetrija:\t{telemetry}")

                # Telemetrijo posljemo v IoT Central
                await device_client.send_message(telemetry)

                #Pocakamo 60s na posiljanje novega paketa
                await asyncio.sleep(intervalPosiljanja)

        # V primeru da pride do prekinitve prenehamo z izvajanjem funkcije        
        except asyncio.CancelledError:
            print("Zapiram povezavo z IoT Cetral...")
    

    # Zaženemo vzporedno cakanje na ukaze
    listeners = asyncio.gather(commandListener(device_client))
    
    # Pozenemo glavno zanko
    await mainLoop()

    # Prekinemo cakanje na ukaze
    listeners.cancel()

    # Prekinemo povezavo s serverjem
    await device_client.disconnect()
    

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Povezava zaprta.")



