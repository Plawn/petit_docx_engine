import minio

class Context:
    def __init__(self):
        self.minio_client: minio.Minio = None