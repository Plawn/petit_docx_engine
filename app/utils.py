import os
import io

def download_minio_stream(stream, _file: io.BytesIO) -> None:
    for d in stream.stream(32*1024):
        _file.write(d)


def ensure_folder_exists(folder_name:str):
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
