# -*- coding: utf-8 -*-
"""
Created on Sun Nov  8 16:24:38 2020

@author: Gareth W. Jones
"""

import argparse
from cryptography.fernet import Fernet
from getpass import getpass
from hashlib import sha256
from sys import exit

"""
This is the function that encrypts the password file.  Notice the checks involving
"DO NOT EDIT THIS LINE!!\r\n".  This is to avoid accidentally encrypting your
file multiple times, which could make decryption difficult if you are unsure
how many times it was encrypted.  Fernet will throw an exception if the incorrect
key is supplied to decrypt a file, so a try/except statement was used to handle this.
"""

def cryptPasswds(file):
    with open(file, "rb") as f:
        contents = f.read()
        if b"DO NOT EDIT THIS LINE!!" not in contents:
            try:
                key = sha256(bytes(getpass(prompt="Please enter your encryption key: "), "utf-8")).hexdigest()[:43]+"="
                enc = Fernet(key)
                check = enc.decrypt(contents)
            except:
                print("Incorrect encryption key.  Exiting...")
                exit(0)
            if b"DO NOT EDIT THIS LINE!!" in check:
                print("You are trying to double-encrypt your password file.  Exiting...")
                exit(0)
        elif  b"DO NOT EDIT THIS LINE!!" in contents:
            key = sha256(bytes(getpass(prompt="Please choose your encryption key: "), "utf-8")).hexdigest()[:43]+"="
            enc = Fernet(key)
            print("Setting up.  Please make sure you remember your encryption key!")
            encrypted = enc.encrypt(contents)
            print("Your password file is now ready.")
            print("It can only be read in cleartext using your encryption key.\n")
            print("Please run \"python gPass.py --add\" to securely add passwords to your file.")
        f.close()
    
    with open(file, "wb") as f:
        f.write(encrypted)

"""
This is the function that decrypts the file.  Again, try/except was used to handle
the exception thrown because of an incorrect key.
"""

def showPasswds(file):
    key = sha256(bytes(getpass(prompt="Please enter your encryption key: "), "utf-8")).hexdigest()[:43]+"="
    dec = Fernet(key)
    with open(file, "rb") as f:
        encrypted = f.read()
        try:
            decrypted = dec.decrypt(encrypted)
        except:
            print("Incorrect encryption key.  Exiting...")
            exit(0)
        f.close()
    
    print("Decrypted contents:")
    for i in decrypted.decode().split("\r\n"):
        if i == "DO NOT EDIT THIS LINE!!":
            continue
        print(i)

"""
This funciton allows the user to add new passwords to the file.  It first decrypts
the current contents of the file, then appends the new password to that and finally
encrypts that and writes it out to the file, overwriting the previous contents.
"""

def addPasswd(file):
    key = sha256(bytes(getpass(prompt="Please enter your encryption key: "), "utf-8")).hexdigest()[:43]+"="
    new_password = getpass(prompt="Please enter a new password to be stored: ")
    new_site = input("Please enter the service the password is being used for: ")
    enc = Fernet(key)
    with open(file, "rb") as f:
        encrypted = f.read()
        try:
            decrypted = enc.decrypt(encrypted)
        except:
            print("Incorrect encryption key.  Exiting...")
            exit(0)
        f.close()
    
    with open(file, "wb") as f:
        decrypted += b"\r\n" + new_site.encode() + ": ".encode() + new_password.encode()
        encrypted = enc.encrypt(decrypted)
        #print(decrypted)
        f.write(encrypted)
        f.close()
    print("Your new password has been added to the locker.\nPlease run \"python gPass.py --decrypt\" to view your passwords.")    
    

"""
Fernet has a function "Fernet.generate_key()" which generates a key for the user.
However, it would be much more beneficial for the user to choose their own "master
password" and then create a key from this.  It requires a 44-byte key, ending with "=".
"getpass" allows for user input without displaying it - like Linux systems.
"""

def main():
    parser = argparse.ArgumentParser(description="""Securely store your passwords. 
                                     If this is your first time using this script, please run \"python gPass.py -e\".  
                                     Please note the locker file can only be encrypted once for convenience,
                                     read the comments in the code for an explanation.""")
    parser.add_argument("-d", "--decrypt", dest="decr", 
                        help="Decrypt file to read a password.", action="store_true")
    parser.add_argument("-a", "--add", dest="add", 
                        help="Add new password to file.", action="store_true")
    parser.add_argument("-e", "--encrypt", dest="encr", 
                    help="Encrypt the locker file with an encryption key of your choosing.",
                    action="store_true")
    args = parser.parse_args()
    
    if args.decr == False and args.add == False and args.encr == False:
        parser.print_help()
        exit(0)
    elif args.decr != False and args.add == False and args.encr == False:
        showPasswds("locker.txt")
    elif args.decr == False and args.add != False and args.encr == False:
        addPasswd("locker.txt")
    elif args.decr == False and args.add == False and args.encr != False:
        cryptPasswds("locker.txt")
    else:
        print("Please specify only one argument at a time!  Exiting...")

if __name__ == "__main__":
    main()