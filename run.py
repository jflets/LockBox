import random
import string
import os
import sys
import tty
import termios

PASSWORDS_DIR = "passwords/"

def read_master_password(username):
    """
    Read the master password for the specified username.
    """
    try:
        with open(f"{PASSWORDS_DIR}{username}/master_password.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return None

def write_master_password(username, master_password):
    """
    Write the master password for the specified username.
    """
    os.makedirs(f"{PASSWORDS_DIR}{username}", exist_ok=True)
    with open(f"{PASSWORDS_DIR}{username}/master_password.txt", "w") as file:
        file.write(master_password)

def read_passwords(username):
    """
    Read the stored passwords for the specified username.
    """
    try:
        with open(f"{PASSWORDS_DIR}{username}/{username}.txt", "r") as file:
            lines = file.readlines()
            return {line.split(":")[0].strip(): line.split(":")[1].strip() for line in lines}
    except FileNotFoundError:
        return {}

def write_passwords(username, passwords):
    """
    Write the provided passwords for the specified username.
    """
    os.makedirs(f"{PASSWORDS_DIR}{username}", exist_ok=True)
    with open(f"{PASSWORDS_DIR}{username}/{username}.txt", "w") as file:
        for account, password in passwords.items():
            file.write(f"{account}: {password}\n")

def get_password_from_user():
    """
    Prompt the user to enter a password without displaying the input.
    """
    password = getpass.getpass("Enter password: ")
    input("Press Enter to continue: ")
    return password

def generate_random_password(length=12):
    """
    Generate a random password of the specified length.
    """
    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(characters) for _ in range(length))

def display_passwords(username, passwords):
    """
    Display the stored passwords for the specified username.
    """
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
    """
    Add a new password for the specified username and account.
    """
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
    """
    Remove the password for the specified username and account.
    """
    account = input("Enter the account name: ")
    passwords = read_passwords(username)
    if account in passwords:
        del passwords[account]
        write_passwords(username, passwords)
        print(f"Password for account '{account}' removed successfully.")
    else:
        print(f"No password found for account '{account}'.")

def clear_terminal():
    """
    Clear the terminal screen.
    """
    os.system('cls' if os.name == 'nt' else 'clear')

def create_new_account():
    """
    Create a new user account.
    """
    clear_terminal()  # Clear the terminal screen

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
    print(ascii_art)  # Display the ASCII art

    print("Welcome to the LockBox Password Manager!")
    print("This program allows you to manage your passwords securely.")

    username = input("Enter your desired username: ")
    if os.path.isfile(f"{PASSWORDS_DIR}{username}/{username}.txt"):
        print("Username already exists. Please choose a different username.")
        return

    master_password = getpass.getpass("Create a master password: ")  # Prompt the user to create a master password without displaying the input
    confirm_password = input("Confirm the master password: ")
    while master_password != confirm_password:
        print("Passwords do not match. Please try again.")
        master_password = getpass.getpass("Create a master password: ")
        confirm_password = input("Confirm the master password: ")

    write_master_password(username, master_password)  # Write the master password for the new user

    print("New account and master password created successfully!")

    account = input("Enter the account name for the new user: ")
    password = get_password_from_user()  # Prompt the user to enter a password without displaying the input
    passwords = {account: password}
    write_passwords(username, passwords)  # Write the password for the new account

    print(f"New account '{account}' created successfully.")
    clear_terminal()
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
            user_passwords = read_passwords(username)  # Read the stored passwords for the current user
            display_passwords(username, user_passwords)  # Display the stored passwords
        elif choice == "2":
            add_password(username)  # Add a new password for the current user
        elif choice == "3":
            remove_password(username)  # Remove a password for the current user
        elif choice == "4":
            print("Exiting Password Manager. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


def main():
    clear_terminal()  # Clear the terminal screen

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
    print(ascii_art)  # Display the ASCII art

    print("Welcome to the LockBox Password Manager!")
    print("This program allows you to manage your passwords securely.")

    new_user = input("Are you a new user? (y/n): ")
    if new_user.lower() == "y":
        create_new_account()  # Create a new user account
        return

    username = input("Enter your username: ")
    master_password = read_master_password(username)  # Read the master password for the entered username

    if master_password is None:
        print("Invalid username. Exiting Password Manager. Goodbye!")
        return

    attempts = 0
    while attempts < 2:
        entered_password = getpass.getpass("Enter your master password: ")  # Prompt the user to enter the master password without displaying the input
        if entered_password == master_password:
            clear_terminal()  # Clear the terminal screen
            print("Login successful!\n")
            break
        else:
            print("Incorrect master password. Please try again.")
            attempts += 1
    else:
        print("You have entered the wrong password multiple times.")
        choice = input("Do you want to create a new master password and account? (y/n): ")
        if choice.lower() == "y":
            create_new_account()  # Create a new user account
        else:
            print("Exiting Password Manager. Goodbye!")
            return

    while True:
        print("1. Display Passwords")
        print("2. Add Password")
        print("3. Remove Password")
        print("4. Quit")
        print("-" * 80)

        choice = input("Enter your choice (1-4): ")
        print("-" * 80)

        if choice == "1":
            user_passwords = read_passwords(username)  # Read the stored passwords for the current user
            display_passwords(username, user_passwords)  # Display the stored passwords
        elif choice == "2":
            add_password(username)  # Add a new password for the current user
        elif choice == "3":
            remove_password(username)  # Remove a password for the current user
        elif choice == "4":
            print("Exiting Password Manager. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
