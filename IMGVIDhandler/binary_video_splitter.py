import random
import hashlib





def generate_viddetails(vid):
    hash_md5 = hashlib.md5()

    urlvidbase = 'https://i.instagram.com/rupload_igvideo/{}-0-{}?segmented=true&phase=transfer'

    videolinkbinary = open(vid, 'rb')
    totalbuffersize = 0

    buffer = videolinkbinary.read(random.randint(150000, 350000))


    listbuffers = []
    listsizebuffers = []
    listtotalsizebuffers = ['0']
    listmd5 = []
    listlinkurls = []

    while len(buffer):
        # Create md5 lists
        hash_md5.update(buffer)
        listmd5.append(hash_md5.hexdigest())

        # Size buffer list
        listsizebuffers.append(len(buffer))

        # Total size buffer list
        totalbuffersize += len(buffer)
        listtotalsizebuffers.append(str(totalbuffersize))


        # Binary data to send (buffer)
        listbuffers.append(buffer)

        # Build a list of urls
        listlinkurls.append(urlvidbase.format(hash_md5.hexdigest(), len(buffer)))


        # Go to the next buffer
        buffer = videolinkbinary.read(random.randint(150000, 350000))
    else:
        return listlinkurls, listbuffers, listmd5, listsizebuffers, listtotalsizebuffers





