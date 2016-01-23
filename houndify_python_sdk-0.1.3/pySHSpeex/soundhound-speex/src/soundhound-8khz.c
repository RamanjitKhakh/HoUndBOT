#include "speex/speex.h"
#include "speex/speex_header.h"
#include <arpa/inet.h>      /* htons */
#include <string.h>

static struct {
    SpeexBits bits;
    void *enc_state;
} SH_speex;

int SH_speex_init(int quality, char *buffer, int buflen)
{
    int q = quality;

    SH_speex.enc_state = speex_encoder_init(&speex_nb_mode);
    speex_encoder_ctl(SH_speex.enc_state, SPEEX_SET_QUALITY, &q);
    speex_bits_init(&SH_speex.bits);

    SpeexHeader speex_header;
    speex_init_header(&speex_header, 8000, 1, &speex_nb_mode);

    int packet_size;
    char *packet = speex_header_to_packet(&speex_header, &packet_size);
    memcpy(buffer, packet, (buflen < packet_size) ? buflen : packet_size);

    return packet_size;
}


// Reads exactly 160 samples (20ms @ 8 Khz) (16 bit unsigned ints)
// Writes into cbits (must be at least 202 bytes)
#define FRAME_SIZE      160
int SH_speex_encode_frame(short *sFrame, char *cbits)
{
    float fFrame[FRAME_SIZE];
    for (int i=0; i < FRAME_SIZE; i++)
        fFrame[i] = (float)sFrame[i];

    speex_bits_reset(&SH_speex.bits);
    speex_encode(SH_speex.enc_state, fFrame, &SH_speex.bits);
//    speex_encode_int(SH_speex.enc_state, sFrame, &SH_speex.bits);

    int nbytes = speex_bits_write(&SH_speex.bits, cbits + 2, 200);
    unsigned short nbytes_s = (unsigned short)nbytes;
    nbytes_s = htons(nbytes_s);
    *((unsigned short *)cbits) = nbytes_s;

    return nbytes;
}
