import random
import string
import os
import sys
import tty
import termios
import hashlib
from cryptography.fernet import Fernet

PASSWORDS_DIR = "passwords/"
KEY_FILE = "encryption_key.txt"


def generate_key():
    """
    Generates a new encryption key using Fernet.
    """
    return Fernet.generate_key()


def get_encryption_key():
    """
    Retrieves the encryption key from the key file.
    If the key file doesn't exist, generates a new key and saves it to the file.  # noqa
    """
    if os.path.isfile(KEY_FILE):
        with open(KEY_FILE, "rb") as key_file:
            key = key_file.read()
    else:
        key = generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
    return key


def encrypt_data(data, key):
    """
    Encrypts the provided data using the encryption key.
    """
    cipher_suite = Fernet(key)
    encrypted_data = cipher_suite.encrypt(data.encode())
    return encrypted_data


def decrypt_data(encrypted_data, key):
    """
    Decrypts the provided encrypted data using the encryption key.
    """
    cipher_suite = Fernet(key)
    decrypted_data = cipher_suite.decrypt(encrypted_data).decode()
    return decrypted_data


def read_master_password(username):
    """
    Reads and returns the master password for the given username.
    If the master password file is not found, returns None.
    """
    try:
        with open(f"{PASSWORDS_DIR}{username}/master_password.txt", "r") as file:  # noqa
            return file.read().strip()
    except FileNotFoundError:
        return None


def write_master_password(username, master_password):
    """
    Writes the hashed master password to the master password file for the given username.  # noqa
    """
    os.makedirs(f"{PASSWORDS_DIR}{username}", exist_ok=True)
    hashed_password = hash_password(master_password)
    with open(f"{PASSWORDS_DIR}{username}/master_password.txt", "w") as file:
        file.write(hashed_password)


def hash_password(password):
    """
    Hashes the provided password using SHA-256 algorithm.
    """
    return hashlib.sha256(password.encode()).hexdigest()


def read_passwords(username, key):
    """
    Reads and returns the stored passwords for the given username.
    If the passwords file is not found, returns an empty dictionary.
    """
    try:
        with open(f"{PASSWORDS_DIR}{username}/{username}.txt", "rb") as file:
            encrypted_data = file.read()
            decrypted_data = decrypt_data(encrypted_data, key)
            lines = decrypted_data.splitlines()
            return {
                line.split(":")[0].strip(): line.split(":")[1].strip()
                for line in lines
            }
    except FileNotFoundError:
        return {}


def write_passwords(username, passwords, key):
    """
    Writes the provided passwords to the passwords file for the given username.
    """
    os.makedirs(f"{PASSWORDS_DIR}{username}", exist_ok=True)
    with open(f"{PASSWORDS_DIR}{username}/{username}.txt", "wb") as file:
        data = "\n".join(
            [f"{account}: {password}" for account, password in passwords.items()]  # noqa
        )
        encrypted_data = encrypt_data(data, key)
        file.write(encrypted_data)


# Add error handling and validation to the get_password_from_user function
def get_password_from_user(prompt="Enter password: "):
    """
    Prompts the user to enter a password securely.
    """
    while True:
        password = ""
        prompt_length = len(prompt)

        # Disable terminal echoing
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setraw(fd)

        try:
            sys.stdout.write(prompt)
            sys.stdout.flush()
            while True:
                char = sys.stdin.read(1)
                if char == "\r" or char == "\n":
                    break
                elif char == "\x03":  # Handle Ctrl+C
                    raise KeyboardInterrupt
                elif char == "\x7f":  # Handle backspace
                    if len(password) > 0:
                        # Erase the last character from the password
                        password = password[:-1]
                        # Erase the asterisk displayed on the screen
                        sys.stdout.write("\b \b")
                        sys.stdout.flush()
                else:
                    password += char
                    sys.stdout.write("*")
                    sys.stdout.flush()

        finally:
            # Restore terminal settings
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        sys.stdout.write("\n")  # Move to the next line after password input
        sys.stdout.flush()

        if len(password) < 4:
            print("Password must be at least 4 characters long. Please try again.")
            continue

        if not any(char in string.punctuation for char in password):
            print("Password must contain at least 1 special character. Please try again.")
            continue

        return password


# Handle exceptions and display appropriate error messages
def display_passwords(username, passwords):
    """
    Displays the stored passwords for the given username.
    """
    print(f"Stored Passwords for user '{username}':")
    print()
    # Check if passwords dictionary is empty or contains only the master password
    if not passwords or all(account == username for account in passwords):
        print("No passwords stored for this user.")
    else:
        for account, password in passwords.items():
            if account != username:  # Exclude master password from display
                print(f"Account: {account}")
                print(f"Password: {password}")
                print("-" * 80)
    print("-" * 80)


# Add error handling and validation to the add_password function
def add_password(username):
    """
    Adds a new password for the given username and account.
    """
    account = input("Enter the site name associated with this password: ")
    password_option = input("Choose an option:\n1. Enter password manually\n2. Generate random password\n")  # noqa
    if password_option == "1":
        password = get_password_from_user()
    elif password_option == "2":
        length = int(input("Enter the length of the password (max is 14): ") or "14")  # noqa
        password = generate_random_password(length)
    else:
        print("Invalid option. Returning to the main menu.")
        return

    # Retrieve the encryption key
    key = get_encryption_key()

    passwords = read_passwords(username, key)
    if account in passwords:
        choice = input(
            f"An account with the name '{account}' already exists for the user '{username}'. "  # noqa
            "Do you want to change the password? (y/n): "
        )
        if choice.lower() == "y":
            passwords[account] = password
            write_passwords(username, passwords, key)
            print(f"Password for account '{account}' changed successfully.")
        else:
            print("Returning to the main menu.")
    else:
        passwords[account] = password
        write_passwords(username, passwords, key)
        print(f"Password added successfully to the new account '{account}' for the user '{username}'.")  # noqa
        print(f"Password: {password}")
    print("-" * 80)


