"""
This code can be run to load a fitting pair of
.pyenc and .pykey files, which will then be "decrypted" with
XOR One Time Pad, so the contained code can be compiled and run.
The .pyenc and .pykey files can be created with "CodePacker".
Both, CodeLoader and CodePacker are supposed to be run as a 
compiled PyInstaller .exe file for Windows.
"""

__version__ = '0.1.0'

import os


# Encrypt / Decrypt using XOR
def decrypt_code(codefile, keyfile, debug=False):
    # decrypt helper function
    def decrypt(bytestring, key, debug=False):
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
    enc_code = open(codefile, 'rb').read()
    cryptokey = open(keyfile, 'rb').read()
    return decrypt(enc_code, cryptokey)


# Load every file with a .pyenc-ending, then decrypt and run it.
if __name__ == '__main__':
    for filename in os.listdir(os.getcwd()):
        if filename[-6:] == ".pyenc":
            print("Opening", filename)
            code = decrypt_code(filename, filename[:-6]+'.pykey', debug=False)
            print()
            print(code.decode('utf-8'))
            print()
            comp_code = compile(code, '<string>', 'exec')
            retval = exec(comp_code)
        else:
            print("Skipping", filename)
    print("END")
    input()
