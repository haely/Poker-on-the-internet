# Contributors:
# Timothy Fong
# Haely Shah
# Oliver Zhu
# CMPE 209 Poker Project
import socket
from Crypto.PublicKey import RSA
from Crypto import Random
import hashlib
import os, random, struct, sys
import Crypto.Random
from Crypto.Cipher import AES
import time
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5

#Declare server's attributes
server = socket.socket()
#host = "10.0.2.15"
host = "127.0.0.1"
port = 7777
#Connect to server
server.connect((host, port))

#Tell server that connection is OK for poker game
server.sendall("Poker: GO")

#Receive public key string from server
server_string = server.recv(1024)

#Remove extra characters
server_string = server_string.replace("public_key=", '')
server_string = server_string.replace("\r\n", '')

#Convert string to key
server_public_key = RSA.importKey(server_string)
#print server_public_key.exportKey()

#Generate Client public/private key pair
random_generator = Random.new().read
client_private_key = RSA.generate(1024, random_generator)
client_public_key = client_private_key.publickey()

#Server's response if too many clients
server_response = server.recv(1024)
server_response = server_response.replace("\r\n", '')
print "server: " + server_response
#If Server occupied
if server_response == "Too many clients":
	print "Fail: server is currently full"
	print "Now quiting"
	server.close()
	sys.exit()

