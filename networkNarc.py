import time
from scapy.all import ARP, Ether, srp 
import socket
import os

manufacturerDb = None
knownDevices = {}
networkToScan = "192.168.0.1" #insert IP HERE or it wont work!!

def loadOuiMap(): #function to load the OUI database!
    global manufacturerDb
    if manufacturerDb is not None: return True
    scriptDir = os.path.dirname(__file__)
    filePath = os.path.join(scriptDir, 'oui.txt')
    ouiMap = {}
    print(f"[+] Initializing OUI Database from: '{filePath}'...")
    try:
        with open(filePath, 'r', encoding='utf-8') as file:
            for line in file:
                if '(hex)' in line:
                    parts = line.split('(hex)')
                    oui = parts[0].strip().replace('-', '')
                    manufacturerName = parts[1].strip()
                    ouiMap[oui] = manufacturerName
        manufacturerDb = ouiMap
        print("[+] OUI Database build: SUCCESS.")
        return True
    except FileNotFoundError:
        print(f"[!] FATAL ERROR: oui.txt not found at: {filePath}")
        return False

def getManufacturer(macAddress): 
    if manufacturerDb is None: return "OUI Database Offline"
    ouiToLookup = macAddress.replace(':', '').upper()[:6]
    return manufacturerDb.get(ouiToLookup, 'Vendor Unknown')

def discoverNetwork(ipRange):
    print(f"[*] Commencing ARP scan on target range: {ipRange}...")
    arpRequest = ARP(pdst=ipRange)
    broadcastPacket = Ether(dst="ff:ff:ff:ff:ff:ff")
    arpRequestBroadcast = broadcastPacket / arpRequest
    answeredList = srp(arpRequestBroadcast, timeout=2, verbose=False)[0]
    foundDevicesDict = {element[1].psrc: element[1].hwsrc for element in answeredList}
    print(f"[*] Network reconnaissance complete. {len(foundDevicesDict)} active hosts detected.")
    return foundDevicesDict

def performSingleScanCycle():
    global knownDevices, networkToScan, manufacturerDb
    if manufacturerDb is None:
        if not loadOuiMap(): 
             return [{'error': "OUI Database could not be loaded."}]

    print(f"\n[+] Initiating network security sweep... Target: {networkToScan}")
    currentDeviceList = discoverNetwork(networkToScan)
    intruderDataList = [] 
    unknownDeviceFound = False

    print(f"[*] Analyzing {len(currentDeviceList)} discovered hosts...")
    for ip, mac in currentDeviceList.items():
        formattedMac = mac.lower()
        knownDevicesLower = {k.lower(): v for k, v in knownDevices.items()}
        if formattedMac not in knownDevicesLower:
            unknownDeviceFound = True
            manufacturer = getManufacturer(formattedMac)
            hostName = "N/A" 
            try:
                hostName = socket.gethostbyaddr(ip)[0]
            except socket.herror:
                pass
            intruderDataList.append({ 
                "ip": ip, "mac": mac,
                "manufacturer": manufacturer, "hostname": hostName
            })
            print(f"[!] ALERT: Unidentified host: IP {ip}, MAC {mac}") 

    if not unknownDeviceFound:
        print("[+] Network integrity check: PASSED.")
    else:
        intruderCount = len(intruderDataList)
        print(f"[!] Network Integrity Check: FAILED. {intruderCount} anomalies detected.")
    print("[+] Security sweep complete.")
    return intruderDataList

if __name__ == '__main__':
    print("[+] NetworkNarc Backend - Direct Execution Mode")
    knownDevices = {"aa:bb:cc:11:22:33": "Dummy"} 
    networkToScan = "192.168.0.1" #insert IP PLEASE IT WONT WORK WITHOUT IT
    if loadOuiMap(): 
        while True:
            results = performSingleScanCycle() 
            print("\n--- CONSOLE SCAN RESULTS ---")
            if not results: print("No intruders or all devices known.")
            elif "error" in results[0]: print(results[0]["error"])
            else:
                for intruderDict in results:
                    print(f"  IP: {intruderDict['ip']}, MAC: {intruderDict['mac']}, Manuf: {intruderDict['manufacturer']}, Host: {intruderDict['hostname']}")
            print(f"\n[+] Standalone mode: Next scan in 5 minutes...")
            time.sleep(300)
    else:
        print("[!] Could not start standalone scanner.")