# Add error handling and validation to the remove_password function
def remove_password(username):
    """
    Removes a password for the given username and account.
    """
    account = input("Enter the account name: ")
    key = get_encryption_key()
    passwords = read_passwords(username, key)
    if account in passwords:
        del passwords[account]
        write_passwords(username, passwords, key)
        print(f"Password for account '{account}' removed successfully.")
    else:
        print(f"No password found for account '{account}'.")


def clear_terminal():
    """
    Clears the terminal screen.
    """
    os.system('cls' if os.name == 'nt' else 'clear')


def generate_random_password(length=12):
    """
    Generates a random password with the specified length, enforcing a minimum length of 8 characters.
    """
    if length < 8:
        print("Minimum password length is 8 characters. Setting length to 8.")
        length = 8

    max_length = min(length, 14)  # Limit the maximum password length to 14
    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(characters) for _ in range(max_length))


def create_new_account():
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
    print("When creating a master password please ensure the following:")
    print("The password is more than 4 characters and contains 1 special character.\n")  # noqa

    # Prompt the user to enter a desired username
    username = input("Enter your desired username: ")

    while not username.strip():
        print("Username cannot be blank. Please try again.")
        username = input("Enter your desired username: ")

    if os.path.isfile(f"{PASSWORDS_DIR}{username}/{username}.txt"):
        print("Username already exists. Please choose a different username.")
        return

    # Prompt the user to create a master password without displaying the input
    master_password = get_password_from_user("Create a master password: ")

    # Prompt the user to confirm the master password
    confirm_password = get_password_from_user("Confirm the master password: ")

    while master_password != confirm_password:
        print("Passwords do not match. Please try again.")
        master_password = get_password_from_user("Create a master password: ")
        confirm_password = get_password_from_user("Confirm the master password: ")  # noqa

    # Generate or retrieve the encryption key
    key = get_encryption_key()

    # Write the master password for the new user
    write_master_password(username, master_password)

    print("New account and master password created successfully!")

    # Prompt the user to enter the account name
    account = input("Enter your account name: ")

    # Prompt the user to enter a password without displaying the input
    password = get_password_from_user("Enter password: ")

    passwords = {account: password}

    # Write the password for the new account
    write_passwords(username, passwords, key)

    print(f"New account '{account}' created successfully.")
    clear_terminal()  # Clear the terminal screen
    print("-" * 80)
    print("Menu")
    print("-" * 80)

    # Load the menu loop
    while True:
        print("1. Display Passwords")
        print("2. Add Password")
        print("3. Remove Password")
        print("4. Quit")
        print("-" * 80)

        choice = input("Enter your option (1-4): ")
        print("-" * 80)

        if choice == "1":
            # Read the stored passwords for the current user
            user_passwords = read_passwords(username, key)
            # Display the stored passwords
            display_passwords(username, user_passwords)
        elif choice == "2":
            # Add a new password for the current user
            add_password(username)
        elif choice == "3":
            # Remove a password for the current user
            remove_password(username)
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

    print(ascii_art)
    print("Welcome to the LockBox Password Manager!")
    print("This program allows you to manage your passwords securely.")

    new_user = input("Are you a new user? (y/n): ")
    while new_user.lower() not in ["y", "n"]:
        print("Invalid option. Please enter 'y' or 'n'.")
        new_user = input("Are you a new user? (y/n): ")

    if new_user.lower() == "y":
        create_new_account()  # Create a new user account
        return

    # Prompt the user to enter their username
    username = input("Enter your username: ")

    # Read the stored master password hash for the username
    stored_master_password_hash = read_master_password(username)

    if stored_master_password_hash is None:
        print("Invalid username. Exiting Password Manager. Goodbye!")
        return

    attempts = 0
    while attempts < 2:
        # Prompt the user to enter their master password without displaying the input  # noqa
        entered_password = get_password_from_user("Enter your master password: ")  # noqa
        entered_password_hash = hash_password(entered_password)

        if entered_password_hash == stored_master_password_hash:
            clear_terminal()  # Clear the terminal screen
            print("Login successful!\n")
            break
        else:
            print("Incorrect master password. Please try again.")
            attempts += 1
    else:
        print("You have entered the wrong password multiple times.")
        choice = input("Do you want to create a new master password and account? (y/n): ")  # noqa
        while choice.lower() not in ["y", "n"]:
            print("Invalid option. Please enter 'y' or 'n'.")
            choice = input("Do you want to create a new master password and account? (y/n): ")  # noqa

        if choice.lower() == "y":
            create_new_account()  # Create a new user account
        else:
            print("Exiting Password Manager. Goodbye!")
            return

    # Generate or retrieve the encryption key
    key = get_encryption_key()

    while True:
        print("1. Display Passwords")
        print("2. Add Password")
        print("3. Remove Password")
        print("4. Quit")
        print("-" * 80)

        choice = input("Enter your option (1-4): ")
        print("-" * 80)

        if choice == "1":
            # Read the stored passwords for the current user
            user_passwords = read_passwords(username, key)
            # Display the stored passwords
            display_passwords(username, user_passwords)
        elif choice == "2":
            # Add a new password for the current user
            add_password(username)
        elif choice == "3":
            # Remove a password for the current user
            remove_password(username)
        elif choice == "4":
            print("Exiting Password Manager. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
