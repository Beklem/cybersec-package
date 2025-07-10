#this is the big bog script, using -sS allows you to bypass some firewalls (even Windows)
import nmap
import sys

#using -sS on linux, it needs to be ran as sudo
#-O for OS detection
#-sV for Version detection
#-sT less stealthy scan, but it doesn't need admin  
def advancedPortScanner(targetHost, portsToScan, scanType='-sT'): #the -sS this is a stealthy scan, it is a lot harder for the firewall to log, using -sT might fail on windows
    print(f"Alright, {targetHost}, let's see what your hiding. Using Nmap with this scan type: {scanType}")
    portScannerObj = nmap.PortScanner()

#the arguments in the scanType that is above takes in command line operations, so you can put in mini instructions for the nmap module for BIG results
    try:
        print(f"Scanning {targetHost} for ports {portsToScan}...")
        scanData = portScannerObj.scan(hosts=targetHost, ports=portsToScan, arguments=scanType)
        print(f"Raw scan data, if your into that kinky stuff: {scanData}")

        if not scanData['scan']:
            print(f"No scan results for {targetHost}. Maybe it's shy... or doesn't exist. Make sure you type it right buddy.")
            return

        for host in portScannerObj.all_hosts():
            print(f"\n Host: {host} ({portScannerObj[host].hostname()})")
            print(f"State: {portScannerObj[host].state()}")

            #OS detection for using -O
            if 'osmatch' in portScannerObj[host] and portScannerObj[host]['osmatch']:
                print("OS Guess-timates (since Nmap is a digital psychic):")
                for osMatch in portScannerObj[host]['osmatch']:
                    print(f"    -Name: {osMatch['name']} ({osMatch['accuracy']}%)")
                    for osClass in osMatch['osclass']:
                        print(f"    -Type: {osClass['type']}, Vendor: {osClass['vendor']}, OS Family: {osClass['osfamily']}, OS Gen: {osClass['osgen']}")

            for protocol in portScannerObj[host].all_protocols():
                print(f"\n Protocol: {protocol.upper()}")
                openPorts = portScannerObj[host][protocol].keys()
                if not openPorts:
                    print(" Cue the sad trombone, there are NO open ports in this bitch.")
                    continue

                for port in sorted(openPorts):
                    portInfo = portScannerObj[host][protocol][port]
                    portState = portInfo['state']
                    portReason = portInfo.get('reason', 'N/A')
                    print(f" Port {port}: {portState} (Reason: {portReason})")
                    
                    if portState == 'open': #just bc they are VIPs
                        serviceName = portInfo.get('name', 'unknown_service')
                        product = portInfo.get('product', '')
                        version = portInfo.get('version', '')
                        extraInfo = portInfo.get('extrainfo', '')
                        cpe = portInfo.get('cpe', '') #common platform enumeration


                        details = f" -> Port {port}: {portState.upper()}"
                        details += f" | Service: {serviceName}"
                        if product:
                            details += f" | Product: {product}"

                        if version:
                            details += f" | Version: {version}"

                        if extraInfo:
                            details += f" | Extra: {extraInfo}"

                        if cpe:
                            details += f" | CPE: {cpe}"
                        print(details)
    
    except nmap.PortScannerError as e:
        print(f"Nmap Scan error, darling: {e}. Did you forget to run with enough priviliges or something? ")
    except Exception as e:
        print(f"Something went catastrophically wrong. Maybe you suck at this. Error: {e}")
        sys.exit(1)

#actually using this pos:
if __name__ == "__main__":
    print("Note: using -sT *might* fail on Windows. So, deal with that.")
    target = input("Enter target IP or hostname: ")
    ports = input("Enter ports to scan (like '20, 443, 17' or '1-1024'): ")
    scanChoice = input("Choose a scan type (like '-sS, -sT, -O, -sV'): ")

    defaultScanType = '-sS -sV -O' #should do the sneaky thing, check the version and scan the operating system



    print("\n Initiating scan. Equipping fake moustache.")
    advancedPortScanner(target, ports, defaultScanType)

    print("\n Scan Complete. Hope you found what you were looking for i guess.")











