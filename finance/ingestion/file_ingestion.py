import os
import shutil
from datetime import datetime


class FileIngestion:
    def __init__(self, db, upload_dir="uploads"):
        self.db = db
        self.upload_dir = upload_dir

    def upload(self, filepath):
        os.makedirs(self.upload_dir, exist_ok=True)
        filename = os.path.basename(filepath)
        dest = os.path.join(self.upload_dir, filename)
        shutil.copy2(filepath, dest)
        upload_date = datetime.now().strftime("%Y-%m-%d")
        ext = os.path.splitext(filename)[1].lower()
        ftype = "pdf" if ext == ".pdf" else ext.lstrip(".")
        file_id = self.db.insert_raw_file(
            filename=filename,
            ftype=ftype,
            upload_date=upload_date,
            statement_period="",
            statement_type="UNKNOWN",
        )
        return file_id

    def list_files(self):
        return self.db.get_all_raw_files()
