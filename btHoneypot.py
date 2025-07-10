#basic bt server - listening for incoming connections
import bluetooth
import subprocess
import time

def setBluetoothName(name):
    print(f"attempting to set bluetooth name to: {name}")
    try:
        print("set bluetooth name manually ")
    except Exception as e:
        print(f"could not set bluetooth name programmatically: {e}")

#change device name if you want i guess
def runBluetoothHoneypot(device_name = "DONOTCONNECT"):
    setBluetoothName(device_name)

    #placeholder UUIDs for common services
    #real honeypot might use multiple UUIDs to mimic various services
    uuid = "00001101-0000-1000-8000-00805F9B34FB"  #serial port profile
    port = 1

    try:
        serverSock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        serverSock.bind(("", port))
        serverSock.listen(1) #listen for one connection at a time

        bluetooth.advertise_service(serverSock, device_name, uuid)

        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - bluetooth honeypot '{device_name}' listening on RFCOMM port {port} with UUID {uuid}")
        print("waiting for incoming connections...")

        clientSock, clientInfo = serverSock.accept()
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - connection from {clientInfo[0]}:{clientInfo[1]}")

        try:
            while True:
                data = clientSock.recv(1024)
                if not data:
                    break

                print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - received data: {data.decode('utf-8', errors='ignore')}")
                clientSock.send("hello from honeypot".encode('utf-8'))
        except bluetooth.btcommon.BluetoothError as e:
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - client disconnected: {e}")
        except Exception as e:
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - error during communication: {e}")
        finally:
            clientSock.close()
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - client connection closed")

    except bluetooth.btcommon.BluetoothError as e:
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - bluetooth error: {e}")
        print("ensure bluetooth service is running and adapter is up (sudo hciconfig hci0 up)")
        print("you might need to install 'pybluez' and 'libbluetooth-dev' packages...")
    except Exception as e:
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - unexpected error: {e}")
    finally:
        if 'serverSock' in locals() and serverSock:
            serverSock.close()
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - server socket closed")

if __name__ == "__main__":
    runBluetoothHoneypot("DONOTCONNECT")
    print("press ctrl + c to stop the honeypot")

