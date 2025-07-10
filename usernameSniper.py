#this should scan for usernames on websites :P ---> be able to see what accounts exist with the same user name 
#prewarning some users (like me) use different usernames/ names for different sites so results may differ...
import requests
import sys
import threading
from queue import Queue

#configurations :P so popular social websites with their profile URL structures bc they are all basic af
# the {} is where the username is gonna be shoved in and tested
sitesToCheck = [
    "https://www.instagram.com/{}",
    "https://twitter.com/{}",
    "https://www.tiktok.com/@{}",
    "https://github.com/{}",
    "https://www.reddit.com/user/{}",
    "https://www.facebook.com/{}",
    "https://t.me/{}",
    "https://www.youtube.com/watch?v=CpJL3qZPnTw{}",
    "https://vimeo.com/{}",
    "https://www.pinterest.com/{}",
    "https://{}.blogspot.com",
    "https://{}.tumblr.com",
    "https://soundcloud.com/{}",
    "https://www.linkedin.com/in/{}"
]

#so it looks like a standard browser and not a python script ;)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

#threading so the program (and my laptop) doesn't explode
printLock = threading.Lock()
siteQueue = Queue()

#this is the intern, pulls a site from the queue, formats the url and checks if the username exists
def checkUsername():
    while not siteQueue.empty():
        urlTemplate = siteQueue.get()
        urlToTest = urlTemplate.format(targetUsername)

        try:
            response = requests.get(urlToTest, headers = headers, timeout = 10, allow_redirects = True)
            if response.status_code != 404: #so the username *probably* doesn't exist
                with printLock:
                    print(f"[!] Found: {urlToTest} (Status: {response.status_code})")

        except requests.exceptions.RequestException:
            pass
        finally:
            siteQueue.task_done()

def main():
    if len(sys.argv) != 2:
        print("Usage: python usernameSniper.py <username>")
        print("Example: python usernameSniper.py <elonmusk>")
        sys.exit(1)

    global targetUsername
    targetUsername = sys.argv[1]

    print(f"[*] Starting sniper run for username: '{targetUsername}'...")

    #loading all the sites in the waiting queue
    for site in sitesToCheck:
        siteQueue.put(site)

    for _ in range (20):
        thread = threading.Thread(target = checkUsername)
        thread.daemon = True
        thread.start()

    siteQueue.join()
    print("[*] Sniper run complete!")

if __name__ == "__main__":
    main()

