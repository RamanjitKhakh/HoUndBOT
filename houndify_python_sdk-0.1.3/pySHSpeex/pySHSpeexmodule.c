/*****************************************************************************
 * Copyright 2015 SoundHound, Incorporated.  All rights reserved.
 *****************************************************************************/
#include <Python.h>

#define SPEEX_HDR_SIZE		80

int SH_speex_init(int quality, char *buffer, int buflen);
int SH_speex_encode_frame(short *sFrame, char *cbits);

static PyObject *
pySHSpeex_SpeexInit(PyObject *self, PyObject *args)
{
	char buffer[SPEEX_HDR_SIZE];
	SH_speex_init(10, buffer, SPEEX_HDR_SIZE);

	return Py_BuildValue("s#", buffer, SPEEX_HDR_SIZE);
}


static PyObject *
pySHSpeex_SpeexEncodeFrame(PyObject *self, PyObject *args)
{
	const char *data;
	int len = 0;
	char bitsOut[202];
	if (!PyArg_ParseTuple(args, "t#", &data, &len)) {
		return NULL;
	}

	int nbytes = SH_speex_encode_frame((short*)data, bitsOut);
	return Py_BuildValue("s#", bitsOut, nbytes + 2);
}


static PyMethodDef pySHSpeexMethods[] = {
	{ "Init",	pySHSpeex_SpeexInit,	METH_VARARGS,	"Initialize speex codec and return the header bytes." },
	{ "EncodeFrame",	pySHSpeex_SpeexEncodeFrame,	METH_VARARGS,	"Encode one speex frame (320 samples) of 16-khz 16-bit audio." },
	{ NULL, NULL, 0, NULL }
};

PyMODINIT_FUNC
initpySHSpeex(void)
{
	(void)Py_InitModule("pySHSpeex", pySHSpeexMethods);
}
