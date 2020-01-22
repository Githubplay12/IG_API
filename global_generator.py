import string
import random
import time
import os
import uuid
import json
import hmac
import hashlib


# Function to generate the signed body :)
def generatesignedbody(data=None, profilpic=None):
    sigkey = '4a53a01ef7e3e10d17a13325af3fc193e95f669a319748a5cc3579adca529b3a'  # Needed sig key for the signature

    data = json.dumps(data)
    hash = hmac.new(sigkey.encode("utf-8"), data.encode("utf-8"), hashlib.sha256).hexdigest()
    if not profilpic:
        signature = 'signed_body=' + hash + '.' + data + '&' + 'ig_sig_key_version=4'
    else:
        signature = hash + '.' + data
    return signature  # 92634ad45e91caa9231c92040885f0312a7c9db8edc477c40ff5556b56fbe050.{"filter_type":"0","timezone_offset":"3600" ...)


# Generate URL ID for liking and commenting a post
def generate_like_com_id(codeuser, codepost):
    return codepost+'_'+codeuser  # https://i.instagram.com/api/v1/media/   1754421113095524315_7344575179  /like/


# Generate random UUID
def generate_uuid():
    return str(uuid.uuid4())  # e.g : de417046-2256-4c8b-a9e2-8a6ad3a59c9d


# Fonction pour generer un random android ID
def generate_androidid():
    chars = string.ascii_uppercase + string.digits
    randomid = ''.join((random.choice(chars) for s in range(16)))
    return 'android-' + randomid  # e.g : android-8YHP19BCZ719CE84


# Generate URL ID for pic and vids upload
def generate_upload_id(somefile):
    upload_id = str(int(time.time() * 1000))  # e.g : 1524115561404
    milieu = '_0_'
    hashcode = str(hash(os.path.basename(somefile))) # e.g : 363954952
    final = upload_id + milieu + str(hashcode)  # e.g : # 1524115561404_0_363954952
    return upload_id, hashcode, final  # https://i.instagram.com/rupload_igvideo/ 1524115561404_0_363954952


# Fonction pour generer un random password de 12 carac
def generate_pass():
    chars = string.digits + string.ascii_letters
    randompass = ''.join((random.choice(chars) for s in range(12)))
    return randompass  # e.g : mzuJHq9wGK9C





