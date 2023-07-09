import random
import string
import getpass
import os

PASSWORDS_DIR = "passwords/"

def read_master_password(username):
    try:
        with open(f"{PASSWORDS_DIR}{username}/master_password.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return None

def write_master_password(username, master_password):
    os.makedirs(f"{PASSWORDS_DIR}{username}", exist_ok=True)
    with open(f"{PASSWORDS_DIR}{username}/master_password.txt", "w") as file:
        file.write(master_password)

def read_passwords(username):
    try:
        with open(f"{PASSWORDS_DIR}{username}/{username}.txt", "r") as file:
            lines = file.readlines()
            return {line.split(":")[0].strip(): line.split(":")[1].strip() for line in lines}
    except FileNotFoundError:
        return {}

def write_passwords(username, passwords):
    os.makedirs(f"{PASSWORDS_DIR}{username}", exist_ok=True)
    with open(f"{PASSWORDS_DIR}{username}/{username}.txt", "w") as file:
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
    print()
    if passwords:
        for account, password in passwords.items():
            print(f"Account: {account}")
            print(f"Password: {password}")
            print("-" * 80)
    else:
        print("No passwords stored.\n")
        print("-" * 80)

def add_password():
    account = input("Enter the account name: ")
    passwords = read_passwords()
    if account in passwords:
        print("An account with that name already exists.")
        choice = input("Do you want to change the password? (y/n): ")
        if choice.lower() == "y":
            password_option = input("Choose an option:\n1. Enter password manually\n2. Generate random password\n")
            if password_option == "1":
                password = get_password_from_user()
            elif password_option == "2":
                length = int(input("Enter the length of the password (default is 12): ") or "12")
                password = generate_random_password(length)
            else:
                print("Invalid option. Returning to main menu.")
                return
            passwords[account] = password
            write_passwords(passwords)
            print(f"Password for account '{account}' has been changed successfully.")
        else:
            print("Returning to main menu.")
    else:
        password_option = input("Choose an option:\n1. Enter password manually\n2. Generate random password\n")
        if password_option == "1":
            password = get_password_from_user()
        elif password_option == "2":
            length = int(input("Enter the length of the password (default is 12): ") or "12")
            password = generate_random_password(length)
        else:
            print("Invalid option. Returning to main menu.")
            return
        passwords[account] = password
        write_passwords(passwords)
        print(f"Password successfully added to new account called '{account}'.")
    
    print()
    print("-" * 80)


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

if __name__ == "__main__":
    main()