class Document:
    def __init__(self, document_id: str, document_info: dict, file_info: dict, uploader: str):
        self.document_id = document_id
        self.document_info = document_info
        self.file_info = file_info
        self.uploader = uploader

    def to_dict(self):
        return {
            'document_id': self.document_id,
            'document_info': self.document_info,
            'file_info': self.file_info,
            'uploader': self.uploader,
        }