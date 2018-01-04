import json

def guess_private_key(zeronet_directory):
	try:
		with open(zeronet_directory + "data/users.json", "r") as f:
			users = json.loads(f.read())
			user = users[users.keys()[0]]

			zeroid = user["certs"]["zeroid.bit"]["auth_address"]

			try:
				zeromail = user["sites"]["1MaiL5gfBM1cyb4a8e3iiL8L5gXmoAJu27"]

				keyname = [key for key in zeromail.keys() if "encrypt_publickey" in key][0]
				publickey = zeromail[keyname]

				keyname = [key for key in zeromail.keys() if "encrypt_privatekey" in key][0]
				privatekey = zeromail[keyname]

				return (zeroid, publickey, privatekey)
			except (KeyError, TypeError):
				return (zeroid, None, None)
	except (IOError, KeyError, TypeError):
		return (None, None, None)

def guess_public_key(zeronet_directory, zeroid):
	try:
		with open(zeronet_directory + "data/1MaiL5gfBM1cyb4a8e3iiL8L5gXmoAJu27/data/users/" + zeroid + "/data.json") as f:
			data = json.loads(f.read())
			return data["publickey"]
	except (IOError, KeyError, TypeError):
		return None

def sign(address, content, zeronet_directory):
	from Site import Site
	site = Site(address, allow_create=False)

	from User import UserManager
	user = UserManager.user_manager.get()
	if user:
		privatekey = user.getAuthPrivatekey("1iD5ZQJMNXu43w1qLB8sfdHVKppVMduGz", create=False)
		if privatekey is None:
			raise TypeError("Could not find ZeroID private key")
	else:
		raise TypeError("Could not find ZeroID private key")

	site.content_manager.sign(
		inner_path=content,
		privatekey=privatekey,
		update_changed_files=True,
		remove_missing_optional=False
	)

def publish(address, content, zeronet_directory):
	# Check for lock
	from util import helper

	data_dir = zeronet_directory.replace("\\", "/") + "data"
	try:
		with helper.openLocked("%s/lock.pid" % data_dir, "w") as f:
			pass

		# Could get lock; let's run normal sitePublish then
		from src import main as zeronet_lib
		zeronet_lib.actions.sitePublish(address, inner_path=content)
	except IOError:
		# Could not get lock
		publish_socket(address, content)

def publish_socket(address, content):
	# Publish file via ZeroWebSocket
	raise NotImplementedError("Cannot publish file via ZeroWebSocket yet")