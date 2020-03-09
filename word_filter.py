#adds a word to a master list of banned words
def ban_string(message):

	with open ("bad_words.txt", "a+") as bad:
		bad.write(message)
		bad.write('\n')
	bad.close()

#Checks the given string for particular swear words.
#I plan to update this to be a more extensive check 
#later on using reg-ex.
def banned_string(message):
	
	with open ("bad_words.txt") as bad:

		bad_words = bad.readlines()
		bad_words = [line.strip() for line in bad_words]

	bad.close()

	msg_words = message.split()
	msg_words = [line.strip() for line in msg_words]

	for word in msg_words:
		if word in bad_words:
			return True
 
	return False
