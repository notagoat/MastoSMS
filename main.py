from flask import Flask, request
from twilio import twiml
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client

from mastodon import Mastodon

import requests

mastodon = Mastodon(
    access_token = "",
    api_base_url = "",
)

#Creds for Twillio are done via bashrc
#Use Ngrok for local forwarding for testing

ngrokaddress = ""

app = Flask(__name__)

@app.route("/sms", methods=['GET','POST'])

def sms():
	message_body = request.form['Body']
	print(request.form)
	mastodon.status_post(message_body,visibility="unlisted",spoiler_text="Hotline Message: CW Everything!!! Be Prepared!!!")
	return message_body

@app.route("/record", methods=['GET','POST'])

def record():
	r = VoiceResponse()
	r.say("Welcome to the Hell Site Hotline! Leave your message after the beep and hangup when done!")
	r.pause()
	r.say("beep")

	r.record(
		playBeep=False,
		recordingStatusCallbackEvent = 'completed',
		recordingStatusCallback = ngrokaddress + '/recording',
		method='GET',
		trim='do-not-trim',
		timeout=0
	)

	r.hangup()
	
	return str(r)

@app.route("/recording", methods=['POST'])

def recording():
	url = request.form.get('RecordingUrl')
	r = requests.get(url)
	open('recording.wav', 'wb').write(r.content)
	mediaid = mastodon.media_post('recording.wav')
	
	print(mediaid['id'])

	mastodon.status_post("This is a recording from the Mastodon Hotline!",media_ids=mediaid['id'],spoiler_text="Hotline Voice Recording: CW Everything",visibility="unlisted")
	return str(mediaid)

if __name__ == "__main__":
    app.run()