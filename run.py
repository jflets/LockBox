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


class User:
    def __init__(self, username):
        """
        Initialize a User instance with the provided username.
        """
        self.username = username

    def generate_key(self):
        """
        Generate a new encryption key using Fernet.
        """
        return Fernet.generate_key()

    def get_encryption_key(self):
        """
        Retrieve the encryption key from the file or generate a"
        " new one if it doesn't exist.
        """
        if os.path.isfile(KEY_FILE):
            with open(KEY_FILE, "rb") as key_file:
                key = key_file.read()
        else:
            key = self.generate_key()
            with open(KEY_FILE, "wb") as key_file:
                key_file.write(key)
        return key

    def read_master_password(self):
        """
        Read the hashed master password from the file if it exists.
        """
        try:
            with open(f"{PASSWORDS_DIR}{self.username}/master_password.txt",
            "r") as file:
                return file.read().strip()
        except FileNotFoundError:
            return None

    def write_master_password(self, master_password):
        """
        Write the hashed master password to the file.
        """
        os.makedirs(f"{PASSWORDS_DIR}{self.username}", exist_ok=True)
        hashed_password = self.hash_password(master_password)
        with open(f"{PASSWORDS_DIR}{self.username}/master_password.txt",
        "w") as file:
            file.write(hashed_password)

    def hash_password(self, password):
        """
        Hash the password using SHA-256.
        """
        return hashlib.sha256(password.encode()).hexdigest()

    def read_passwords(self):
        """
        Read and decrypt the user's passwords from the file.
        """
        try:
            with open(f"{PASSWORDS_DIR}{self.username}/{self.username}.txt",
            "rb") as file:
                encrypted_data = file.read()
                decrypted_data = self.decrypt_data(encrypted_data)
                lines = decrypted_data.splitlines()
                return {
                    line.split(":")[0].strip(): line.split(":")[1].strip()
                    for line in lines
                }
        except FileNotFoundError:
            return {}

    def write_passwords(self, passwords):
        """
        Write and encrypt the user's passwords to the file.
        """
        os.makedirs(f"{PASSWORDS_DIR}{self.username}", exist_ok=True)
        with open(f"{PASSWORDS_DIR}{self.username}/{self.username}.txt",
        "wb") as file:
            data = "\n".join(
                [f"{account}: {password}" for account, password in
                passwords.items()]
            )
            encrypted_data = self.encrypt_data(data)
            file.write(encrypted_data)

    def encrypt_data(self, data):
        """
        Encrypt data using the encryption key.
        """
        cipher_suite = Fernet(self.get_encryption_key())
        encrypted_data = cipher_suite.encrypt(data.encode())
        return encrypted_data

    def decrypt_data(self, encrypted_data):
        """
        Decrypt data using the encryption key.
        """
        cipher_suite = Fernet(self.get_encryption_key())
        decrypted_data = cipher_suite.decrypt(encrypted_data).decode()
        return decrypted_data

    def generate_random_password(self, length):
        """
        Generate a random password of the specified length.
        The maximum password length is limited to 14 characters.
        """
        characters = string.ascii_letters + string.digits + string.punctuation
        password = "".join(random.choice(characters) for _ in range(min(length,
        14)))
        return password
    

def remove_password(username):
    """
    Remove a password for the given username and account.
    """
    account = input("Enter the site name associated with the password"
    " you want to remove: ")

    key = User(username).get_encryption_key()

    passwords = User(username).read_passwords()
    if account in passwords:
        choice = input(
            f"Are you sure you want to remove the password for"
            " account '{account}'? (y/n): "
        )
        if choice.lower() == "y":
            del passwords[account]
            User(username).write_passwords(passwords)
            print(f"Password for account '{account}' removed successfully.")
        else:
            print("Returning to the main menu.")
    else:
        print(f"No password found for account '{account}' in"
        " the user's passwords.")
    print("-" * 80)


def get_password_from_user(prompt="Enter password: ", hide_input=True):
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
                    if hide_input:  # Hide password when adding manually
                        sys.stdout.write("*")
                        sys.stdout.flush()
                    else:
                        sys.stdout.write(char)
                        sys.stdout.flush()

        finally:
            # Restore terminal settings
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        sys.stdout.write("\n")  # Move to the next line after password input
        sys.stdout.flush()

        if len(password) < 4:
            print("Password must be at least 4 characters long. "
            "Please try again.")
            continue

        if not any(char in string.punctuation for char in password):
            print("Password must contain at least 1 special character. "
            "Please try again.")
            continue

        return password


def display_passwords(username, passwords):
    """
    Displays the stored passwords for the given username.
    """
    print(f"Stored Passwords for user '{username}':")
    print()
    if not passwords or all(account == username for account in passwords):
        print("No passwords stored for this user.")
    else:
        for account, password in passwords.items():
            if account != username:
                print(f"Account: {account}")
                print(f"Password: {password}")
                print("-" * 80)
    print("-" * 80)


