#!/usr/bin/env python3

import requests
import json
import webbrowser
import base64

#---------------------------
#Define functions
#---------------------------

def check_error(esi_response, job):
	status_code = esi_response.status_code
	
	if status_code != 200 and status_code != 204:
		#Error
		print( "Got errors!")
		print( esi_response, " ", esi_response.status_code, " " )
		print( esi_response.json() )
		#print('Failed to '+job+'. Error',esi_response.status_code,'-', esi_response.json()['error'])
		error = True
		global has_errors
		has_errors = True
	else:
		error = False
		try:
			#Try to print warning
			print('Warning',esi_response.headers['warning'])
		except KeyError:
			warning = False
	
	return error
	
	
#Code for logging in
def logging_in():
	scopes = 'esi-fittings.read_fittings.v1+esi-fittings.write_fittings.v1'
	login_url = 'https://login.eveonline.com/oauth/authorize?response_type=code&redirect_uri=http://localhost/oauth-callback&client_id='+client_id+'&scope='+scopes

	webbrowser.open(login_url, new=0, autoraise=True)

	authentication_code = input("Give your authentication code: ")
	
	combo = base64.b64encode(bytes( client_id+':'+client_secret, 'utf-8')).decode("utf-8")
	authentication_url = "https://login.eveonline.com/oauth/token"
	
	esi_response = requests.post(authentication_url, headers =  {"Authorization":"Basic "+combo}, data = {"grant_type": "authorization_code", "code": authentication_code} )
	
	if not check_error(esi_response, 'exchange authorization code for tokens'):
		response = esi_response.json()
		
		access_token = response['access_token']
		refresh_token = response['refresh_token']
		
		character_info = get_char_info(access_token)
		
		#Check if character info errored
		if character_info == 'error':
			return
			
		character_info["refresh_token"] = refresh_token

		config['characters'].append(character_info)
		
		print('Character: '+character_info['character_name']+' logged in')
		
		#Save new config
		with open('config.txt', 'w') as outfile:
			json.dump(config, outfile, indent=4)
	else:
		return
	
	return config
	
#Use refresh token to get new access token
def refresh_auth(refresh_token):
	refresh_url = 'https://login.eveonline.com/oauth/token'
	
	combo = base64.b64encode(bytes( client_id+':'+client_secret, 'utf-8')).decode("utf-8")
	esi_response = requests.post(refresh_url, headers =  {"Authorization":"Basic "+combo}, data = {"grant_type": "refresh_token", "refresh_token": refresh_token} )
	
	if not check_error(esi_response, 'refresh access token'):
		access_token = esi_response.json()['access_token']
	else:
		return 'error'

	return access_token
	
#Get info on the character by using the access token
def get_char_info(access_token):
	
	url = 'https://login.eveonline.com/oauth/verify'
	esi_response = requests.get(url, headers =  {"Authorization":"Bearer "+access_token})
	
	if not check_error(esi_response, 'get character info with access token'):
		response = esi_response.json()
		character_id = response['CharacterID']
		character_name = response['CharacterName']
		character_info = {"character_id":character_id, "character_name":character_name}
	else:
		return 'error'

	return character_info

def main_menu():
	#List saved characters
	if len(config['characters']) == 0:
		print('\nNo characters saved')
	else:
		print('\nSaved characters:')
		for n in range(0, len(config['characters'])):
			print(n, config['characters'][n]['character_name'])
			
	print('\n[S] Start deleting fits\n[D] Delete characters\n[L] Log in a character\n[R] Reset')
	user_input = input("[S/D/L/R] ")

	if user_input == 'S' or user_input == 's':
		delete_fits()
	elif user_input == 'D' or user_input == 'd':
		delete_characters()
	elif user_input == 'L' or user_input == 'l':
		print('Log in a new character.')
		logging_in()
	elif user_input == 'R' or user_input == 'r':
		reset()
	else:
		print('[R]un inporting\n[E]dit characters\n[L]og in a character')
	return

