import sqlite3, cryptlib, os, json, base64, errno

current_directory = os.path.dirname(os.path.realpath(__file__))


class ZeroMail(object):
    def __init__(self, zeronet_directory, pub, priv):
        self.zeronet_directory = zeronet_directory
        self.pubkey = pub
        self.privkey = priv

        self.cache_directory = current_directory + "/cache/" + base64.b64encode(pub)
        try:
            os.makedirs(self.cache_directory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        self.conn = sqlite3.connect(zeronet_directory + 'data/1MaiL5gfBM1cyb4a8e3iiL8L5gXmoAJu27/data/users/zeromail.db')
        self.cursor = self.conn.cursor()

    def get_secrets(self, from_date_added=0):
        secrets = []
        for row in self.cursor.execute('SELECT encrypted, json_id, date_added FROM secret WHERE date_added > %s ORDER BY date_added DESC' % from_date_added):
            aes_key, json_id, date_added = cryptlib.eciesDecrypt(row[0], self.privkey), row[1], row[2]
            if aes_key != None:
                secrets.append([aes_key, json_id])
            from_date_added = max(from_date_added, date_added)
        return (secrets, from_date_added)
    def update_secrets(self):
        old_secrets = []
        from_date_added = 0
        try:
            with open(self.cache_directory + "/secrets.json", "r") as f:
                cache = json.loads(f.read())
                old_secrets = cache["secrets"]
                from_date_added = cache["date_added"]
        except:
            pass

        new_secrets, date_added = self.get_secrets(from_date_added)
        secrets = old_secrets + new_secrets

        with open(self.cache_directory + "/secrets.json", "w") as f:
            cache = dict(secrets=secrets, date_added=date_added)
            f.write(json.dumps(cache))

        return secrets

    def get_messages(self, secrets, from_date_added=0):
        date_added = 0

        res = dict()
        for s in secrets:
            aes_key, json_id = s[0], s[1]
            messages = self.cursor.execute('SELECT encrypted, date_added FROM message WHERE json_id = ? AND date_added > %s ORDER BY date_added DESC' % from_date_added, (json_id,))
            for m in messages:
                message = m[0].split(',')
                iv, encrypted_text = message[0], message[1]
                result = cryptlib.aesDecrypt(iv, encrypted_text, aes_key)
                if result != None:
                    res[str(m[1])] = result
                date_added = max(date_added, m[1])

        return (res, date_added)
    def update_messages(self, secrets):
        old_messages = dict()
        from_date_added = 0
        try:
            with open(self.cache_directory + "/messages.json", "r") as f:
                cache = json.loads(f.read())
                old_messages = cache["messages"]
                from_date_added = cache["date_added"]
        except:
            pass

        new_messages, date_added = self.get_messages(secrets, from_date_added)

        messages = old_messages.copy()
        messages.update(new_messages)

        with open(self.cache_directory + "/messages.json", "w") as f:
            cache = dict(messages=messages, date_added=date_added)
            f.write(json.dumps(cache))

        return messages