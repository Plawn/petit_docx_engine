import os

def download_minio_stream(stream, filename: str) -> None:
    with open(filename, 'wb') as file_data:
        for d in stream.stream(32*1024):
            file_data.write(d)


def ensure_folder_exists(folder_name:str):
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
