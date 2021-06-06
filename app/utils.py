import io

import minio


def download_minio_stream(stream) -> io.BytesIO:
    _file = io.BytesIO()
    for d in stream.stream(32*1024):
        _file.write(d)
    return _file


def upload_file(minio_client: minio.Minio, name: str, bucket: str, _file: io.BytesIO) -> None:
    length = len(_file.getvalue())
    _file.seek(0)
    minio_client.put_object(
        bucket, name, _file, length=length
    )
