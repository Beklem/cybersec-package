import hashlib
import re
import requests

try:
    from colorama import Fore, Style
except ImportError:
    class Fore:
        GREEN = ''
        YELLOW = ''
        RED = ''
        CYAN = ''
        MAGENTA = ''
        RESET = ''
    class Style:
        BRIGHT = ''
        RESET_ALL = ''

def printColoured(text, color = Fore.RESET, style = Style.RESET_ALL):
    print(f"{color}{style}{text}{Style.RESET_ALL}")

def inputColoured(prompt, color = Fore.RESET, style = Style.RESET_ALL):
    return input(f"{color}{style}{prompt}{Style.RESET_ALL}")

#basic strength check on a password
def checkPasswordStrength(password):
    strengthScore = 0
    feedback = []

    #length check
    if len(password) < 8:
        feedback.append(f"{Fore.RED} too short: needs at least 8 characters.{Style.RESET_ALL}")
    elif 8 <= len(password) < 12:
        strengthScore += 1
        feedback.append(f"{Fore.YELLOW} decent length, but you could add more.{Style.RESET_ALL}")
    else:
        strengthScore += 2
        feedback.append(f"{Fore.GREEN} great length! {Style.RESET_ALL}")

    #character type mix
    hasLower = bool(re.search(r'[a-z]', password))
    hasUpper = bool(re.search(r'[A-Z]', password))
    hasDigit = bool(re.search(r'\d', password))
    hasSymbol = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

    charTypesCount = sum([hasLower, hasUpper, hasDigit, hasSymbol])

    if charTypesCount < 3:
        feedback.append(f"{Fore.RED} needs more character variety: try mixing lowercase, uppercase, digits, and symbols.{Style.RESET_ALL}")
    elif charTypesCount == 3:
        feedback.append(f"{Fore.YELLOW} good mix, but could use more variety.{Style.RESET_ALL}")
    else:
        strengthScore += 2
        feedback.append(f"{Fore.GREEN} excellent character variety! {Style.RESET_ALL}")

    #check simple patterns
    if re.search(r'(.)\1{2,}', password):
        feedback.append(f"{Fore.RED} avoid repeating characters like 'aaa' or '111'.{Style.RESET_ALL}")
    elif re.search(r'\d{3,}', password):
        feedback.append(f"{Fore.RED} avoid long sequences of digits like '1234'.{Style.RESET_ALL}")
    elif re.search(r'123|abc|qwerty|password', password.lower()):
        feedback.append(f"{Fore.RED} avoid common patterns like '123', 'abc', or 'qwerty'.{Style.RESET_ALL}")
    else:
        strengthScore += 1
        feedback.append(f"{Fore.GREEN} no obvious patterns found! {Style.RESET_ALL}")

    return strengthScore, feedback

    #could add more complex checks like dictionary lookups, keyboard patterns and conceptual checks

#kinda important to check if a password has been leaked in a data breach
def checkHackedPasswords(password):
    printColoured("checking if your password has been leaked in a data breach...", Fore.CYAN, Style.BRIGHT)

    sha1Hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix = sha1Hash[:5]
    suffix = sha1Hash[5:]

    hibpAPI = f"https://api.pwnedpasswords.com/range/{prefix}"

    try:
        response = requests.get(hibpAPI)
        response.raise_for_status()

        foundInBreach = False
        lines = response.text.splitlines()
        for line in lines:
            if line.startswith(suffix):
                count = int(line.split(':')[1])
                printColoured(f"{Fore.RED} your password has been found in {count} data breaches!{Style.RESET_ALL}")
                foundInBreach = True
                break

        if not foundInBreach:
            printColoured(f"{Fore.GREEN} good news! your password has not been found in any known data breaches.{Style.RESET_ALL}")

    except requests.RequestException as e:
        printColoured(f"{Fore.RED} error checking password: {e}{Style.RESET_ALL}")
        printColoured("could not connect to the breach database [haveIbeenpwned.com]", Fore.RED)
        return None
    except Exception as e:
        printColoured(f"{Fore.RED} unexpected error: {e}{Style.RESET_ALL}")
        return None
    
    return foundInBreach

#main function to run script 
def runPasswordCheck():
    printColoured("password strength checker", Fore.CYAN, Style.BRIGHT)
    printColoured("see if your password is weak, or if it's already floating in the wild...", Fore.YELLOW)

    password = inputColoured("enter a password to check: ", Fore.GREEN).strip()
    if not password:
        printColoured("no password entered... exiting.", Fore.RED)
        inputColoured("press enter to exit...", Fore.RED)
        return
    
    printColoured("checking password strength", Fore.CYAN, Style.BRIGHT)
    strengthScore, feedback = checkPasswordStrength(password)
    for item in feedback:
        printColoured(item, Fore.RESET)
        
    overallStrengthMessage = ""
    if strengthScore <= 1:
        overallStrengthMessage = f"{Fore.RED} your password is weak. consider changing it...{Style.RESET_ALL}"
    elif strengthScore == 2:
        overallStrengthMessage = f"{Fore.YELLOW} your password is decent, but you could bump up the strength a bit.{Style.RESET_ALL}"
    elif strengthScore == 3:
        overallStrengthMessage = f"{Fore.GREEN} your password is strong! {Style.RESET_ALL}"
    
    printColoured(overallStrengthMessage, Fore.RESET)
    printColoured(f"compromise check (haveIbeenPwned)", Fore.CYAN, Style.BRIGHT)
    checkHackedPasswords(password)

    inputColoured("press enter to exit...", Fore.RED)

if __name__ == "__main__":
    runPasswordCheck()
