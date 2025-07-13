import re

try:
    from colorama import Fore, Style
except ImportError:
    class Fore:
        GREEN = ''
        YELLOW = ''
        RED = ''
        CYAN = ''
        RESET = ''
    class Style:
        BRIGHT = ''
        RESET_ALL = ''

def printColoured(text, color = Fore.RESET, style = Style.RESET_ALL):
    print(f"{color}{style}{text}{Style.RESET_ALL}")

def inputColoured(prompt, color = Fore.RESET, style = Style.RESET_ALL):
    return input(f"{color}{style}{prompt}{Style.RESET_ALL}")

#tries to find the type of hash - looks at length, patterns and prefixes
def identifyHash(hashString):
    hashLength = len(hashString)
    identifiedTypes = []

    #common regex for hexadecimal strings
    isHex = bool(re.fullmatch(r'[0-9a-fA-F]+', hashString))

    #other common regex for base64 strings
    isBase64Char = bool(re.fullmatch(r'[0-9a-zA-Z+/=]+', hashString))

    #check by length and hexadecimal format
    if isHex:
        if hashLength == 32:
            identifiedTypes.append("MD5")
            identifiedTypes.append("NTLM (often 32-char hex, MD4-based)")
        elif hashLength == 40:
            identifiedTypes.append("SHA1")
        elif hashLength == 64:
            identifiedTypes.append("SHA256")
        elif hashLength == 96:
            identifiedTypes.append("SHA384")
        elif hashLength == 128:
            identifiedTypes.append("SHA512")
        elif hashLength == 16:
            identifiedTypes.append("MySQL (old password hash - 16-char hex)")
            identifiedTypes.append("DES (16-char hex)")
        elif hashLength == 48:
            identifiedTypes.append("MySQL5.x /SHA1(SHA1 hex password) (45 char hex but common to be 48 hex representation)")


    #check prefixes - strong indicator for modern hashes
    #have non hex characterss like $
    if hashString.startswith('$2a$') or hashString.startswith('$2b$') or hashString.startswith('$2y$'):
        if len(hashString) >= 60 and len(hashString) <= 61:
            identifiedTypes.append("Bcrypt")
    elif hashString.startswith('$s0$'):
        identifiedTypes.append("Scrypt")
    elif hashString.startswith('$argon2id$') or hashString.startswith ('$argon2i$'):
        identifiedTypes.append("Argon2")
    elif hashString.startswith('$P$B') and len(hashString) == 34:
        identifiedTypes.append("Wordpress (MD5 with portable hashing)")
    elif hashString.startswith('$H$') and len(hashString) == 55:
        identifiedTypes.append("PHPass (MD5/SHA256 with salt/iterations)")
    elif re.match(r'^[a-fA-F0-9]{32}:[a-fA-F0-9]{32}$', hashString):
        identifiedTypes.append("LM:NTLM (found in windows dumps)")
    elif hashString.startswith('{SSHA}'):
        identifiedTypes.append("Salted SHA - LDAP SSHA")
    elif hashString.startswith('$md5$') or hashString.startswith('$sha1$') or hashString.startswith('$sha256$') or hashString.startswith('$sha512$'):
        identifiedTypes.append("Unix crypt (salted MD5/SHA variants)")

    #fallbacks
    if not identifiedTypes:
        if hashLength > 0 and isHex:
            identifiedTypes.append("unknown hexadecimal hash (length: {})".format(hashLength))
        elif hashLength > 0 and isBase64Char:
            identifiedTypes.append("unknown base 64 like hash (length: {})".format(hashLength))
        else:
            identifiedTypes.append("could not identify: appears to be plain text or unknown format.")

    return list(set(identifiedTypes))


#main function - prompts for a hash string and prints its possible types
def runHashIdentifier(args):
    printColoured(f" hash identifier ", Fore.CYAN, Style.BRIGHT)
    printColoured(f" enter a hash string, i'll tell you what kind of digital monster it is: ", Fore.YELLOW)

    hashString = inputColoured("enter the hash string: ", Fore.GREEN).strip()

    if not hashString:
        printColoured("no hash string entered. can't identify anything...")
        inputColoured("press enter to return to menu...", Fore.YELLOW)
        return # Added return to exit if no hash is entered

    identifiedTypes = identifyHash(hashString)

    if identifiedTypes:
        printColoured(f" possible hash types: ", Fore.GREEN, Style.BRIGHT)
        for hashType in identifiedTypes:
            printColoured(f" - {hashType}", Fore.CYAN)

    else:
        printColoured(f" could not identify the hash type. it's either very obscure, or not a hash.", Fore.RED)
        printColoured(f"input: {hashString} (Length: {len(hashString)})", Fore.YELLOW)

    inputColoured("press enter to return to menu...")


runHashIdentifier(None)