# toolkit/passwords/cupp_generator.py

import itertools
import os
from datetime import datetime
import sys

try:
    from colorama import Fore, Style, init
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

def generateTransformations(words):
    """
    Generates various permutations and transformations of input words
    to create a comprehensive suggested password list.
    """
    wordlist = set()

    # permutations and transformations
    for wordRaw in words:
        word = str(wordRaw).strip()

        if not word:
            continue

        #basic forms/transformations
        wordLower = word.lower()
        wordUpper = word.upper()
        wordCapitalise = word.capitalize()
        wordNoSpace = word.replace(' ', '')

        wordlist.add(wordLower)
        wordlist.add(wordUpper)
        wordlist.add(wordCapitalise)
        wordlist.add(wordNoSpace)
        wordlist.add(wordNoSpace.lower())
        wordlist.add(wordNoSpace.upper())
        wordlist.add(wordNoSpace.capitalize())

        # reversals
        wordlist.add(wordLower[::-1])
        wordlist.add(wordUpper[::-1])
        wordlist.add(wordCapitalise[::-1])
        wordlist.add(wordNoSpace[::-1])

        # simple replacements
        simpleReplacements = {
            'a': ['@', '4'], 'b': ['8'], 'e': ['3'], 'i': ['1', '!'], 'o': ['0'],
            's': ['5', '$'], 't': ['7'], 'g': ['9'], 'z': ['2']
        }

        for char, replacements in simpleReplacements.items():
            if char in wordLower:
                for rep in replacements:
                    tempWord = wordLower.replace(char, rep)
                    wordlist.add(tempWord)
                    wordlist.add(tempWord.capitalize())
                    wordlist.add(tempWord.upper())
                    
        #common numbers and stuff
        current_year = datetime.now().year
        common_year_suffixes = [
            str(current_year), str(current_year)[2:],
            str(current_year - 1), str(current_year - 1)[2:],
            str(current_year + 1), str(current_year + 1)[2:]
        ]
        commonNumbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '123', '321', '00', '01']

        for baseW in [wordLower, wordCapitalise, wordNoSpace.lower()]:
            for num_suffix in commonNumbers + common_year_suffixes:
                wordlist.add(baseW + num_suffix)
                wordlist.add(num_suffix + baseW)
                wordlist.add(baseW + "_" + num_suffix)
                wordlist.add(baseW + "-" + num_suffix)
                wordlist.add(baseW.capitalize() + num_suffix)
                wordlist.add(baseW.upper() + num_suffix)

        # common symbols
        commonSymbols = ['!', '@', '#', '$', '%', '^', '&', '*', '_', '-']
        for baseW in [wordLower, wordCapitalise, wordNoSpace.lower()]:
            for sym in commonSymbols:
                wordlist.add(baseW + sym)
                wordlist.add(sym + baseW)
                wordlist.add(baseW + sym + "1")
                wordlist.add(sym + baseW + "1")
                wordlist.add(baseW + "1" + sym)

    #combinations of inputs
    primaryInputsLower = [w.lower() for w in words if w.strip()]
    
    if len(primaryInputsLower) > 1:
        for combo_pair in itertools.permutations(primaryInputsLower, 2):
            combined_word = ''.join(combo_pair)
            wordlist.add(combined_word)
            wordlist.add(combined_word.capitalize())
            wordlist.add(combined_word.upper())
            wordlist.add(combined_word[::-1])
            wordlist.add(f"{combined_word}1")
            wordlist.add(f"{combined_word}!")
            wordlist.add(f"{combined_word}{str(datetime.now().year)[2:]}")

            wordlist.add(f"{combo_pair[0]}_{combo_pair[1]}")
            wordlist.add(f"{combo_pair[0]}-{combo_pair[1]}")

    return sorted(list(wordlist))
    
