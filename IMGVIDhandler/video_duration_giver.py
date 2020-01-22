import ffprobe3

videolink = r'C:\Users\CARBON\Desktop\30218427_2117692945128183_4838014671619358720_n.mp4'


def return_duration(vid):
    meta = ffprobe3.FFProbe(vid)
    duration = None
    for petitmeta in meta.streams:
        duration = int((float(petitmeta.duration))*1000)

    return duration

