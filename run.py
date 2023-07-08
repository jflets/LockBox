import random
import string
import getpass
import os

PASSWORDS_FILE = "passwords.txt"
MASTER_PASSWORD_FILE = "master_password.txt"

def print_ascii_art():
    ascii_art = """

888                       888      888888b.                     
888                       888      888  "88b                    
888                       888      888  .88P                    
888      .d88b.   .d8888b 888  888 8888888K.   .d88b.  888  888 
888     d88""88b d88P"    888 .88P 888  "Y88b d88""88b `Y8bd8P' 
888     888  888 888      888888K  888    888 888  888   X88K   
888     Y88..88P Y88b.    888 "88b 888   d88P Y88..88P .d8""8b. 
88888888 "Y88P"   "Y8888P 888  888 8888888P"   "Y88P"  888  888 
                                                                
    """
    print(ascii_art)

def read_master_password():
    try:
        with open(MASTER_PASSWORD_FILE, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return None

def write_master_password(master_password):
    with open(MASTER_PASSWORD_FILE, "w") as file:
        file.write(master_password)

def read_passwords():
    try:
        with open(PASSWORDS_FILE, "r") as file:
            lines = file.readlines()
            return {line.split(":")[0].strip(): line.split(":")[1].strip() for line in lines}
    except FileNotFoundError:
        return {}

def write_passwords(passwords):
    with open(PASSWORDS_FILE, "w") as file:
        for account, password in passwords.items():
            file.write(f"{account}: {password}\n")

def create_master_password():
    password = input("Create a master password: ")

    confirm_password = input("Confirm the master password: ")
    while password != confirm_password:
        print("Passwords do not match. Please try again.")
        password = input("Create a master password: ")
        confirm_password = input("Confirm the master password: ")

    write_master_password(password)
    print("Master password created successfully!")

    # Clear the master password from the terminal
    clear_terminal()

def get_password_from_user():
    password = ""
    while True:
        key = getpass.getpass("Enter the password: ")
        if key == "":
            print()
            break
        else:
            password += key
            sys.stdout.write("*")
            sys.stdout.flush()
    return password

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(characters) for _ in range(length))
