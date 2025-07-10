#script is a detective (or fbi profiler like John Douglas if you will), visits target URl and answers the question "What even are you?"
# Douglas interrogates the server, reading its public mail, and looks for manufacturer labels

import requests
import sys
import re
from bs4 import BeautifulSoup

#*configurations YAY
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

#dictionary of clues, need to update this so its *more effective*
theClues = {
    "WordPress": {
        #check if paths exist...
        "paths": ["/wp-login.php", "/wp-admin/"],
        #checking meta tags in the html that scream "im made in framer!", "im made in wordpress"
        "metaTags": [{"name": "generator","content": "Wordpress"}]
    },
        "Joomla": {
        "paths": ["/administrator/"],
        "metaTags": [{"name": "generator","content": "Joomla!"}]
    },
        "Durpal": {
        "paths": ["/user/login"],
        "htmlContent": ["sites/default/files"]
    }
}

#the interrogation. beloved john douglas is sitting down with the server and is GRILLING him for info
def douglasHeaders(targetUrl):
    print("[*] Analysing HTTP Headers :P")
    
    try:
        response = requests.get(targetUrl, headers=headers, timeout=10)

        #server header tells us about the web server stuff
        server = response.headers.get("Server")
        if server:
            print(f"[*] Server: {server}")

        #the x powered by usually tells you what backend tech it has
        poweredBy = response.headers.get('X-Powered-By')
        if poweredBy:
            print(f"[*] X-Powered-By: {poweredBy}")

        #checks security headers - these can be a vulnerability itself
        if 'Strict-Transport-Security' not in response.headers:
            print(f"[*] Security Warning: Missing 'Strict-Transport-Security' (HSTS) header")
        if 'Content-Security-Policy' not in response.headers:
            print(f"[*] Security Warning: Missing 'Content Security Policy' (CSP) header")
        if 'X-Frame-Options' not in response.headers:
            print(f"[*] Security Warning: Missing 'X-Frame-Options' (Clickjacking risk).")

    except requests.exceptions.RequestException as e:
        print(f"[!] Could not connect to {targetUrl}: {e}")
        return None

    return response

#douglas is reading diaries, robots.txt is a list of *secrets*******
def douglasRobotsTxt(targetUrl):
    robotsUrl = f"{targetUrl}/robots.txt"
    print(f"\n[*] Checking {robotsUrl} for secrets....")

    try:
        response = requests.get(robotsUrl, headers = headers, timeout = 5)
        if respnse.status_code == 200:
            print("[!] Found robots.txt. Looking for interesting 'disallow' entries: ")
            disallowedPaths = re.findall(r"Disallow: (.*)", response.text)
            if disallowedPaths:
                for path in disallowedPaths:
                    print(f"[!] Found disallowed Path: {path.strip()}")
            else:
                print(f"[*] No interesting entries found :O")
        else:
            print("[*] robots.txt not found or not accessible...")
    except requests.exception.RequestException:
        pass

#profile the target...
def fingerprintCms(response):
    if not response:
        return

    print("\n[*] Fingerprinting the CMS and Framework...")
    soup = BeautifulSoup(response.text, 'html.parser')

    #ceo of checking meta tags
    for the, clues in theClues.items(): 
        if "metaTags" in clues:
            for tagClue in clues["metaTags"]:
                foundTag = soup.find('meta', attrs = tagClue)
                if foundTag:
                    print(f"[!] Found Something! The meta tag indicates this is a {tech} site.")
                    return

    print("[*] Couldn't identify a common CMS from the HTML...")

def main():
    if len(sys.argv) != 2:
        print("Example: python techProfiler.py https:www.tesla.com")
        sys.exit(1)

    targetUrl = sys.argv[1].rstrip('/')
    print(f"\n .... Starting Tech Profile for {targetUrl} .... ")
    initialResponse = douglasHeaders(targetUrl)

    if initialResponse:
        fingerprintCms(initialResponse)
        douglasRobotsTxt(targetUrl)

    print("\n .... Profile Complete ....")

if __name__ == "__main__":
    main()
































