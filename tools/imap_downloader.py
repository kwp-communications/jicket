# Downloads entire IMAP folder and writes emails as binary into files

import imaplib
import ssl


imaphost = "imap.web.de"
imapport = 993
imapuser = "jicket-test@web.de"
imappass = "pVfYLdbCcVnKLF6HExGm"

folder = "jicket"


imap = imaplib.IMAP4_SSL(imaphost, imapport, ssl_context=ssl.create_default_context())
imap.login(imapuser, imappass)
response = imap.select(folder)
emailcount = int(response[1][0])
response = imap.uid("search", None, "(ALL)")
indices = response[1][0].split()
for uid in indices:
    print(f"Fetching {uid}")
    response = imap.uid("fetch", uid, "(RFC822)")
    if response[0] != "OK":
        print(f"UID {uid} failed: {response}")
        continue

    with open(f"{uid}.eml", "wb") as f:
        f.write(response[1][0][1])