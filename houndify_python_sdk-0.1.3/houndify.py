##############################################################################
# Copyright 2015 SoundHound, Incorporated.  All rights reserved.
##############################################################################
from htp import *
import base64
import hashlib
import hmac
import httplib
import json
import pySHSpeex
import threading
import time
import uuid
import urllib
import zlib

HOUND_SERVER = "api.houndify.com"
TEXT_ENDPOINT = "/v1/text"


class TextHoundClient:
	"""
	TextHoundClient is used for making text queries for Hound
	"""
	def __init__(self, clientID, clientKey, userID, requestInfo = dict()):
		self.clientID = clientID
		self.userID = userID
		self.clientKey = base64.urlsafe_b64decode(clientKey)
		self.requestInfo = requestInfo
		self.conversationState = dict()
	
	def query(self, query):
		"""
		Make a text query to Hound.

		query is the string of the query
		"""
		RequestID = str(uuid.uuid4())
		headers = { 'Hound-Request-Info': json.dumps(self.requestInfo) }
		self._authentication(RequestID, headers)

		http_conn = httplib.HTTPSConnection(HOUND_SERVER)
		http_conn.request('GET', TEXT_ENDPOINT + '?query=' + urllib.quote(query), headers = headers)
		resp = http_conn.getresponse()

		return resp.read()

	def _authentication(self, requestID, headers):
		timestamp = str(int(time.time()))
		HoundRequestAuth = self.userID + ";" + requestID
		h = hmac.new(self.clientKey, HoundRequestAuth + timestamp, hashlib.sha256)
		signature = base64.urlsafe_b64encode(h.digest())
		HoundClientAuth = self.clientID + ";" + timestamp + ";" + signature

		headers['Hound-Request-Authentication'] = HoundRequestAuth
		headers['Hound-Client-Authentication'] = HoundClientAuth


class HoundListener:
	"""
	HoundListener is an abstract base class that defines the callbacks
	that can be received while streaming speech to the server
	"""
	def onPartialTranscript(self, transcript):
		"""
		onPartialTranscript is fired when the server has sent a partial transcript
		in live transcription mode.  'transcript' is a string with the partial transcript
		"""
		pass
	def onFinalResponse(self, response):
		"""
		onFinalResponse is fired when the server has completed processing the query
		and has a response.  'response' is the JSON object (as a Python dict) which
		the server sends back.
		"""
		pass
	def onTranslatedResponse(self, response):
		"""
		onTranslatedResponse is fired if the server was requested to send the JSON
		response to an external API.  In that case, this will be fired after
		onFinalResponse and contain the raw data from the external translation API
		"""
		pass
	def onError(self, err):
		"""
		onError is fired if there is an error interacting with the server.  It contains
		the parsed JSON from the server.
		"""
		pass


