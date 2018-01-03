def formatDate(timestamp):
	date = datetime.datetime.fromtimestamp(timestamp / 1000)

	weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][date.weekday()]
	month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][date.month - 1]
	return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (weekday, date.day, month, date.year, date.hour, date.minute, date.second)


import os, sys, datetime, json

from config import zeronet_directory

# Load ZeroNet plugins
os.chdir(zeronet_directory)
sys.path.insert(0, os.path.join(zeronet_directory, "plugins/CryptMessage"))  # External liblary directory
sys.path.insert(0, os.path.join(zeronet_directory, "src/lib"))  # External liblary directory
sys.path.insert(0, os.path.join(zeronet_directory, "src"))  # Imports relative to src

# Guess private/public keys
import zeronet

zeroid, privatekey = zeronet.guess_private_key(zeronet_directory)
if zeroid is None:
	print "Could not access users.json"
	zeroid = raw_input("ZeroID:")
	privatekey = raw_input("Private key:")
elif privatekey is None:
	print "ZeroID:", zeroid
	privatekey = raw_input("Private key:")
else:
	print "ZeroID:", zeroid
	print "Private key:", privatekey

from zeromail import ZeroMail
zeromail = ZeroMail(zeronet_directory, zeroid=zeroid, priv=privatekey)

print "Updating secrets..."
secrets = zeromail.update_secrets()

print "Updating messages..."
messages = zeromail.update_messages(secrets)
for date, message in messages.items():
	data = json.loads(message["raw"])
	print "Date: " + formatDate(int(date))
	print "From: " + message["cert_user_id"]
	print "To: " + data["to"]
	print "Subject: " + data["subject"]
	print ""
	print data["body"]
	print ""
	print "---"
	print ""