import os
import io


def download_minio_stream(stream) -> io.BytesIO:
    _file = io.BytesIO()
    for d in stream.stream(32*1024):
        _file.write(d)
    return _file
