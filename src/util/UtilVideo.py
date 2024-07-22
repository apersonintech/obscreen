import struct


def mp4_duration_with_ffprobe(filename):
    import subprocess, json

    result = subprocess.check_output(
            f'ffprobe -v quiet -show_streams -select_streams v:0 -of json "{filename}"',
            shell=True).decode()
    fields = json.loads(result)['streams'][0]

    if 'tags' in fields and 'DURATION' in fields['tags']:
        return int(float(fields['tags']['DURATION']))

    if 'duration' in fields:
        return int(float(fields['duration']))

    return 0
