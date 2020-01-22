from moviepy.editor import VideoFileClip
import os
import time

def return_thumbnail(video):
    thumbnaildirectory = os.path.join(os.getcwd(), 'tpthumb.jpg')
    myclip = VideoFileClip(video)
    myclip.save_frame(thumbnaildirectory)
    while not os.path.exists(thumbnaildirectory):
        time.sleep(2)
    else:
        return thumbnaildirectory, str(os.path.getsize(thumbnaildirectory))

