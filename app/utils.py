
def download_minio_stream(stream, filename: str) -> None:
    with open(filename, 'wb') as file_data:
        for d in stream.stream(32*1024):
            file_data.write(d)
