import ffprobe3

def return_duration(vid):
    meta = ffprobe3.FFProbe(vid)
    duration = None
    for petitmeta in meta.streams:
        duration = int((float(petitmeta.duration))*1000)

    return duration

