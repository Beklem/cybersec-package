from scapy.all import *
import sys
import signal
import os

#handle when the user copies
def signalHandler(signal, frame):
    print("\n-----------------------")
    print("Execution aborted by user")
    print("-------------------------")
    os.system("kill -9 " + str(os.getpid()))
    sys.exit(1)

#exit
def signalExit(signal, frame):
    print("Signal exit")
    sys.exit(1)

#remind user of basic syntax if they suck
def usage():
    if len(sys.argv) < 3:

        print("\n Usage:")


        print("\twifiScanner.py -i <interface> \n")
        sys.exit(1)

#acting like Scooby Doo and smelling anything that remotely resembles food (wifi)
def sniffPackets(packet):
    try:
        SRCMAC = packe[0].addr2
        DSTMAC = packet[0].addr1
        BSSID = packet[0].addr3
    except:
        print("Cannot read MAC address")
        print(str(packet).encode("hex"))
        sys.exc_clear()

    try:
        SSIDSize = packet[0][Dot11Elt].len
        SSID = packet[0][Dot11Elt].info
    except: #leave it if there is no name of the food
        SSID = ""
        SSIDSize = 0

    if packet[0].type == 0:
        ST = packet[0][Dot11].subtype
        if str(ST) == "8" and SSID == "" and DSTMAC.lower() == "ff:ff:ff:ff:ff:ff":
            p = packet[Dot11Elt]
            cap = packet.sprintf("{Dot11Beacon:%Dot11Beacon.cap%}"
                                "{Dot11ProbeResp:%Dot11ProbeResp.cap%}").split('+')
            channel = None
            crypto = set()

#not duplicating results
def initProcess():
    global ssidList
    ssidList = {}
    global s
    s = conf.L2socket(iface=newiface)

#function 2 set up wireless interface in a monitor type mode
def setUpMonitor(iface):
    print("Setting up sniffing options...")
    os.system('ifconfig' + iface + 'down')
    try:
        os.system('iwconfig' + iface + 'mode monitor')
    except:
        print("Failed to setup your interface in monitor mode")
        sys.exit(1)
    os.system('ifconfig' + iface + 'up')
    return iface

def checkRoot():
    if not os.getpid() == 0:
        print("You must run this script w/ root privileges.")
        exit(1)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signalHandler)
    usage()
    checkRoot()
    parameters = {sys.argv[1]:sys.argv[2]}
    if "mon" not in str(parameters["-i"]):
        newiface = setup_monitor(parameters["-i"])
    else:
        newiface = str(parameters["-i"])
    init_process()
    print("Starting HA Wi-Fi Sniffer")

    print("Sniffing on interface " + str(newiface) + "... \n")
    sniff(iface=newiface, prn=sniffpackets, store=0)





