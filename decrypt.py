from cryptography.fernet import Fernet

key = ""

system_information_e = "e_systems.txt"
clipboard_information_e = "e_clipboard.txt"
keys_information_e = "e_key_log.txt"

file_path = ""
extend = "\\"
file_merge = file_path + extend

encrypted_files = [system_information_e, clipboard_information_e, keys_information_e]
count = 0

for decrypting_file in encrypted_files:
    with open(file_merge + encrypted_files[count], 'rb') as f:
        data = f.read()

    fernet = Fernet(key)
    decrypted = fernet.decrypt(data)

    with open("decryption.txt", 'ab') as f:
        f.write(decrypted)

    count += 1