class StreamingHoundClient:
		"""
		StreamingHoundClient is used to send streaming audio to the Hound
		server and receive live transcriptions back
		"""
		def __init__(self, key, clientID, hostname = HOUND_SERVER, port = 4444):
			"""
			key and clientID are "Client ID" and "Client Key" from the Houndify.com
			web site.
			"""
			self.clientKey = base64.urlsafe_b64decode(key)
			self.clientID = clientID
			self.hostname = hostname
			self.port = port
			self.HoundRequestInfo = { 'ObjectByteCountPrefix': True, 'PartialTranscriptsDesired': True,
							          'ClientID': clientID }


		def setLocation(self, latitude, longitude):
			"""
			Many domains make use of the client location information to provide
			relevant results.  This method can be called to provide this information
			to the server before starting the request.

			latitude and longitude are floats (not string)
			"""
			self.HoundRequestInfo['Latitude'] = latitude
			self.HoundRequestInfo['Longitude'] = longitude
			self.HoundRequestInfo['PositionTime'] = int(time.time())


		def setHoundRequestInfo(self, key, value):
			"""
			There are various fields in the HoundRequestInfo object that can
			be set to help the server provide the best experience for the client.
			Refer to the Houndify documentation to see what fields are available
			and set them through this method before starting a request
			"""
			self.HoundRequestInfo[key] = value


		def _callback(self, listener):
			expectTranslatedResponse = False
			while True:
				try:
					msg = self.conn.ReadMessage()
					msg = zlib.decompress(msg.data, zlib.MAX_WBITS | 16)
					if expectTranslatedResponse:
						listener.onTranslatedResponse(msg)
						continue
					parsedMsg = json.loads(msg)
					if parsedMsg.has_key("Format"):
						if parsedMsg["Format"] == "SoundHoundVoiceSearchParialTranscript":
							## also check SafeToStopAudio
							listener.onPartialTranscript(parsedMsg["PartialTranscript"])
							if parsedMsg.has_key("SafeToStopAudio") and parsedMsg["SafeToStopAudio"]:
								## Because of the GIL, simple flag assignment like this is atomic
								self.audioFinished = True
						if parsedMsg["Format"] == "SoundHoundVoiceSearchResult":
							## Check for ConversationState and ConversationStateTime
							if parsedMsg.has_key("ResultsAreFinal"):
								expectTranslatedResponse = True
							if parsedMsg.has_key("AllResults"):
								for result in parsedMsg["AllResults"]:
									if result.has_key("ConversationState"):
										self.HoundRequestInfo["ConversationState"] = result["ConversationState"]
										if result["ConversationState"].has_key("ConversationStateTime"):
											self.HoundRequestInfo["ConversationStateTime"] = result["ConversationState"]["ConversationStateTime"]
							listener.onFinalResponse(parsedMsg)
					elif parsedMsg.has_key("status"):
						if parsedMsg["status"] <> "ok":
							listener.onError(parsedMsg)
					## Listen for other message types
				except:
					break


		def start(self, listener):
			"""
			This method is used to make the actual connection to the server and prepare
			for audio streaming.

			listener is a HoundListener (or derived class) object
			"""
			self.audioFinished = False
			self.buffer = ''
			self.HoundRequestInfo['RequestID'] = str(uuid.uuid4())
			self.conn = HTPConnection(self.hostname, self.port)
			htpMsg = self.conn.ReadMessage()
			challengeMsg = json.loads(htpMsg.data)
			if not challengeMsg.has_key('status') or challengeMsg['status'] <> 'ok':
				raise Exception("Error reading challenge message")

			nonce = challengeMsg['nonce']
			signature = self._authenticate(nonce)

			## Startup the listening thread (above)
			self.callbackTID = threading.Thread(target = self._callback, args = (listener,))
			self.callbackTID.start()

			self.conn.SendMessage(HTPMessage(HTPMessage.HTP_TYPE_JSON,
					json.dumps({'access_id': self.clientID, 'signature': signature, 'version': '1.1'})))
			HoundRequestInfo = json.dumps(self.HoundRequestInfo)
			gzip_compressor = zlib.compressobj(9, zlib.DEFLATED, zlib.MAX_WBITS | 16)
			msg = gzip_compressor.compress(HoundRequestInfo) + gzip_compressor.flush()
			self.conn.SendMessage(HTPMessage(HTPMessage.HTP_TYPE_BINARY, msg))

			spxHeader = pySHSpeex.Init()
			self.conn.SendMessage(HTPMessage(HTPMessage.HTP_TYPE_BINARY, spxHeader))


		def fill(self, data):
			"""
			After successfully connecting to the server with start(), pump PCM samples
			through this method.

			data is 16-bit, 16 KHz little-endian PCM samples.
			Returns True if the server detected the end of audio and is processing the data
			or False if the server is still accepting audio
			"""
			if self.audioFinished:
				# buffer gets flushed on next call to start()
				return True

			self.buffer += data
			while len(self.buffer) > 640:
				speexFrame = pySHSpeex.EncodeFrame(self.buffer[:640])
				self.conn.SendMessage(HTPMessage(HTPMessage.HTP_TYPE_BINARY, speexFrame))
				self.buffer = self.buffer[640:]

			return False


		def finish(self):
			"""
			Once fill returns True, call finish() to finalize the transaction.  finish will
			wait for all the data to be received from the server.

			After finish() is called, you can start another request with start() but each
			start() call should have a corresponding finish() to wait for the threads
			"""
			self.conn.SendMessage(HTPMessage(HTPMessage.HTP_TYPE_JSON, json.dumps({'endOfAudio': True})))
			self.callbackTID.join()


		def _authenticate(self, nonce):
			h = hmac.new(self.clientKey, nonce, hashlib.sha256)
			signature = base64.urlsafe_b64encode(h.digest())
			return signature

#
# The code below will demonstrate how to use streaming audio through Hound
#
if __name__ == '__main__':
	# We'll accept WAV files but it should be straightforward to 
	# use samples from a microphone or other source
	import wave
	import sys

	BUFFER_SIZE = 512

	if len(sys.argv) < 4:
		print "Usage: %s <client key> <client ID> <wav file> [ <more wav files> ]" % sys.argv[0]
		sys.exit(0)

	CLIENT_KEY = sys.argv[1]
	CLIENT_ID = sys.argv[2]

	#
	# Simplest HoundListener; just print out what we receive.
	#
	# You can use these callbacks to interact with your UI.
	#
	class MyListener(HoundListener):
		def onPartialTranscript(self, transcript):
			print "Partial transcript: " + transcript
		def onFinalResponse(self, response):
			print "Final response: " + str(response)
		def onTranslatedResponse(self, response):
			print "Translated response: " + response
		def onError(self, err):
			print "ERROR"

	client = StreamingHoundClient(CLIENT_KEY, CLIENT_ID)
	## Pretend we're at SoundHound HQ.  Set other fields as appropriate
	client.setLocation(37.388309, -121.973968)

	for fname in sys.argv[3:]:
		print "============== %s ===================" % fname
		audio = wave.open(fname)
		samples = audio.readframes(BUFFER_SIZE)
		finished = False
		client.start(MyListener())
		while not finished:
			finished = client.fill(samples)
			time.sleep(0.032)			## simulate real-time so we can see the partial transcripts
			samples = audio.readframes(BUFFER_SIZE)
			if len(samples) == 0:
				break
		client.finish()
