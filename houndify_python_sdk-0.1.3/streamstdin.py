#!/usr/bin/env python

import houndify
import sys

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print "Usage: %s <CLIENT_KEY> <CLIENT_ID>" % sys.argv[0]
		sys.exit(0)

	CLIENT_KEY = sys.argv[1]
	CLIENT_ID = sys.argv[2]

	#
	# Simplest HoundListener; just print out what we receive.
	#
	# You can use these callbacks to interact with your UI.
	#
	class MyListener(houndify.HoundListener):
		def onPartialTranscript(self, transcript):
			print "Partial transcript: " + transcript
		def onFinalResponse(self, response):
			print "Final response: " + str(response)
		def onTranslatedResponse(self, response):
			print "Translated response: " + response
		def onError(self, err):
			print "ERROR"

	client = houndify.StreamingHoundClient(CLIENT_KEY, CLIENT_ID)
	## Pretend we're at SoundHound HQ.  Set other fields as appropriate
	client.setLocation(37.388309, -121.973968)

	BUFFER_SIZE = 512
	samples = sys.stdin.read(BUFFER_SIZE)
	finished = False
	client.start(MyListener())
	while not finished:
		finished = client.fill(samples)
		samples = sys.stdin.read(BUFFER_SIZE)
		if len(samples) == 0:
			break
	client.finish()
