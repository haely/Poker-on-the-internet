# Contributors:
# Timothy Fong
# Haely Shah
# Oliver Zhu
# CMPE 209 Poker Project
import socket
from Crypto.PublicKey import RSA
import hashlib

#Declare server's attributes
server = socket.socket()
#host = "10.0.2.15"
host = "127.0.0.1"
port = 7777
#Connect to server
server.connect((host, port))

#Tell server that connection is OK for account creation
server.sendall("Account: OK")

#Receive public key string from server
server_string = server.recv(1024)

#Remove extra characters
server_string = server_string.replace("public_key=", '')
server_string = server_string.replace("\r\n", '')

#Convert string to key
server_public_key = RSA.importKey(server_string)

#Server's response if too many clients
server_response = server.recv(1024)
server_response = server_response.replace("\r\n", '')
if server_response == "Too many clients":
	print "Fail: server is currently full"
	print "Now quiting"
	server.close()
#Otherwise
elif server_response == "Ready":
	#Encrypt username and password and send to server
	#hash_user = hashlib.md5(username)
	#hash_pass = hashlib.md5(password)
	#print hash_user.hexdigest()
	#print hash_pass.hexdigest()
	username = raw_input("Username: ")
	type(username)
	password = raw_input("Password: ")
	type(password)
	#encrypted = server_public_key.encrypt(hash_user.hexdigest() + "#" + hash_pass.hexdigest(), 32)
	message = "make_account=" + username + "!@#$%^&*()" + password
	encrypted = server_public_key.encrypt(message, 32)
	server.sendall(str(encrypted))

	#Server's response
	server_response = server.recv(1024)
	server_response = server_response.replace("\r\n", '')
	if server_response == "Server: OK":
		print "Server decrypted message successfully\n"
		print "Now quiting"

		#End server thread and close program
		#server.sendall("Quit")
		encrypted = server_public_key.encrypt("Quit", 32)
		server.sendall(str(encrypted))
		#Quit server response
		print(server.recv(1024)) 
		server.close()
	else:
		print "There was an error"
		server.close()
# Contributors:
# Timothy Fong
# Haely Shah
# Oliver Zhu
# CMPE 209 Poker Project
