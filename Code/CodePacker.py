"""
This code can be run to pack every .py-file into
a .pyenc and .pykey pair, which uses XOR One Time Pad encryption.
This can be loaded and run anywhere using the CodeLoader.
Both, CodeLoader and CodePacker are supposed to be run as a 
compiled PyInstaller .exe file for Windows.
"""

__author__ = 'Lord Inquisitor Thaddeus'
__version__ = '0.1.0'

"""
Encrypt using XOR
"""
def encrypt_code(codefile, debug=False):
    """encrypt helper function"""
    def encrypt(bytestring, key, debug=False):
        if debug:
            print("Original:")
            for ib in range(len(bytestring)):
                print(format(bytestring[ib], "02x"), end=" ")
            print("\nKey:")
            for ib in range(len(bytestring)):
                print(format(key[ib%len(key)], "02x"), end=" ")
            print("\nResult:")
        res = b""
        for ib in range(len(bytestring)):
            newbyte = bytes((bytestring[ib] ^ key[ib%len(key)],))
            res += newbyte
            if debug:
                print(format(newbyte[0], "02x"), end=" ")
        return res
    with open(codefile, 'rb') as f:
        enc_code = f.read()
    cryptokey = b""
    print("Generating Key with", len(enc_code), "Bytes")
    for ib in range(len(enc_code)):
        cryptokey += bytes((random.getrandbits(8),))
    output = encrypt(enc_code, cryptokey, debug)
    with open(codefile[:-3]+'.pykey', 'wb+') as fkey, open(codefile[:-3]+'.pyenc', 'wb+') as fcode:
        fkey.write(cryptokey)
        fcode.write(output)
    return output

"""
Load every file with a .py-ending,
generate a length-fitting key,
encrypt the file using XOR-OneTimePad
"""
def encrypt_directory(dir_path):
    assert (os.path.exists(dir_path) and os.path.isdir(dir_path)), "Directory not found."
    for filename in os.listdir(dir_path):
        if filename[-3:] == ".py":
            print("Opening", filename)
            code = encrypt_code(filename, DEBUG)
            print("Stored encrypted/packed code in file", filename[:-3]+'.pyenc')
        else:
            print("Skipping", filename)

"""
Main processes args and calls encrypt_directory depending on them
"""
if __name__ == '__main__':
    import os
    import random
    import sys
    DEBUG = False
    if len(sys.argv) <= 1:
        print("Encrypting all .py-Files in", os.getcwd())
        try:
            encrypt_directory(os.getcwd())
        except Exception as e:
            print(e)
    else:
        print("Encrypting all .py-Files in", sys.argv[0])
        try:
            encrypt_directory(sys.argv[1])
        except Exception as e:
            print(e)
    print("END")
    input()