#collects personal details interactively and generates a word list
def runGenerator(args):
    printColoured("welcome to the password suggestion generator!", Fore.CYAN, Style.BRIGHT)
    printColoured("this will generate a possible list of passwords based on your input", Fore.CYAN, Style.BRIGHT)

    potentialBaseWords = []
    
    # variables to store specific parsed components for new combinations
    parsedFullNameCapitalizedNoSpace = ""
    parsedBirthDay = ""
    parsedBirthMonth = ""
    parsedBirthYear = ""

    # collecting personal details
    fullName = inputColoured("target's full name (e.g., Elliot Alderson): ", Fore.YELLOW, Style.BRIGHT)
    if fullName:
        potentialBaseWords.extend(fullName.split())
        fullNameNoSpace = fullName.replace(' ', '')
        potentialBaseWords.append(fullNameNoSpace)
        potentialBaseWords.append(fullName.lower())
        potentialBaseWords.append(fullName.upper())
        potentialBaseWords.append(fullName.capitalize())
        

        parsedFullNameCapitalizedNoSpace = fullNameNoSpace.capitalize()

    nickname = inputColoured ("target's nickname: ", Fore.YELLOW, Style.BRIGHT)
    if nickname:
        potentialBaseWords.append(nickname)
        potentialBaseWords.append(nickname.replace(' ', ''))
        potentialBaseWords.append(nickname.lower())
        potentialBaseWords.append(nickname.upper())
        potentialBaseWords.append(nickname.capitalize())

    birthDate = inputColoured("target's birth date (DD/MM/YYYY): ", Fore.YELLOW, Style.BRIGHT)
    if birthDate:
        try:
            dateObj = datetime.strptime(birthDate, '%d/%m/%Y')
            potentialBaseWords.append(dateObj.strftime('%d%m%Y'))
            potentialBaseWords.append(dateObj.strftime('%Y%m%d'))
            potentialBaseWords.append(dateObj.strftime('%d-%m-%Y'))
            potentialBaseWords.append(dateObj.strftime('%Y-%m-%d'))
            potentialBaseWords.append(dateObj.strftime('%d%m'))
            potentialBaseWords.append(dateObj.strftime('%m%d'))
            
            parsedBirthDay = str(dateObj.day).zfill(2) 
            parsedBirthMonth = str(dateObj.month).zfill(2) 
            parsedBirthYear = str(dateObj.year) 
            
            potentialBaseWords.append(parsedBirthDay)
            potentialBaseWords.append(parsedBirthMonth)
            potentialBaseWords.append(parsedBirthYear)
            potentialBaseWords.append(parsedBirthYear[2:]) # Year in YY format

        except ValueError:
            printColoured("Invalid date format. Please use DD/MM/YYYY. Skipping date-based permutations.", Fore.RED)

    partnerName = inputColoured("target's partner's name: ", Fore.YELLOW, Style.BRIGHT)
    if partnerName:
        potentialBaseWords.append(partnerName)
        potentialBaseWords.append(partnerName.replace(' ', ''))
        potentialBaseWords.append(partnerName.lower())
        potentialBaseWords.append(partnerName.upper())
        potentialBaseWords.append(partnerName.capitalize())

    petName = inputColoured("target's pet's name: ", Fore.YELLOW, Style.BRIGHT)
    if petName:
        potentialBaseWords.append(petName)
        potentialBaseWords.append(petName.replace(' ', ''))
        potentialBaseWords.append(petName.lower())
        potentialBaseWords.append(petName.upper())
        potentialBaseWords.append(petName.capitalize())

    # collecting keywords
    keywords = inputColoured("any keywords (comma separated, e.g., Fsociety, EvilCorp): ", Fore.YELLOW, Style.BRIGHT)
    if keywords:
        for keyword in keywords.split(','):
            keyword = keyword.strip()
            if keyword:
                potentialBaseWords.append(keyword)
                potentialBaseWords.append(keyword.replace(' ', ''))
                potentialBaseWords.append(keyword.lower())
                potentialBaseWords.append(keyword.upper())
                potentialBaseWords.append(keyword.capitalize())
                

    specific_combinations = set()
    if parsedFullNameCapitalizedNoSpace:
        if parsedBirthYear:
            specific_combinations.add(f"{parsedFullNameCapitalizedNoSpace}{parsedBirthYear}") 
        if parsedBirthDay:
            specific_combinations.add(f"{parsedFullNameCapitalizedNoSpace}{parsedBirthDay}") 
            if parsedBirthMonth:
                specific_combinations.add(f"{parsedFullNameCapitalizedNoSpace}{parsedBirthDay}{parsedBirthMonth}") 
    
    potentialBaseWords.extend(list(specific_combinations))

    outputFile = inputColoured("output file name (leave blank for default 'suggested_passwords.txt'): ", Fore.YELLOW, Style.BRIGHT)
    if not outputFile:
        outputFile = 'suggested_passwords.txt'

    printColoured("\ngenerating password suggestions...", Fore.CYAN, Style.BRIGHT)

    finalWordlist = generateTransformations(potentialBaseWords)

    try:
        with open(outputFile, 'w', encoding='utf-8') as f:
            for word in finalWordlist:
                f.write(f"{word}\n")
        printColoured(f"\npassword suggestions saved to {outputFile}. Total entries: {len(finalWordlist)}", Fore.GREEN, Style.BRIGHT)
    except Exception as e:
        printColoured(f"error saving to file: {e}", Fore.RED, Style.BRIGHT)

    inputColoured("\npress enter to return to menu...", Fore.YELLOW, Style.BRIGHT)

if __name__ == "__main__":
    runGenerator(None)