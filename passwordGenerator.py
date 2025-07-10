import secrets
import string

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

def generateRandomPassword():
    printColoured("random password generator", Fore.CYAN, Style.BRIGHT)
    printColoured("generate a truly random, unguessable password...", Fore.YELLOW)

    while True:
        try:
            length = int(inputColoured("enter desired password length (e.g. 18): ", Fore.GREEN).strip())
            if length <= 0:
                printColoured("length must be a positive integer", Fore.RED)
            elif length < 8:
                printColoured("for security... maybe aim for at least 8 characters", Fore.YELLOW)
                break
            else:
                break
        except ValueError:
            printColoured("invalid input... please enter a number. not whatever that was", Fore.RED)

    while True:
        includeLowercase = inputColoured("include lowercase letters? (y/n): ", Fore.GREEN).strip().lower() == 'y'
        includeUppercase = inputColoured("include uppercase letters? (y/n): ", Fore.GREEN).strip().lower() == 'y'
        includeDigits = inputColoured("include digits? (y/n): ", Fore.GREEN).strip().lower() == 'y'
        includeSymbols = inputColoured("include standard symbols? (y/n): ", Fore.GREEN).strip().lower() == 'y'
        includeUnicode = inputColoured("include extra unicode symbols (e.g. ♥, ★, ☂)? (y/n): ", Fore.GREEN).strip().lower() == 'y'

        allCharacters = ""
        if includeLowercase:
            allCharacters += string.ascii_lowercase
        if includeUppercase:
            allCharacters += string.ascii_uppercase
        if includeDigits:
            allCharacters += string.digits
        if includeSymbols:
            allCharacters += string.punctuation
        if includeUnicode:
            unicodeSymbols = "♥★☂☀☁☃☾☽♠♣♥♦♪♫✓✗✦✧✩✪✫✬✭✮✯✰✱✲✳✴✵✶✷✸✹✺✻✼✽✾✿❀❁❂❃❄❅❆❇❈❉❊❋"
            allCharacters += unicodeSymbols

        if not allCharacters:
            printColoured("you need to select at least one character type...", Fore.RED)
        else:
            break

    passwordCharacters = []
    if includeLowercase:
        passwordCharacters.append(secrets.choice(string.ascii_lowercase))
    if includeUppercase:
        passwordCharacters.append(secrets.choice(string.ascii_uppercase))
    if includeDigits:
        passwordCharacters.append(secrets.choice(string.digits))
    if includeSymbols:
        passwordCharacters.append(secrets.choice(string.punctuation))
    if includeUnicode:
        passwordCharacters.append(secrets.choice(unicodeSymbols))

    if len(passwordCharacters) > length:
        printColoured("length is too short for the selected character types", Fore.YELLOW)
        length = len(passwordCharacters)

    remainingLength = length - len(passwordCharacters)
    passwordCharacters += [secrets.choice(allCharacters) for _ in range(remainingLength)]

    secrets.SystemRandom().shuffle(passwordCharacters)
    generatedPassword = "".join(passwordCharacters)

    printColoured(f"generated password: {generatedPassword}", Fore.MAGENTA, Style.BRIGHT)
    printColoured(f"copy this. don't write it where someone can find it: {generatedPassword}", Fore.GREEN, Style.BRIGHT)

    inputColoured("press enter to return to menu", Fore.YELLOW)

if __name__ == "__main__":
    generateRandomPassword()