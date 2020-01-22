import subprocess
import math
import ffprobe3
import os




def split_by_seconds(filename, split_length=None, vcodec="h264", acodec="copy",
                     extra="", **kwargs):

    if not split_length:
        split_length = 15

    #if split_length and split_length <= 0:
        #print("Split length can't be 0")
        #raise SystemExit
    meta = ffprobe3.FFProbe(filename)

    video_length = None
    for something in meta.streams:
        video_length = float(something.duration)
    #split_length = int(video_length/4)


        # print('{} min et {} sec'.format(int(math.modf(float(something.duration)/60)[1]), (math.modf(float(something.duration)/60)[0])))
    '''
    output = subprocess.Popen("ffmpeg -i \""+filename+"\" 2>&1 | findstr 'Duration'",
                            shell = True,
                            stdout = subprocess.PIPE
                            ).stdout.read()
    print(output)


    matches = re_length.search(meta)
    if matches:
        video_length = int(matches.group(1)) * 3600 + \
                        int(matches.group(2)) * 60 + \
                        int(matches.group(3))
    else:
        print("Can't determine video length.")
        raise SystemExit
    '''
    print("Video length in seconds: " + str(video_length))

    split_count = int(math.ceil(video_length / float(split_length)))
    if (split_count == 1):
        print("Video length is less then the target split length.")
        raise SystemExit






    filepath = os.path.join(r'C:\\Users\CARBON\Desktop\internet work\PY project work\Instagram API\Test files', 'test.mp4')

    split_cmd = "ffmpeg -i \"%s\" -vcodec %s -acodec %s %s" % (filepath, vcodec,
                                                               acodec, extra)
    resize_cmd = 'ffmpeg -i \"{}\" -vf scale=1080:1920 \"{}\"'

    list_splitted_filenames = []

    print('about to run {}'.format(resize_cmd.format(filename, filepath)))
    resize = subprocess.Popen(resize_cmd.format(filename, filepath), shell=True, stdout=subprocess.PIPE).stdout.read()

    justname = os.path.splitext(filepath)[0]
    justextension = os.path.splitext(filepath)[1]


    for n in range(0, split_count):
        split_str = ""
        if n == 0:
            split_start = 0
        else:
            split_start = split_length * n

        split_str += " -ss " + str(split_start) + " -t " + str(split_length) + \
                     " \"" + justname + "-" + str(n) + justextension

        # Splitting files here
        print("About to run: " + split_cmd + split_str)
        output = subprocess.Popen(split_cmd + split_str, shell=True, stdout=subprocess.PIPE).stdout.read()
        # Resizing files to 1080, 1920 for stories:
        splitted_filename = justname+'-'+str(n)+justextension

        list_splitted_filenames.append(splitted_filename)




    return list_splitted_filenames


split_by_seconds(r'C:\Users\CARBON\Desktop\internet work\PY project work\Instagram API\Test files\30218427_2117692945128183_4838014671619358720_n.mp4', split_length=15)