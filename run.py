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

def get_password_from_user():
    password = getpass.getpass("Enter password: ")
    input("Press Enter to continue: ")
    return password

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(characters) for _ in range(length))

def display_passwords(username, passwords):
    print(f"Stored Passwords for user '{username}':")
    print()
    if passwords:
        for account, password in passwords.items():
            print(f"Account: {account}")
            print(f"Password: {password}")
            print("-" * 80)
    else:
        print("No passwords stored for this user.")
    print("-" * 80)

def add_password(username):
    account = input("Enter the account name: ")
    password_option = input("Choose an option:\n1. Enter password manually\n2. Generate random password\n")
    if password_option == "1":
        password = get_password_from_user()
    elif password_option == "2":
        length = int(input("Enter the length of the password (default is 12): ") or "12")
        password = generate_random_password(length)
    else:
        print("Invalid option. Returning to the main menu.")
        return

    passwords = read_passwords(username)
    if account in passwords:
        choice = input(f"An account with the name '{account}' already exists for the user '{username}'. Do you want to change the password? (y/n): ")
        if choice.lower() == "y":
            passwords[account] = password
            write_passwords(username, passwords)
            print(f"Password for account '{account}' changed successfully.")
        else:
            print("Returning to the main menu.")
    else:
        passwords[account] = password
        write_passwords(username, passwords)
        print(f"Password added successfully to the new account '{account}' for the user '{username}'.")
        print(f"Password: {password}")
    print("-" * 80)

def remove_password(username):
    account = input("Enter the account name: ")
    passwords = read_passwords(username)
    if account in passwords:
        del passwords[account]
        write_passwords(username, passwords)
        print(f"Password for account '{account}' removed successfully.")
    else:
        print(f"No password found for account '{account}'.")

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def create_new_account():
    clear_terminal()

    ascii_art = r"""
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

    print("Welcome to the LockBox Password Manager!")
    print("This program allows you to manage your passwords securely.")

    username = input("Enter your desired username: ")
    if os.path.isfile(f"{PASSWORDS_DIR}{username}/{username}.txt"):
        print("Username already exists. Please choose a different username.")
        return

    master_password = getpass.getpass("Create a master password: ")
    confirm_password = input("Confirm the master password: ")
    while master_password != confirm_password:
        print("Passwords do not match. Please try again.")
        master_password = getpass.getpass("Create a master password: ")
        confirm_password = input("Confirm the master password: ")

    write_master_password(username, master_password)
    print("New account and master password created successfully!")

    account = input("Enter the account name for the new user: ")
    password = get_password_from_user()
    passwords = {account: password}
    write_passwords(username, passwords)
    print(f"New account '{account}' created successfully.")
    print("-" * 80)

    # Run the program normally
    while True:
        print("1. Display Passwords")
        print("2. Add Password")
        print("3. Remove Password")
        print("4. Quit")
        print("-" * 80)

        choice = input("Enter your choice (1-4): ")
        print("-" * 80)

        if choice == "1":
            user_passwords = read_passwords(username)
            display_passwords(username, user_passwords)
        elif choice == "2":
            add_password(username)
        elif choice == "3":
            remove_password(username)
        elif choice == "4":
            print("Exiting Password Manager. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
