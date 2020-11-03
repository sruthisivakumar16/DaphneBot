import os
import json
import requests
import random
from flask import Flask, request
from dotenv import load_dotenv
from twilio.twiml.messaging_response import MessagingResponse
load_dotenv()

app = Flask(__name__)

#route for the website
@app.route("/")
def hello():
    return "Shru says hi!"

#route for where the queries get posted on the sandbox
@app.route('/vocab', methods=['POST'])

def dict():
    
    ans = ["I dont understand. Can you please rephrase the sentence?",
    "Please check the spelling.",
    "I dont get it",
    "Sorry I'm good at finding definitions for words and fetching you the weather. Other stuff, not so good.",
    "I'm sorry I dont understand that. I can only help you with vocabulary and weather.",
    "Hmm.. I dont have an answer for that.",
    "I didn't quite catch that. Let's try that again, shall we?"]

    neutral = [ "Okay!", "Awesome!","Cool", "That's great!" ,"Noice!","Alright!"]

    thank_you_msg = ["My pleasure.", "You're welcome.", "Anytime.", "That's what heroes do!" , "Glad to help.", "Dont mention it.", "No problemo."]

    goodbye = ["Tata!", "Cya later!" , "Bye Bye!" , "Adios!" ,"Au revoir!"]
    
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    message = resp.message()
    responded = False
    words = incoming_msg.split('-')

    if "hi" in incoming_msg or "hey" in incoming_msg or ("who" in incoming_msg and "you" in incoming_msg):
        help_string = create_help_message()
        message.body(help_string)
        responded = True
    
    if "weather" in incoming_msg:
    	data = return_weather(incoming_msg)
    	message.body(data)
    	responded = True
    
    if "covid" in incoming_msg:
    	corona = return_covid_stat()
    	message.body(corona)
    	responded = True
    
    elif "thank" in incoming_msg:
    	message.body(random.choice(thank_you_msg))
    	responded = True
    
    elif "bye" in incoming_msg or "later" in incoming_msg:
    	message.body(random.choice(goodbye))
    	responded = True
    
    elif "how" in incoming_msg and "you" in incoming_msg:
    	message.body("I was great. Until I started talking to you")
    	responded = True

    elif "great" in incoming_msg or "okay" in incoming_msg or "awesome" in incoming_msg or "cool" in incoming_msg:
    	message.body(random.choice(neutral))
    	responded = True

    elif "what" in incoming_msg and "doin" in incoming_msg:
    	message.body("Definitely not you.")
    	responded = True
    
    elif "how" in incoming_msg and "your" in incoming_msg and "day" in incoming_msg:
    	message.body("Depressing, just like this conversation.")
    	responded = True

    elif len(words) == 2:
        search_type = words[0].strip()
        input_string = words[1].strip().split()
        if len(input_string) == 1:
            response = get_dictionary_response(input_string[0])
            if search_type == "meaning":
                message.body(response["meaning"])
                responded = True
    
    if not responded:
        message.body(random.choice(ans))
    return str(resp)


def create_help_message():
 
    help_message = "Hey! I'm Daphne!\n\n" \
        "You can ask me the definition of any word by simply typing _meaning - word_ \n \n"\
        "You can also ask me the weather for any city by simply typing _weather - place_ \n\n"\
        "You can also ask for covid stats in India by simply typing _covid_\n\n"\
        "I swear I won't google ;)"    
    return help_message


def return_weather(place):
    words = place.split("-")
    r = data = requests.get(
        'http://api.openweathermap.org/data/2.5/weather?q=' + words[1] + '&APPID=Enter your API ID here')
    if data.json()['cod'] == 200:
        weather = data.json()['weather'][0]['description']
        loc = data.json()['name']
        msg = "The current weather forecast for " + loc + " is : " + weather
        return msg
    else:
        msg = "Please provide the correct location."
        return msg

def return_covid_stat():
# return cases in india
    r = requests.get('https://coronavirus-19-api.herokuapp.com/countries/india')
    if r.status_code == 200:
        data = r.json()
        text = f'_Covid-19 Cases in India_ \n\nConfirmed Cases : *{data["cases"]}* \n\nToday Cases : *{data["todayCases"]}* \n\nDeaths : *{data["deaths"]}* \n\nRecovered : *{data["recovered"]}* \n\n'
    else:
        text = 'I could not retrieve the results at this time, sorry.'
    return text


def get_dictionary_response(word):
    """
    Query Webster's Thesaurus API
    :param word: query's word
    :return: definitions
    """
    word_metadata = {}
    definition = "sorry, no definition is available."
    api_key = os.getenv("KEY_THESAURUS")
    url = f"https://www.dictionaryapi.com/api/v3/references/thesaurus/json/{word}?key={api_key}"
    response = requests.get(url)
    api_response = json.loads(response.text)
    if response.status_code == 200:
        for data in api_response:
            try:
                if data["meta"]["id"] == word:
                    try:
                        if len(data["meta"]["syns"]) != 0:
                            synonyms = data["meta"]["syns"][0]
                        if len(data["meta"]["ants"]) != 0:
                            antonyms = data["meta"]["ants"][0]
                        for results in data["def"][0]["sseq"][0][0][1]["dt"]:
                            if results[0] == "text":
                                definition = results[1]
                            if results[0] == "vis":
                                example = results[1][0]["t"].replace("{it}", "*").\
                                    replace("{/it}", "*")
                    except KeyError as e:
                        print(e)
            except TypeError as e:
                print(e)
            break
    word_metadata["meaning"] = definition
    return word_metadata


if __name__ == "__main__":
    app.run()
