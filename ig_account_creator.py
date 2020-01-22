import requests
from Utilitaires.requesthandler import RequestHandler
from Utilitaires.global_generator import generate_androidid, generate_pass
import json
from collections import OrderedDict

# Url used to create an account
createaccounturl = 'https://i.instagram.com/api/v1/accounts/create/'

def create_account(username, first_name, email, proxy=None):

    r = RequestHandler()

    #Setup proxy on the session
    if proxy:
        http_proxy = "http://"+proxy
        https_proxy = "https://"+proxy
        ftp_proxy = "ftp://"+proxy

        proxyDict = {
            "http": http_proxy,
            "https": https_proxy,
            "ftp": ftp_proxy
        }
        r.s.proxies.update(proxyDict)


    # Data pour créer un compte
    password = generate_pass()
    createaccountdata = json.dumps(OrderedDict([
        ('allow_contacts_sync', 'true'),
        ('device_id', generate_androidid()),
        ('username', username),
        ('first_name', first_name),
        ('email', email),
        ('password', password),
        # ('phone_id', "b85d076f-7d52-440c-89a4-bdcc8ebb5e7e"),
        # ('_csrftoken', 'RtakdsWi21SeclVEnAeh7Tu4WHr7Rrzt'),
        # ('adid', "33cf4211-9c4a-47f5-9bed-a8637637b71f"),
        # ('guid', '18cf5805-e663-4682-9189-0f7f8df9d595'),
        # ('force_sign_up_code', ""),
        # ('waterfall_id', "d7034d86-0e3b-4fc7-8617-2a20df4efffe"),
        # ('qs_stamp', ""),
    ]))

    #Basic headers
    headers = {
        'User-Agent': 'Instagram 35.0.0.20.96 Android (23/6.0.1; 480dpi; 1080x1920; samsung; SM-G935F; hero2lte; qcom; fr_FR; 95414346)',
        'Accept-Language': 'fr-FR, en-US',
        # 'Cookie': 'mid=WqJiWgABAAGXC7ZOSTYZgHntdBgc; mcd=1; csrftoken=RtakdsWi21SeclVEnAeh7Tu4WHr7Rrzt; rur=FRC',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept-Encoding': 'gzip, deflate',
        'Host': 'i.instagram.com',
        'X-FB-HTTP-Engine': 'Liger',
        'Connection': 'keep-alive',
    }

    r.s.headers.update(headers)

    # Create an account
    create = r.postrequest(createaccounturl, data=createaccountdata, jsonplease=False)
    if create.json()['account_created']:
        print('Username : {}\nPassword : {}'.format(username, password))



create_account('username', 'Complete name, 'email')