def add_password(user):
    """
    Add a new password for the given username and account.
    """
    account = input("Enter the site name associated with this password: ")
    password_option = input("Choose an option:\n1. Enter password manually\n2."
    " Generate random password\n")

    if password_option == "1":
        password = get_password_from_user(prompt="Enter password: ",
        hide_input=False)
    elif password_option == "2":
        length = int(input("Enter the length of the password (max is 14): ")
        or "14")

        if length > 14:
            print("Password length exceeds the maximum limit. "
            "Generating a random password with 14 characters.")
            password = user.generate_random_password(14)
        else:
            password = user.generate_random_password(length)
    else:
        print("Invalid option. Returning to the main menu.")
        return

    key = user.get_encryption_key()

    passwords = user.read_passwords()
    if account in passwords:
        choice = input(
            f"An account with the name '{account}' already exists"
            " for the user '{user.username}'. "
            "Do you want to change the password? (y/n): "
        )
        if choice.lower() == "y":
            passwords[account] = password
            user.write_passwords(passwords)
            print(f"Password for account '{account}' changed successfully.")
        else:
            print("Returning to the main menu.")
    else:
        passwords[account] = password
        user.write_passwords(passwords)
        print(f"Password added successfully to the new account '{account}' "
        "for the user '{user.username}'.")
        print(f"Password: {password}")
    print("-" * 80)


def create_new_account():
    """
    Create a new account for a new user.
    """
    clear_terminal()

    # Display the ASCII art
    display_ascii_art()

    print("Welcome to the LockBox Password Manager!")
    print("This program allows you to manage your passwords securely.")

    username = input("Enter your desired username: ")

    while not username.strip():
        print("Username cannot be blank. Please try again.")
        username = input("Enter your desired username: ")

    if os.path.isfile(f"{PASSWORDS_DIR}{username}/{username}.txt"):
        print("Username already exists. Please choose a different username.")
        return

    master_password = get_password_from_user("Create a master password: ")
    confirm_password = get_password_from_user("Confirm the master password: ")

    while master_password != confirm_password:
        print("Passwords do not match. Please try again.")
        master_password = get_password_from_user("Create a master password: ")
        confirm_password = get_password_from_user("Confirm the master"
        " password: ")

    new_user = User(username)  # Create a new User instance for the new user
    key = new_user.get_encryption_key()

    new_user.write_master_password(master_password)

    print("New account and master password created successfully!")

    input("Press Enter key to continue to the login...")
    clear_terminal()
    # Prompt the user to log in again before accessing the main menu
    login_user = login()
    while login_user is None:
        print("Incorrect username or master password. Please try again.")
        login_user = login()

    if login_user:
        input("Press any key to continue to the main menu...")
        clear_terminal()
        main_menu(login_user)


def main_menu(user):
    """
    Display the main menu and handle user interactions.
    """
    while True:
        print("-" * 80)
        print("Menu")
        print("-" * 80)
        print("1. Display Passwords")
        print("2. Add Password")
        print("3. Remove Password")
        print("4. Quit")
        print("-" * 80)
        choice = input("Enter your option (1-4): ")
        print("-" * 80)

        if choice == "1":
            user_passwords = user.read_passwords()
            display_passwords(user.username, user_passwords)
        elif choice == "2":
            add_password(user)
        elif choice == "3":
            remove_password(user.username)
        elif choice == "4":
            print("Exiting Password Manager. Goodbye!")
            sys.exit()
        else:
            print("Invalid choice. Please try again.")


def display_ascii_art():
    """
    Display the ASCII art representing the LockBox Password Manager.
    """
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
    clear_terminal()
    print(ascii_art)


def clear_terminal():
    """
    Clears the terminal screen.
    """
    os.system('cls' if os.name == 'nt' else 'clear')


def main():
    """
    Main function that serves as the entry point to the program.
    """
    clear_terminal()

    # Display the ASCII art
    display_ascii_art()

    print("Welcome to the LockBox Password Manager!")
    print("This program allows you to manage your passwords securely.")

    new_user = input("Are you a new user? (y/n): ")
    while new_user.lower() not in ["y", "n"]:
        print("Invalid option. Please enter 'y' or 'n'.")
        new_user = input("Are you a new user? (y/n): ")

    if new_user.lower() == "y":
        create_new_account()
    else:
        user = login()
        while user is None:
            print("Incorrect username. Please try again or"
            " create a new account.")
            new_user = input("Are you a new user? (y/n): ")
            if new_user.lower() == "y":
                create_new_account()
                break
            else:
                user = login()

        if user:
            input("Press any key to continue to the main menu...")
            clear_terminal()
            main_menu(user)


if __name__ == "__main__":
    main()