def delete_characters():
	#Edit characters and return to main menu
	if len(config['characters']) == 0:
		print('No characters to delete')
	else:
		print('\nSelect the character to delete')
		for n in range(0, len(config['characters'])):
			print(n, config['characters'][n]['character_name'])
			
		user_input = input("Character number: ")
		
		try:
			user_input = int(user_input)
			
			if user_input <= len(config['characters']):
				del config['characters'][user_input]
				#Save new config
				with open('config.txt', 'w') as outfile:
					json.dump(config, outfile, indent=4)
			else:
				print('No character', user_input)
		except ValueError:
			print('invalid input', user_input)
		
	return
	
def delete_fits():
	
	if len(config['characters']) == 0:
		print('No characters to import')
	else:
		print('Deleting fits...')
		
		#Delete all character fits one by one
		for n in range(0, len(config['characters'])):
			
			character_name = config['characters'][n]['character_name']
			character_id = config['characters'][n]['character_id']
			refresh_token = config['characters'][n]['refresh_token']
			
			print('Deleting fits from '+character_name+'...')
			
			access_token = refresh_auth(refresh_token)
			
			#Check if the access token didn't error
			if access_token == 'error':
				return
			

			
			#Import savet fits
			url = 'https://esi.evetech.net/v2/characters/'+str(character_id)+'/fittings/?datasource=tranquility'
			
			esi_response = requests.get(url, headers =  {"Authorization":"Bearer "+access_token})
			if not check_error(esi_response, 'get character skills'):
				response = esi_response.json()
				number_of_fits = len(esi_response.json())
				print(number_of_fits, 'fits to delete')
				
				
				for n2 in range(0, number_of_fits):
					fit_id = response[n]['fitting_id']
					url = 'https://esi.evetech.net/v1/characters/'+str(character_id)+'/fittings/'+str(fit_id)+'?datasource=tranquility'
					print( url )
					esi_response = requests.delete(url, headers =  {"Authorization":"Bearer "+access_token})
					
					if not check_error(esi_response, 'delete fit'):
						print(n2+1,'of',number_of_fits)
					else:
						return
					
			else:
				return
							
			
		#stop running after imported
		global run
		run = False
	
	
	return
	
def reset():
		
	config = {"client_id":'', "client_secret":'', "characters":[]}
	with open('config.txt', 'w') as outfile:
		json.dump(config, outfile, indent=4)
	
	#Resets configuration
	print('\nno client ID or secret found. \nRegister at https://developers.eveonline.com/applications to get them')
	client_id = input("Give your client ID: ")
	client_secret = input("Give your client secret: ")
	config = {"client_id":client_id, "client_secret":client_secret, "characters":[]}
	with open('config.txt', 'w') as outfile:
			json.dump(config, outfile, indent=4)
	item_id = {}
	with open('item_id.txt', 'w') as outfile:
		json.dump(item_id, outfile, indent=4)
	
	
#---------------------------
#Start the actual script now
#---------------------------

print('\nESI API importer for EFT by Hirmuolio Pine')

#Check if client ID and client secret are in the onfiguration file.
#If not ask for them and write them to the file.
try:
	config = json.load(open('config.txt'))
	
	try:
		client_id = config['client_id']
		client_secret = config['client_secret']
	except KeyError:
		print('no client ID or secret found. \nRegister at https://developers.eveonline.com/applications to get them')
		client_id = input("Give your client ID: ")
		client_secret = input("Give your client secret: ")
		config = {"client_id":client_id, "client_secret":client_secret, "characters":[]}
		with open('config.txt', 'w') as outfile:
			json.dump(config, outfile, indent=4)
		
except (IOError, json.decoder.JSONDecodeError):
	print('no client ID or secret found. \nRegister at https://developers.eveonline.com/applications to get them')
	client_id = input("Give your client ID: ")
	client_secret = input("Give your client secret: ")
	config = {"client_id":client_id, "client_secret":client_secret, "characters":[]}
	with open('config.txt', 'w') as outfile:
		json.dump(config, outfile, indent=4)

run = True
while run:
	main_menu()

print('Completed')