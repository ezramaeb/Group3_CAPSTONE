import discord
import requests
import time
import datetime
from replit import db
from keep_alive import keep_alive

#will return all integers in boundaries
def check(boundaries):
  try:
    return all(isinstance(int(x),int) for x in boundaries)
  except:
    return False

#crypto data gathering
def data_gathering(crypto):
	URL = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=php'
	r = requests.get(url=URL)
	data = r.json()

	#crypto and their prices in database
	for i in range(len(data)):
	    db[data[i]['id']] = data[i]['current_price']
	if crypto in db.keys():
		return db[crypto]
	else:
		return None 
		
#will return bool if var crypto is in the db
def support_status(crypto):
	if crypto in db.keys():
		return True
	else:
		return False

# start with a discord client
client = discord.Client()

@client.event
async def on_ready():
	print(f"ABG Crypto News has successfully come online")
	channel = discord.utils.get(client.get_all_channels(),name='general')
	
	await client.get_channel(channel.id).send(f"ABG Crypto News is ready for a new command! Use ***$help*** to know all the commands!")
	
@client.event #when there's a message
async def on_message(message):
	
	if message.author == client.user:
		return 
	#displaying crypto price
	if message.content.lower() in db.keys():
		await message.channel.send(f"Current price of {message.content} is: {data_gathering(message.content.lower())} PHP")
	if message.content.startswith("$help"):
		
		await message.channel.send(f".\n** [-=-=-=-=-=-COMMANDS-=-=-=-=-=-]**\n$list\n     This returns the list of available cryptocurrencies for analysis, based on the CoinGecko website’s database that refreshes regularly.\n$support <cryptocurrency>\n     This returns a boolean value of True or False, indicating whether the input is part of the list of supported cryptocurrencies.\n$converttocrypto <cryptocurrency> <ValueInPeso>\n     This converts and converts a given amount of Philippine pesos into the users’ preferred cryptocurrency.\n$converttopeso <cryptocurrency> <ValueInCrypto>\n     This converts and converts a given amount of the users’ preferred crypto currency into its Philippine pesos value.\n$buyprice <cryptocurrency> <ValueInPeso>\n     This sets a lower bound on the named cryptocurrency, waiting for it to reach that price, thus notifying the user when they should buy the coin.\n$sellprice <cryptocurrency> <ValueInPeso>\n     This sets a upper bound on the named cryptocurrency, waiting for it to reach that price, thus notifying the user when they should sell the coin.")
	#listing all coins
	if message.content.startswith("$list"):
		crypto_list = [key for key in db.keys()]
		await message.channel.send(crypto_list)
	#checks if a crypto is supported by the updater
	if message.content.startswith("$support "):
		support_check = message.content.split("$support ", 1)[1].lower()
		await message.channel.send(support_status(support_check))

  #$converttocrypto convert peso to crypto 
	if message.content.startswith('$converttocrypto '):
		messageList = message.content.split(' ')
		cryptoConcerned = messageList[1].lower()

    #converted worth 
		Worth = 0 
		Worth = int(messageList[2])/data_gathering(cryptoConcerned)

		await message.channel.send(f'The price of {messageList[2]} PHP in {messageList[1]} is {Worth}.')

  #$converttopeso convert crypto to peso 
	if message.content.startswith('$converttopeso '):
		messageList = message.content.split(' ')
		cryptoConcerned = messageList[1].lower()
	
    #converted worth 
		Worth = 0 
		Worth = int(messageList[2])*data_gathering(cryptoConcerned)

		await message.channel.send(f'The price of {messageList[2]} {messageList[1]} to Philippine Pesos is {Worth} PHP.')

	
	#buy price
	if message.content.startswith('$buyprice '):
		i=1
		messageList = message.content.split(' ')
		cryptoConcerned = messageList[1].lower()
		buyPrice = int(messageList[2])
		await message.channel.send(f"Copy! Now waiting for the bot to reach {buyPrice}")
		while data_gathering(cryptoConcerned) > buyPrice:
			now = datetime.datetime.now()
			date_time = now.strftime("%d/%m/%Y %H:%M:%S")
			seconds = int(date_time[-2:])
			sleep = 60-seconds
			await message.channel.send(f"As of check number {i}, the price has not yet reached {buyPrice}. The current price is {data_gathering(cryptoConcerned)}.")
			i +=1
			time.sleep(sleep)
			
		await message.channel.send(f"You should buy {cryptoConcerned}! It's currently at {data_gathering(cryptoConcerned)}")
	if message.content.startswith('$sellprice '):
		i=1
		messageList = message.content.split(' ')
		cryptoConcerned = messageList[1].lower()
		sellPrice = int(messageList[2])
		await message.channel.send(f"Copy! Now waiting for the bot to reach {sellPrice}")

		#essentially, it does the same thing as the buyPrice on top.
		# we loop the function at a certain time interval, so that we can lessen the load on the uptimerobot 
		# also so that we give time for the API of coingecko to update
		#while the price of the crypto is LESS than the stated sellPrice, we let it say that it still hasn't reached.
		#so, when it does become GREATER than sellPrice, it moves on to ...
		while data_gathering(cryptoConcerned) < sellPrice:
			now = datetime.datetime.now()
			date_time = now.strftime("%d/%m/%Y %H:%M:%S")
			seconds = int(date_time[-2:])
			sleep = 60-seconds
			await message.channel.send(f"As of check number {i}, the price has not yet reached {sellPrice}. The current price is {data_gathering(cryptoConcerned)}.")
			i +=1
			time.sleep(sleep)
		#... this !!! it now will say that we should sell it since it's gone up a certain amount (based on the user!)
		await message.channel.send(f"You should sell {cryptoConcerned}! It's currently at {data_gathering(cryptoConcerned)}")

		
#keeps the code running
keep_alive()

TOKEN="OTk4ODk5MzI5MDM5MzQ3ODAy.G6huFD.zaEvRTsE9nfDAWxCZHnoomE4mKp9-a2mhalSd8"
client.run(TOKEN)
