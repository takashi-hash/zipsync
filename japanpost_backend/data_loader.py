import zipfile
import csv
import io
from .models import create_address_entry


def load_csv_from_zip(zip_path: str) -> list:
    with zipfile.ZipFile(zip_path, 'r') as z:
        csv_file = z.namelist()[0]
        with z.open(csv_file) as f:
            content = f.read().decode('utf-8')
            rows = list(csv.reader(io.StringIO(content)))
            return [create_address_entry(row) for row in rows]
