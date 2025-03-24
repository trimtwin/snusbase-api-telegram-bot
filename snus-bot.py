from aiogram import Bot, Dispatcher, types
from aiogram.types import BufferedInputFile
from aiogram.filters import Command
from aiogram.types import Message

import logging, json, time, requests, io

logging.basicConfig(level=logging.INFO)
API_TOKEN = '1111:xxxxxx' # Add Telegram bot token here

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

snusbase_auth = 'xxxxxx' # snusbase api access token goes here
snusbase_api = 'https://api.snusbase.com/'

# Snusbase API request

def snus_request(url, body=None):
	headers = {
		'Auth': snusbase_auth,
		'Content-Type': 'application/json',
	}
	method = 'POST' if body else 'GET'
	response = requests.request(method, snusbase_api + url, headers=headers, json=body)
	return response.json()

# Telegram Bot Commands

@dp.message(Command("ip"))
async def whois_cmd(message: Message):
	ip_text = message.text.split(maxsplit=1)
	ip = ip_text[1]

	ip_whois_response = snus_request('tools/ip-whois', {
		'terms': [ip],
	})
	ip_address, details = next(iter(ip_whois_response['results'].items()))

	output_text = f"IP Address: {ip_address}\n"
	output_text += "\n".join(f"{key}: {value}" for key, value in details.items())

	await message.reply(output_text)

@dp.message(Command("email"))
@dp.message(Command("username"))
@dp.message(Command("password")) # You can add Full Name, whatever else snusbase may support in the future
async def search_snus(message: Message):
	searching = message.text.split(maxsplit=1)

	type = searching[0]

	try: term =  searching[1] 
	except: await message.reply(f"Try adding a search term | {type} <input>"); return

	search_response = snus_request('data/search', {
		'terms': [term],
		'types': [type[1:]],
		'wildcard': False,
	})
	if not (size := search_response.get('size', 0)): await message.reply("Piss outta luck, No results!"); return
	
	txt_buffer = io.BytesIO()
	text_data = ""

	for breach, accounts in search_response["results"].items():
		text_data += f"Database: {breach}\n\n"
		for account in accounts:
			for key, value in account.items():
				text_data += f"{key}: {value}\n"
			text_data += "\n\n-----------------------------------------------------------------------\n\n"

	txt_buffer.write(text_data.encode("utf-8"))
	txt_buffer.seek(0)

	input_file = BufferedInputFile(txt_buffer.read(), filename="leaked_data.txt")
	await message.reply_document(input_file)


@dp.message(Command("start"))
async def send_welcome(message: Message):
	user_id = message.from_user.id
	first_name = message.from_user.first_name
	
	await message.reply(f"Welcome, {first_name}! Your ID is `{user_id}`.\nI'd Message @PhilLeotardo to get access to a 24/7 hosted bot by himself!", parse_mode="Markdown")

if __name__ == '__main__':
	import asyncio
	asyncio.run(dp.start_polling(bot))