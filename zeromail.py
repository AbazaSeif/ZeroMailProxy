import sqlite3, cryptlib

pubkey = '' # <-- Add pub_key here
privkey = '' # <-- Add encrypted_private_key here

conn = None
c = None
def connect(zeronet_directory):
    global conn, c
    conn = sqlite3.connect(zeronet_directory + 'data/1MaiL5gfBM1cyb4a8e3iiL8L5gXmoAJu27/data/users/zeromail.db')
    c = conn.cursor()

def get_secrets():
    secrets = []
    for row in c.execute('SELECT encrypted, json_id FROM secret ORDER BY date_added DESC'):
        aes_key, json_id = cryptlib.eciesDecrypt(row[0], privkey), row[1]
        if aes_key != None:
            secrets.append([aes_key, json_id])
    return secrets

def get_messages(secrets):
    res = []
    for s in secrets:
        aes_key, json_id = s[0], s[1]
        messages = c.execute('SELECT encrypted FROM message WHERE json_id = ? ORDER BY date_added DESC', (json_id,))
        for m in messages:
            message = m[0].split(',')
            iv, encrypted_text = message[0], message[1]
            result = cryptlib.aesDecrypt(iv, encrypted_text, aes_key)
            if result != None:
                res.append(result)
    return res