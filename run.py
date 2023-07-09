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

def display_passwords():
    passwords = read_passwords()
    print("Stored Passwords:")
    if passwords:
        for account, password in passwords.items():
            print(f"Account: {account}")
            print(f"Password: {password}")
            print("-" * 80)
    else:
        print("No passwords stored.\n")

def add_password():
    account = input("Enter the account name: ")
    password_option = input("Choose an option:\n1. Enter password manually\n2. Generate random password\n")
    if password_option == "1":
        password = get_password_from_user()
    elif password_option == "2":
        length = int(input("Enter the length of the password (default is 12): ") or "12")
        password = generate_random_password(length)
    else:
        print("Invalid option. Returning to main menu.")
        return
    passwords = read_passwords()
    passwords[account] = password
    write_passwords(passwords)
    print(f"Password successfully added to new account called {account}.")

def remove_password():
    account = input("Enter the account name: ")
    passwords = read_passwords()
    if account in passwords:
        del passwords[account]
        write_passwords(passwords)
        print("Password removed successfully.")
    else:
        print("Password not found.")

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    # Checking terminal size
    rows, columns = os.popen('stty size', 'r').read().split()
    if int(rows) < 24 or int(columns) < 80:
        print("Please resize your terminal to at least 80x24 to use the password manager.")
        return
    
        # Displaying welcome message and ASCII art
    print()
    print("Welcome to the LockBox Password Manager!")
    print("This program allows you to manage your passwords securely.")
    print("You can store, view, add, remove passwords, and generate random passwords.")
    print("You will be asked to create a master password if you don't already have one.")
    print()
    print_ascii_art()
    print("-" * 80)

        # Reading or creating the master password
    master_password = read_master_password()
    if master_password is None:
        create_master_password()
        master_password = read_master_password()

    # Main menu loop
    while True:
        # Displaying options
        print("1. Display Passwords")
        print("2. Add Password")
        print("3. Remove Password")
        print("4. Quit")
        print("-" * 80)

        # Getting user's choice
        choice = input("Enter your choice (1-4): ")
        print("-" * 80)

        # Handling user's choice
        if choice == "1":
            display_passwords()
        elif choice == "2":
            add_password()
        elif choice == "3":
            remove_password()
        elif choice == "4":
            print("Exiting Password Manager. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

