"""
.       - Any Character Except New Line

\d      - Digit (0-9)

\D      - Not a Digit (0-9)

\w      - Word Character (a-z, A-Z, 0-9, _)

\W      - Not a Word Character

\s      - Whitespace (space, tab, newline)

\S      - Not Whitespace (space, tab, newline)



\b      - Word Boundary

\B      - Not a Word Boundary

^       - Beginning of a String

$       - End of a String



[]      - Matches Characters in brackets

[^ ]    - Matches Characters NOT in brackets

|       - Either Or

( )     - Group



Quantifiers:

*       - 0 or More

+       - 1 or More

?       - 0 or One

{3}     - Exact Number

{3,4}   - Range of Numbers (Minimum, Maximum)

"""


import os
from typing import List
from colorama import init, Fore, Back
import re

setup_dir = "d:\Development\SexyBot"#os.getcwd()[:-12]

ignore = ["Database"]

def get_packages(files: list) -> list:
    packages: List[str] = []
    content_list: List[str] = []

    for file in files:
        with open(file, errors="ignore", encoding="utf8") as f:
            content_list.append(f.read())

    content = "\n\n".join(content_list)

    regex = r"^(import|from) (.+\s)"

    pattern: re.Pattern = re.compile(regex, re.MULTILINE)

    matches_re = pattern.finditer(content)
    matches: List[str] = []

    for match in matches_re:
        matches.append(content[match.span()[0]:match.span()[1]])

    for match_s in matches:
        if "from " in match_s:
            packages.append(match_s.split("from ")[1].split(" import ")[0]) 
        else:
            packages.append(match_s.split("import ")[1].split(" as ")[0])

    for index, match_s in enumerate(packages):
        if match_s.endswith("\n"):
            packages[index] = match_s.strip("\n")
        if "," in match_s:
            packages.pop(index)
                
    packages_filtered: List[str]= []

    for package in packages:
        if package not in packages_filtered:
            packages_filtered.append(package)

    for package in packages_filtered:
        if package in get_filenames(files=files):
            packages_filtered.remove(package)

    with open("packages.txt", 'w') as f:
        f.write("\n".join(packages_filtered))

    return packages_filtered

def get_files(DIR: str, files: list) -> list:

    for file in os.listdir(DIR):
        is_folder = file.split(".")[0] == file 
        is_cache = file.startswith("__") and file.endswith("__") or file != "opus"

        if file.endswith(".py"):
            files.append(DIR + "\\" + file)

        elif is_folder and not is_cache:
                get_files(DIR + "\\" + file, files)

    for file in files:
        for ignored in ignore:
            if f"\\{ignored}\\" in file:
                files.remove(file)

    return files

def get_filenames(files: list) -> list:
    filenames: List[str] = []

    for file in files:
        filenames.append(os.path.basename(file)[:-3])

    return filenames

def install_packages(file):
    with open("packages.txt") as f:
        packages = f.readlines()

    for package in packages:
        os.system(f"pip install {package}")

files = get_files(setup_dir, [])

packages = get_packages(files)

print("Please reveiw the contents of packages.txt")
os.startfile("packages.txt")

valid_response = False
responses = {"no": False, "yes": True, "yea": True, "perhaps": True, "nop": False, "nope": False}

while not valid_response:
    response = input("Install packages from packages.txt?: ")

    if response in responses:
        response_bool = responses[response]
        valid_response = True
    else:
        print("Invalid response")
        valid_response = False

init(convert=True)

if response_bool:
    install_packages(os.getcwd() + "\\" + "packages.txt")

    print(Fore.BLACK + Back.GREEN + "DONE, packages installed.")
else:
    init(convert=True)
    print(Fore.BLACK + Back.CYAN + "DONE, packages not installed.")

print(Fore.WHITE+Back.BLACK)