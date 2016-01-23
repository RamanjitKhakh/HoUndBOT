Python Hound SDK

Install / Build:

The SDK relies on another Python module:
- pySHSpeex handles compressing audio into SoundHound's Speex format

To build / install pySHSpeex:

cd pySHSpeex
sudo python setup.py install

(this will install it system-wide though it's possible to install it per-user
following standard Python module installation procedure)

There is some sample code to demonstrate how to use the streaming audio in the
main houndify.py module and two .wav files you can try.  There is also another
demonstration program - 'streamstdin.py' - which will take PCM samples from
stdin.  You can use it with arecord to do real-time decoding from a microphone.
e.g.

arecord -t raw -c 1 -f S16_LE -r 16000 | ./streamstdin.py <CLIENT KEY> <CLIENT ID>