#Otherwise, send client's public key for asymmetric encryption
elif server_response == "Request Public Key":
	server.sendall("public_key=" + client_public_key.exportKey() + "\n")
	#print client_public_key.exportKey()

	#Login to obtain public key
	username = raw_input("Username: ")
	type(username)
	password = raw_input("Password: ")
	type(password)
	message = "encrypted_login=" + username + "!@#$%^&*()" + password

	#hashing, maybe later
	#hash_user = hashlib.md5(username)
	#hash_pass = hashlib.md5(password)
	#message = hash_user.hexdigest() + "#" + hash_pass.hexdigest() + "#" + client_public_key


	#Encrypt message
	encrypted = server_public_key.encrypt(message, 32)
	#Send Login Info to server
	server.sendall(str(encrypted))
	#Receive server reply confirming reception of username and password
	#server_response = server.recv(1024)
	#server_response = server_response.replace("\r\n", '')
	
	#Receive request for session key
	server_response = server.recv(1024)
	encrypted = eval(server_response)
	#Decrypt message
	decrypted = client_private_key.decrypt(encrypted)
	print decrypted
	#Confirm request
	if "Request Session Key" in decrypted:
		#Generate AES key and information
		AES_key = Crypto.Random.OSRNG.posix.new().read(AES.block_size)
		#print AES_key
		#Generate initialization vector
		IV = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
		#print IV
		mode = AES.MODE_CBC
		#Encrypt AES key and IV
		encrypted = server_public_key.encrypt(AES_key + "!@#$%^&*()" + IV, 32)
		#Send to server
		server.sendall(str(encrypted))
	else:
		print "nono"
		sys.exit()
	#Decryptor/Encryptor check message
	aes = AES.new(AES_key, mode, IV=IV)
	#Get Player ID
	player = ''
	server_response = server.recv(1024)
	player = aes.decrypt(server_response)
	player = player.replace("~", '')
	if player == "0":
		print "Room full"
		sys.exit()
	else:
		print "Player " + player
	
	#Poker game
	while True:
		#Ready up
		#print "type READY"

		msg = raw_input("type READY or QUIT: ")
		while msg != "READY" and msg != "QUIT":
			#print "type READY or QUIT"
			msg = raw_input("type READY or QUIT: ")
		type(msg)
		#msg = "QUIT"

		if "READY" in msg:
			print msg
			if len(msg) % 16 != 0:
				msg += '~' * (16 - len(msg) % 16)
			ciphertext = aes.encrypt(msg)
			server.sendall(ciphertext)
		elif "QUIT" in msg:
			print msg
			if len(msg) % 16 != 0:
				msg += '~' * (16 - len(msg) % 16)
			ciphertext = aes.encrypt(msg)
			server.sendall(ciphertext)
			break

		#Waiting for players
		print "SIGNAL"
		signal = ''
		while("DEALING" not in signal):
			server_response = server.recv(1024)
			signal = aes.decrypt(server_response)
			print signal
			time.sleep(1)

		#Receive a hand of cards
		server_response = server.recv(1024)
		HandofCards = aes.decrypt(server_response)
		HandofCards = HandofCards.replace("~", '')
		print HandofCards

		#Betting
		#Receive own money situation
		while True:
			#Bet Turn/Betting phase
			server_response = server.recv(1024)
			msg = aes.decrypt(server_response)
			msg = msg.replace("~", '')
			msg = msg.replace("\r\n", '')
			if "Betting" in msg:
				#money = 0
				choose = ""
				current_bet = 0
				bet = 0
				#Receive Money info
				server_response = server.recv(1024)
				msg = aes.decrypt(server_response)
				msg = msg.replace("~", '')
				msg = msg.replace("\r\n", '')
				print "Make a bet. Your money: " + msg
				money = int(msg)
				#Receive Pot info
				server_response = server.recv(1024)
				msg = aes.decrypt(server_response)
				msg = msg.replace("~", '')
				print "Pot: " + msg
				#Receive current bet value
				server_response = server.recv(1024)
				msg = aes.decrypt(server_response)
				msg = msg.replace("~", '')
				msg = msg.replace("\r\n", '')
				print "Current_bet: " + msg
				current_bet = int(msg)
				print 
				#Choose
				choose = raw_input("type BET or FOLD: ")
				type(choose)
				while choose != "BET" and choose != "FOLD":
					#print "type READY or QUIT"
					choose = raw_input("type BET or FOLD: ")
					type(choose)

				if choose == "FOLD":
					#Hash the fold
					digest = SHA256.new()
					digest.update(choose)
					#Load private key and sign message
					signer = PKCS1_v1_5.new(client_private_key)
					sig = signer.sign(digest)
					#Sign the fold with RSA private key
					signed_fold = choose + "!@#$%^&*()" + sig
					#Encrypt with AES and send to server
					if len(signed_fold) % 16 != 0:
						signed_fold += '~' * (16 - len(signed_fold) % 16)
					ciphertext = aes.encrypt(signed_fold)
					server.sendall(ciphertext)
				elif choose == "BET":
					#Input bet amount
					bet = raw_input("bet amount: ")
					type(bet)
					#Bet has to be great than or equal to the current bet
					#Bet has to be less or equal to your current money
					while(int(bet) < current_bet or int(bet) > money):
						bet = raw_input("bet amount: ")
						type(bet)
					#Round numbers if jerks type float values
					bet = int(bet)
					bet = str(bet)
		
					#Hash the bet
					digest = SHA256.new()
					digest.update(bet)
					#Load private key and sign message
					signer = PKCS1_v1_5.new(client_private_key)
					sig = signer.sign(digest)
					#Sign the bet with RSA private key
					signed_bet = bet + "!@#$%^&*()" + sig
					#Encrypt with AES and send to server
					if len(signed_bet) % 16 != 0:
						signed_bet += '~' * (16 - len(signed_bet) % 16)
					ciphertext = aes.encrypt(signed_bet)
					server.sendall(ciphertext)
			else:
				#print "You folded"
				print msg
		
			#Receive verification response
			server_response = server.recv(1024)
			msg = aes.decrypt(server_response)
			msg = msg.replace("~", '')

			if "Resend" in msg:
				print "Resending"
				if choose == "FOLD":
					#Hash the fold
					digest = SHA256.new()
					digest.update(choose)
					#Load private key and sign message
					signer = PKCS1_v1_5.new(client_private_key)
					sig = signer.sign(digest)
					#Sign the fold with RSA private key
					signed_fold = choose + "!@#$%^&*()" + sig
					#Encrypt with AES and send to server
					if len(signed_fold) % 16 != 0:
						signed_fold += '~' * (16 - len(signed_fold) % 16)
					ciphertext = aes.encrypt(signed_fold)
					server.sendall(ciphertext)
				else:
					#Hash the bet
					digest = SHA256.new()
					digest.update(bet)
					#Load private key and sign message
					signer = PKCS1_v1_5.new(client_private_key)
					sig = signer.sign(digest)
					#Sign the bet with RSA private key
					signed_bet = bet + "!@#$%^&*()" + sig
					#Encrypt with AES and send to server
					if len(signed_bet) % 16 != 0:
						signed_bet += '~' * (16 - len(signed_bet) % 16)
					ciphertext = aes.encrypt(signed_bet)
					server.sendall(ciphertext)
			else:
				#Should print No problem
				print msg
			#Check if all player's bets are the same 
			server_response = server.recv(1024)
			msg = aes.decrypt(server_response)
			msg = msg.replace("~", '')
			if "Move" in  msg:
				print msg
				break
			else:
				print msg

		#Result: Win or Lose
		server_response = server.recv(1024)
		result = aes.decrypt(server_response)
		result = result.replace("~", '')
		print result
		if "LOSE" in result:
			print "Winner Hand"
			server_response = server.recv(1024)
			winning_hand = aes.decrypt(server_response)
			winning_hand = winning_hand.replace("~", '')
			print winning_hand
	#print server_response
	#while True:
		#break
	#Tell server to finish connection
	#if message == "quit": break

#server.sendall("Quit")
print "done"
#print(server.recv(1024)) 
#Quit server response
server.close()
# Contributors:
# Timothy Fong
# Haely Shah
# Oliver Zhu
# CMPE 209 Poker Project
