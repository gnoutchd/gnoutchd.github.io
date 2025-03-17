#!/usr/bin/env python3

import urllib.request
import urllib.parse
import io
from itertools import cycle
from base64 import b64decode
from operator import xor

# see http://stackoverflow.com/questions/120951/how-can-i-normalize-a-url-in-python
def norm_url(orig_url):
    '''
    Bring the given URL closer to standard.

    Returns the given URL with some basic quoting-related repairs done, which
    hopefully will make its retrieval more reliable.
    '''
    scheme, netloc, path_s, query_s, fragment = urllib.parse.urlsplit(orig_url)
    path = urllib.parse.unquote(path_s)
    query = urllib.parse.parse_qs(query_s)

    return urllib.parse.urlunsplit((
        scheme,
        netloc,
        urllib.parse.quote(path),
        urllib.parse.urlencode(query, doseq=True),
        fragment))

def get_response_body(url, referer=None):
    request = urllib.request.Request(norm_url(url))
    if referer:
        request.add_header('Referer', referer)
    response = urllib.request.urlopen(request)
    response_meta = response.info()
    if response_meta.get_content_maintype() == 'text':
        charset = response_meta.get_content_charset(failobj='ISO-8859-1')
        return io.TextIOWrapper(response, charset)
    else:
        return response

def str_extract(text, prefix, suffix):
    '''
    Extract a substring flanked by the given prefix and suffix.

    Find and extract the first (and shortest) substring in the given text that
    is preceded by the given prefix and is followed by the given suffix.
    Returns the first (and shortest) such substring.  

    Raises ValueError if no such substring is found.
    '''
    extract_start = text.index(prefix) + len(prefix)
    extract_end = text.index(suffix, extract_start)
    return text[extract_start:extract_end]

def file_extract(document, prefix, suffix):
    for line in document:
        try:
            return str_extract(line, prefix, suffix)
        except ValueError:
            pass

    raise ValueError(
        'no matching line found (prefix {0}, suffix {1})'
            .format(prefix, suffix))

def decrypt_vid_url(cipertext):
    '''
    Decrypt video URLs encrypted for af.tv's playernew.swf

    Returns the URL of the video that animefreak.tv's playernew.swf flash player
    would fetch if the given cipertext was passed to it's <file> parameter. 
    '''
    key = b'seningibicocukolmazolsunnepislikbisimissinsenaq654154'
    binary_ciphertext = b64decode(cipertext)
    plaintext_iter = map(xor, binary_ciphertext, cycle(key))
    return bytes(plaintext_iter).decode('ascii')

def extract_vid_url(page_url):
    with get_response_body(page_url) as main_document:
        iframe_code_quoted = file_extract(main_document,
            "var tempfile = '",
            "';")
    iframe_code = urllib.parse.unquote_plus(iframe_code_quoted)
    iframe_url = str_extract(iframe_code, ' src="', '">')

    with get_response_body(iframe_url, referer=page_url) as iframe_document:
      vid_url_encrypted = file_extract(iframe_document,
        'playernew.swf?file=',
        '&captions=')
    return decrypt_vid_url(vid_url_encrypted)

if __name__ == '__main__':
    import sys
    print(extract_vid_url(sys.argv[1]))
