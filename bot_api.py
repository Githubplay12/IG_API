#key = 4a53a01ef7e3e10d17a13325af3fc193e95f669a319748a5cc3579adca529b3a for #36

from collections import OrderedDict

import requests
from requests_toolbelt import MultipartEncoder

from Utilitaires.IMGVIDhandler.change_img import compress_img
from Utilitaires.IMGVIDhandler.video_duration_giver import return_duration
from Utilitaires.IMGVIDhandler.thumbnail_generator import return_thumbnail
from Utilitaires.global_generator import *
from Utilitaires.requesthandler import postrequest, getrequest

pingouintest = r'C:\Users\CARBON\Desktop\ping.jpg'


class BotApi:
    # Basic user agent (a modifier ?)
    useragent = 'Instagram {} Android ({}/{}; 480dpi; 1080x1920; {}; {}; hero2lte; qcom; fr_FR; 95414346)'  # .format(self.ig_version, str(self.android_version),self.android_release, self.manufacturer, self.model)

    # Start of API URL
    api_url = 'https://i.instagram.com/api/v1'

    igweb_url = 'https://www.instagram.com/{}/?__a=1'

    # Basic headers
    headers = {
        'User-Agent': '',
        'Accept-Language': 'fr-FR, en-US',
        'Accept-Encoding': 'gzip, deflate',
        'Host': 'i.instagram.com',
        'X-FB-HTTP-Engine': 'Liger',
        'Connection': 'keep-alive',
    }


    def __init__(self, username, password):

        # Username and password of the account
        self.username = username
        self.password = password

        # Creating a session object to maintain headers and proxies.
        self.s = requests.session()

        # For user agent / device etc
        self.ig_version = '35.0.0.20.96'
        self.android_version = 23
        self.android_release = '6.0.1'
        self.manufacturer = 'samsung'
        self.model = 'SM-G935F'

        # Include the above into the headers :
        self.headers['User-Agent'] = self.useragent.format(self.ig_version, str(self.android_version), self.android_release, self.manufacturer, self.model)

        #Session token, mid et ds_user_id juste au cas ou
        self.token = None
        self.mid = None
        self.user_id = None

        self.uuid = generate_uuid()
        self.adid = generate_uuid()
        self.phone_id = generate_uuid()

        self.cookie = []

        self.retrycontext = "{\"num_step_auto_retry\":0,\"num_reupload\":0,\"num_step_manual_retry\":0}"
        self.imagecompression = "{\"lib_name\":\"moz\",\"lib_version\":\"3.1.m\",\"quality\":\"84\"}"
        self.device = { "manufacturer": self.manufacturer,
                        "model":self.model,
                        "android_version":self.android_version,
                        "android_release":self.android_release
                      }

    # Login method
    def login(self):

        # URL to login via API
        loginurl = self.api_url + '/accounts/login/'

        # Headers to login
        self.s.headers.update(self.headers)
        self.s.headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'

        #Data to login
        loginsigdata = {
                        'phone_id': self.phone_id,
                        # '_csrftoken' : self.token,
                        'username': self.username,
                        'adid': self.adid,
                        'guid': self.uuid,
                        'device_id': "android-C1ACF6A20CE58585",
                        'password' : self.password,
                        'login_attempt_count' : "0",
                       }

        login = postrequest(self.s, loginurl, data=generatesignedbody(loginsigdata), jsonplease=True)
        rlogin = login[0]
        jsonlogin = login[1]

        if rlogin.status_code == 200 and jsonlogin['status'] == 'ok':
            print('{} Connected'.format(self.username))
            print('\n')

            # Get token / user_id / mid from response in case we need them
            for cookie in rlogin.cookies:
                if cookie.name == 'csrftoken':
                    self.token = cookie.value
                elif cookie.name == 'ds_user_id':
                    self.user_id = cookie.value
                elif cookie.name == 'mid':
                    self.mid = cookie.value

        # Handling login problems here
        elif rlogin.status_code == 400:

            #If there's a challenge (captcha / phone / email)
            urlchallenge = self.api_url + login.json()['challenge']['url'].split('instagram.com')[1]
            #urlchallengereset = self.apiurl
            challenge = getrequest(self.s, urlchallenge, jsonplease=True)

            # If there's a phone problem :
            if challenge.json()['step_name'] == 'submit_phone':
                print('{} Got a phone challenge'.format(self.username))

                # In case the phone isn't assigned yet
                if challenge.json()['step_data']['phone_number'] == 'None':
                    nophone = input('Which phone number to assign to the user {} ? : \n'.format(self.username))
                    addphone = postrequest(self.s, urlchallenge, data=generatesignedbody({'phone_number' : nophone}))

                # If the phone number is already assigned
                else:
                    sendauth = input('Click Y to send sms now : \n')
                    if sendauth == 'y':
                        sendsms = postrequest(self.s, urlchallenge)

                # Confirmation of code reception
                coderecept = input('If you did receive the sms, type it, else click N : \n')
                while True:
                    if coderecept != 'n':
                        confirmcode = postrequest(self.s, urlchallenge, data=generatesignedbody({'security_code' : coderecept}))
                        break
                    else:
                        time.sleep(60)
                        sendsms = postrequest(self.s, urlchallenge)
                print('{} Connected'.format(self.username))









    # Get info from current user profil (we need email to change bio ;))
    def get_currentuser_info(self):

        getinfourl = self.api_url + '/accounts/current_user/?edit=true'

        getinforequest = getrequest(self.s, getinfourl, jsonplease=True)
        user = getinforequest[1]['user']

        userinfodata = {
                    'external_url': user['external_url'],
                    'gender': str(user['gender']),
                    'phone_number': user['phone_number'],
                   '_csrftoken': self.token,
                    'username': user['username'],
                    'first_name': user['full_name'],
                    '_uid': self.user_id,
                    'biography': user['biography'],
                    '_uuid': self.uuid,
                    'email': user['email'],
                    }

        return userinfodata


    # Change something in the profil (everything but the profil picture)
    def change_profil(self, linkurl=None, gender=None, phonenumber=None, username=None, first_name=None, bio=None, email=None):

        profilchangeurl = self.api_url + '/accounts/edit_profile/'

        profilpicdata = self.get_currentuser_info()


        # Change / add link
        if linkurl:
            profilpicdata.update({'external_url' : linkurl})
        # Change / add gender
        if gender:
            profilpicdata.update({'gender': gender})
        # Change / add phone number
        if phonenumber:
            profilpicdata.update({'phone_number': phonenumber})
        # Change / add username
        if username:
            profilpicdata.update({'username': username})

        # Change / add first_name
        if first_name:
            profilpicdata.update({'first_name': first_name})
        # Change / add bio
        if bio:
            profilpicdata.update({'biography': bio})
        # Change / add email
        if email:
            profilpicdata.update({'email': email})

        # Same url to change entire profil
        changeprofil = postrequest(self.s, profilchangeurl, data=generatesignedbody(profilpicdata))


    # Change profil picture
    def change_profilpic(self, profilpic):

        urlchangeprofilpic = self.api_url + '/accounts/change_profile_picture/'

        headersprofilpic = {'Content-type': 'multipart/form-data; boundary=' + self.uuid}

        tokendata = {'_csrftoken': self.token,
                            '_uid': self.user_id,
                            '_uuid': self.uuid}

        m = MultipartEncoder(fields={
                                'signed_body' : generatesignedbody(tokendata, profilpic=True),
                                'ig_sig_key_version' : '4',
                                'profile_pic' : ('profile_pic', open(profilpic, 'rb'), 'application/octet-stream',
                                                 {'Content-Transfer-Encoding' : 'binary'})
                                    },
                             boundary=self.uuid)


        rchangeprofilpic = postrequest(self.s, urlchangeprofilpic, data=m, headers=headersprofilpic)


    # DM function using the code10 OR username from a user
    def dm_1user(self, text, codeuser):

        dmurl = self.api_url + '/direct_v2/threads/broadcast/text/'
        # girlswimsuit code10 = 5835839886

        dmdata = {  'recipient_users' : '[['+codeuser+']]',
                    'action': 'send_item',
                    'client_context' : self.uuid,
                    '_csrftoken' : self.token,
                    'text' : text,
                    '_uuid' : self.uuid,}



        rdm = postrequest(self.s, dmurl, data=dmdata)


    # Get code10 from only ONE username if not private(from the web)
    def general_oneinfo(self, username):

        weburl = self.igweb_url.format(username)

        generalinfoheaders = {
            'Accept-Encoding': 'gzip, deflate',
            #'Accept-Language': self.accept_language,
            'Connection': 'keep-alive',
            'Content-Length': '0',
            'Host': 'www.instagram.com',
            'Origin': 'https://www.instagram.com',
            'Referer': 'https://www.instagram.com/',
            #'User-Agent': self.useragent,
            'X-Instagram-AJAX': '1',
            'X-Requested-With': 'XMLHttpRequest'
        }
        getinfo = getrequest(self.s, weburl, headers=generalinfoheaders, jsonplease=True)
        try:
            jsonrgetinfo = getinfo[1]['graphql']['user']
        except ValueError:
            print('{} inexistant'.format(username))
        else:
            return jsonrgetinfo['id']


    # Follow a user
    def follow_user(self, codeuser):

        urlfollow = self.api_url + '/friendships/create/{}/'.format(codeuser)

        datafollow = {'_csrftoken' : self.token,
                      'user_id' : codeuser,
                      'radio_type' : 'wifi-none',
                      '_uid' : self.user_id,
                      '_uuid' : self.uuid,
                      }

        rfollow = postrequest(self.s, urlfollow, data=generatesignedbody(datafollow))

    # Unfollow user
    def unfollow_user(self, codeuser):

        urlunfollow = self.api_url + '/friendships/destroy/{}/'.format(codeuser)

        dataunfollow = {'_csrftoken' : self.token,
                      'user_id' : codeuser,
                      'radio_type' : 'wifi-none',
                      '_uid' : self.user_id,
                      '_uuid' : self.uuid,
                      }

        runfollow = postrequest(self.s, urlunfollow, data=generatesignedbody(dataunfollow), jsonplease=True)

    # Like a user's post
    def like_post(self, codeuser, codepost):
        code = generate_like_com_id(codeuser, codepost)

        urllike = self.api_url+'/media/{}/like/'.format(code)

        datalike = {#'module_name' : '',
                    'media_id': code,
                    '_csrftoken': self.token,
                    #'username': self.username,
                    #'user_id': self.user_id,
                    'radio_type': 'wifi_none',
                    '_uid': self.user_id,
                    '_uuid': self.uuid,
                    }

        rlike = postrequest(self.s, urllike, data=generatesignedbody(datalike))


    # Comment something on a post
    def comment(self, codeuser, codepost, comment):
        code = generate_like_com_id(codeuser, codepost)

        urlcomment = self.api_url + '/media/{}/comment/'.format(code)

        datacomment = {'_csrftoken' : self.token,
                       'radio_type': 'wifi_none',
                       '_uuid': self.uuid,
                       'comment_text': comment,
                       }

        rcomment = postrequest(self.s, urlcomment, data=generatesignedbody(datacomment))

    # Post picture
    def postpic(self, img):

        link, size, width, height = compress_img(img)
        upload_idonly, hashcode, upload_idforurl = generate_upload_id(link)

        urlpic = 'https://i.instagram.com/rupload_igphoto/{}'.format(upload_idforurl)

        Ruploadparams = json.dumps({"upload_id": str(upload_idonly),
                          "image_compression":self.imagecompression,
                          "retry_context":self.retrycontext,
                          "media_type":"1"})

        headersgetphoto = self.headers

        headersgetphoto.update({'X-Instagram-Rupload-Params' : Ruploadparams,
                                'X_FB_PHOTO_WATERFALL_ID' : self.uuid,
                                'X-Entity-Type': 'image/jpeg',
                                 'X-Entity-Length': str(int(size)),
                                 'Offset': '0',
                                 'X-Entity-Name': str(upload_idforurl),
                                 'Content-Type': 'application/octet-stream',
                                 'Content-Length': str(int(size)),
                                })

        m = open(link, 'rb').read()

        rpostpic = postrequest(self.s, urlpic, data=m, headers=headersgetphoto)

        urlconfig = self.api_url + '/media/configure/'

        edits = {"crop_original_size" : [float(width),float(height)],
                 "crop_center" : [0.0,-0.0],
                 "crop_zoom" : 1.0
                 }

        extra = {"source_width":width,
                 "source_height":height}

        datapostpic = {"timezone_offset":"3600",
                       "_csrftoken":self.token,
                       "media_folder":"Instagram",
                       "source_type":"1",
                       "_uid":self.user_id,
                       "_uuid":self.uuid,
                       "caption":"lol",
                       "upload_id":upload_idonly,#str(upload_idonly),
                       "device": self.device,
                       "edits": edits,
                       "extra": extra,
                       }

        rconfigurepic = postrequest(self.s, urlconfig, data=generatesignedbody(datapostpic))


    def post_vid2(self, file, thumbnail=None):

        thumbnailsize = None

        videoduration = return_duration(file)
        upload_idonly, hashcode, upload_idforurl = generate_upload_id(file)
        filesize = str(os.path.getsize(file))
        if not thumbnail:
            thumbnailpic, thumbnailsize = return_thumbnail(file)
        else:
            thumbnailpic = thumbnail

        urlpostvid2 = 'https://i.instagram.com/rupload_igvideo/{}'.format(upload_idforurl)
        urlpostthumbail = 'https://i.instagram.com/rupload_igphoto/{}'.format(upload_idforurl)
        urlconfigure = self.api_url + '/media/configure/?video=1'

        XInstagramRuploadParams = json.dumps({"upload_media_height": "0",
                                   "upload_media_width": "0",
                                   "upload_media_duration_ms": filesize,
                                   "upload_id": upload_idonly,
                                   "retry_context": self.retrycontext,
                                   "media_type": "2"
                                   })
        headerspostvid2 = self.headers
        headerspostvid2.update({'X-Entity-Type': 'video/mp4',
                                   'Offset': '0',
                                   'X-Instagram-Rupload-Params': XInstagramRuploadParams,
                                   'X-Entity-Name': upload_idforurl,
                                   'X-Entity-Length': filesize,
                                   'X_FB_VIDEO_WATERFALL_ID': self.uuid,
                                   'Content-Length': filesize
                                })

        fileb = open(file, 'rb').read()

        rpostvid2 = postrequest(self.s, urlpostvid2, data=fileb, headers=headerspostvid2)

        # If the video was posted
        if rpostvid2[1]['status'] == 'ok':

            # Configure the thumbnail part
            Ruploadparams2 = json.dumps({"retry_context": self.retrycontext,
                                         "image_compression": "{\"lib_name\":\"moz\",\"lib_version\":\"3.1.m\",\"quality\":\"84\"}",
                                         "media_type": "2",
                                         "upload_id": upload_idonly,
                                         })

            headerspostthumnail = headerspostvid2
            headerspostthumnail['X-Instagram-Rupload-Params'] = Ruploadparams2
            headerspostthumnail['X-Entity-Type'] = 'image/jpeg'
            headerspostthumnail['X-Entity-Length'] = thumbnailsize
            headerspostthumnail['Content-Length'] = thumbnailsize

            thumb = open(thumbnailpic, 'rb').read()

            rpostthumbnail = postrequest(self.s, urlpostthumbail, data=thumb, headers=headerspostthumnail)
            # Sleeping to avoid transcode problem
            time.sleep(10)
            


            # Finally confirm the upload
            headersconfigure = self.headers
            headersconfigure.update({'retry_context' : self.retrycontext})

            clips = [{'length' : videoduration,
                      'source_type' : '3',
                      'camera_position' : 'back'
                      }]

            extra = {"source_width":720,"source_height":1280}

            datapostvid = {'filter_type' : '0',
                           "timezone_offset" : "3600",
                           "_csrftoken" : self.token,
                           "source_type" : "3",
                            'video_result' : '',
                            "_uid" : self.user_id,
                           "_uuid" : self.uuid,
                           "caption" : "lol",
                           "upload_id" : upload_idonly,#str(upload_idonly),
                           "device": self.device,
                           "length" : videoduration,
                           'clips' : clips,
                           'extra' : extra,
                           'audio_muted' : False,
                           "poster_frame_index" : 0,
                        }

            rconfigurevid = postrequest(self.s, urlconfigure, data=generatesignedbody(datapostvid), headers=headersconfigure, jsonplease=True)
            if rconfigurevid[1]['status'] == 'ok':
                os.remove(thumbnailpic)

    # Upload to story (video ou photo)
    def upload_story(self, filelink):

        width, height, size, is_vid, is_pic, upload_thumbnail, url_upload_thumbnail_story, thumbnail, headers_upload_story_thumbnail = [None]*9
        upload_id, hashcode, upload_id_url = generate_upload_id(filelink)

        # General data for the file configure
        data_config_story = {'timezone_offset': '3600',
                             '_csrftoken': self.token,
                             'configure_mode': '1',
                             'source_type': '4',
                             '_uid': self.user_id,
                             '_uuid': self.uuid,
                             'caption': '',
                             'capture_type': 'normal',
                             'mas_opt_in': 'NOT_PROMPTED',
                             'upload_id': upload_id,
                             'device': self.device,
                             }

        if os.path.splitext(filelink)[1] not in ['.jpg', '.png']:
            is_vid = True
            # Configuring the video details (headers / data to send in sig)
            duration, size = return_duration(filelink), str(os.path.getsize(filelink))

            # URLS for upload video + config
            url_upload_story = 'https://i.instagram.com/rupload_igvideo/{}'.format(upload_id_url)
            url_config_tostory = self.api_url + '/media/configure_to_story/?video=1'

            # Headers for video upload
            XEntityType = 'video/mp4'
            Xwaterfall = {'X_FB_VIDEO_WATERFALL_ID' : self.uuid}
            XInstagramRuploadParams = json.dumps({'upload_media_height': "0",
                                                  'upload_media_width': "0",
                                                  'upload_media_duration_ms': duration,
                                                  'upload_id': upload_id,
                                                  'for_album': '1',
                                                  'retry_context': self.retrycontext,
                                                  'media_type': '2',})

            # Data for video upload
            extra = {'source_width': 720,
                     'source_height': 1280, }
            data_story_video_upload = {'video_result': '',
                                       'clips': [{"length": 0.336, "source_type": "3", "camera_position": "front"}],
                                       'audio_muted': False,
                                       'poster_frame_index': 0,
                                       'extra': extra
                                       }
            data_config_story.update(data_story_video_upload)

            # Thumbnail for the video

            # Thumbnail details
            thumbnail, thumbnailsize,  = return_thumbnail(filelink)
            thumbhashcode = generate_upload_id(thumbnail)[1]

            # Thumbnail URL
            url_upload_thumbnail_story = 'https://i.instagram.com/rupload_igphoto/{}'.format(upload_id+'_0_'+hashcode)

            # Thumbnail headers
            XInstagramRuploadParamsthumbnail = json.dumps({'upload_id': upload_id,
                                                           'image_compression': self.imagecompression,
                                                           'retry_context': self.retrycontext,
                                                           'media_type': '1'})
            XEntityThumbnailType = 'image/jpeg'
            Xwaterfallthumbnail = {'X_FB_PHOTO_WATERFALL_ID': self.uuid}
            headers_upload_story_thumbnail = {**self.headers,
                                    **Xwaterfallthumbnail,
                                    'X-Entity-Name': upload_id+'_0_'+hashcode,
                                    'X-Entity-Length': thumbnailsize,
                                    'X-Entity-Type': XEntityThumbnailType,
                                    'X-Instagram-Rupload-Params': XInstagramRuploadParamsthumbnail,
                                    'Offset': '0',
                                    'Content-Type': 'application/octet-stream',
                                    'Content-Length': thumbnailsize, }

        else:
            is_pic = True
            # Image details
            filelink, size, width, height = compress_img(filelink, story=True)
            upload_id, hashcode, upload_id_url = generate_upload_id(filelink)

            # URL to upload and configure photo
            url_upload_story = 'https://i.instagram.com/rupload_igphoto/{}'.format(upload_id_url)
            url_config_tostory = self.api_url + '/media/configure_to_story/'

            # Headers for the photo upload
            XEntityType = 'image/jpeg'
            Xwaterfall = {'X_FB_PHOTO_WATERFALL_ID': self.uuid}
            XInstagramRuploadParams = json.dumps({'upload_id': upload_id,
                                                  'image_compression': self.imagecompression,
                                                  'retry_context': self.retrycontext,
                                                  'media_type': '1'})

            # Data for the photo upload
            extra = {'source_width': width,
                     'source_height': height,
                     }
            edits = {'crop_original_size' : [float(width),float(height)],
                     'crop_center' : [0.0,0.0],
                     'crop_zoom' : 1.0,}
            data_config_story.update({'edits' : edits,
                                      'extra' : extra,})

        # General upload headers (specific are above)
        headers_upload_story = {**self.headers,
                                **Xwaterfall,
                                'X-Entity-Name' : upload_id_url,
                                'X-Entity-Length' : size,
                                'X-Entity-Type' : XEntityType,
                                'X-Instagram-Rupload-Params' : XInstagramRuploadParams,
                                'Offset' : '0',
                                'Content-Type': 'application/octet-stream',
                                'Content-Length' : size,}

        # Converting the file to binary
        fileupload = open(filelink, 'rb').read()

        # Upload the video or photo
        upload_file_tostory = postrequest(self.s, url_upload_story, data=fileupload, headers=headers_upload_story, line=give_line_exception())
        # If video then upload the thumbnail too
        if is_vid:
            upload_thumbnail = postrequest(self.s, url_upload_thumbnail_story, data=open(thumbnail, 'rb').read(), headers=headers_upload_story_thumbnail,
                                           jsonplease=True)

        # If the file was uploaded then it's time to configure
        if upload_file_tostory[1]['status'] == 'ok':

            if is_pic:
                # Getting the upload id from the response of upload pic
                upload_id = {'upload_id' : str(upload_file_tostory[1]['upload_id'])}
                data_config_story.update(upload_id)

            elif is_vid:
                # Getting the upload id from the response of upload thumbnail of video
                upload_id = {'upload_id': str(upload_thumbnail[1]['upload_id'])}
                data_config_story.update(upload_id)

            # Finally configuring the file
            post_configure_story = postrequest(self.s, url_config_tostory, data=generatesignedbody(data_config_story))


bot = BotApi('aberr5410', 'Test@1test@1')
bot.login()




























