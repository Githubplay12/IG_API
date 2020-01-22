from requests.exceptions import RequestException
from .sleeper import sleep_please
import sys
import requests

class RequestHandler():
    def __init__(self, proxies=None):
        self.s = requests.session()
        self.s.proxies = proxies

    # Function that displays exceptions
    def exception_displayer(self, e):
        print(f' {e} : {e.__class__} (Line : {sys.exc_info()[-1].tb_lineno})')

    # Function that handles exceptions
    def exception_handler(self, request):
        while True:
            try:
                request
            except RequestException as e:
                self.exception_displayer(e)
                sleep_please(minutes=10)
            except OSError as e:
                self.exception_displayer(e)
                sleep_please(minutes=10)
            except Exception as e:
                self.exception_displayer(e)
                break
            else:
                return request

    # Function that gives and can display the json
    def jsontest(self, request, jsonplease):
        try:
            jsonaccepted = request.json()
        except ValueError:
            print('No json for this request')
        else:
            if jsonplease == 'show':
                for key, value in jsonaccepted.items():
                    if isinstance(value, dict):
                        for key2, value2 in value.items():
                            print('{} : {} : {}'.format(key, key2, value2))
                    else:
                        print('{} : {}'.format(key, value))
                print('\n')
            return jsonaccepted

    # Basic get function
    def getrequest(self, url, jsonplease=None):
        request = self.exception_handler(self.s.get(url))
        return self.analyzerequest(request, jsonplease)


    # Basic post function
    def postrequest(self, url, jsonplease=None, *args, **kwargs):
        request = self.exception_handler(self.s.post(url, args, kwargs))
        return self.analyzerequest(request, jsonplease)


    # Analyzing the request sent, if not 200 say something
    def analyzerequest(self, request, jsonplease):
        if request.status_code != 200 or jsonplease:
            print(f'Status code : {request.status_code}')
            return self.jsontest(request, jsonplease)

        elif request.status_code == 200:
            return request











