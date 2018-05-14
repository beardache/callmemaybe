from flask import Flask, request, make_response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import re
from functools import wraps

config = {
	'twilio': {'sid':'', 'authToken':''},
	'HTTPBasicAuth': {'user':'', 'password':''},
	'phoneNumber': ''
}

client = Client(config["twilio"]["sid"], config["twilio"]["authToken"])
app = Flask(__name__)

def authRequired(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		auth = request.authorization
		if auth and auth.username == config["HTTPBasicAuth"]["user"] and auth.password == config["HTTPBasicAuth"]["password"]:
			return f(*args, **kwargs)
		return make_response('Could not verify login details!', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

	return decorated


def parsePhoneNumber(_):
	results = []
	regex = r"\(?\b[2-9][0-9]{2}\)?[-. ]?[2-9][0-9]{2}[-. ]?[0-9]{4}\b"
	matches = re.findall(regex, _)

	for i in matches:
		results.append(re.sub('[^0-9]+', '', i))

	return results

def makeOutbound(requestUrl, toPhone):
	for numbers in toPhone:
		print numbers
		call = client.calls.create(
	                        url=requestUrl,
	                        from_=config["phoneNumber"],
	                        to="+1{}".format(numbers)
                    )

def getReply(message, baseUrl):
	message = message.lower()
	response = None
	default_response = "Not sure what you mean."

	if message.startswith("hacktheplanet"):
		makeOutbound("{}static/xml/hackThePlanet.xml".format(baseUrl), parsePhoneNumber(message))
		response = "HACK THE PLANET!"

	if message.startswith("allthethings"):
		makeOutbound("{}static/xml/hackAllTheThings.xml".format(baseUrl), parsePhoneNumber(message))
		response = "Don't drink and hack!"

	if message.startswith("RussiaWithLove"):
		makeOutbound("{}static/xml/russiaWithLove.xml".format(baseUrl), parsePhoneNumber(message))
		response = "For mother Russia!"

	if message.startswith("rickroll"):
		makeOutbound("{}static/xml/rickRoll.xml".format(baseUrl), parsePhoneNumber(message))
		response = "Never gonna give you up!"

	if message.startswith("conference"):
			makeOutbound("{}static/xml/conference.xml".format(baseUrl), parsePhoneNumber(message))
			response = "Beaming up for a conference!"

	if message.startswith("helpme"):
		response = "hackThePlanet, allthethings, russiaWithLove, rickroll"

	return response or default_response


@app.route("/", methods=['POST'])
@authRequired
def sms():
	message_body = request.form['Body']
	resp = MessagingResponse()

	replyText = getReply(message_body, request.base_url)
	resp.message(replyText)
	return str(resp)

@app.route('/static/<path:path>', methods=['POST', 'GET'])
def staticFile(path):
	return app.send_static_file(path)


if __name__ == '__main__':
	app.run(host="0.0.0.0", port=5000, debug=True)
