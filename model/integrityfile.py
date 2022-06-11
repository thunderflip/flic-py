import csv
import os
import shutil
import tempfile

from model.integrityentry import IntegrityEntry


class IntegrityFile:

    FIELD_NAMES = [
        IntegrityEntry.FILE_PATH,
        IntegrityEntry.FILE_SIZE,
        IntegrityEntry.FILE_MODTIME,
        IntegrityEntry.DATE_CHECKED
    ]

    def __init__(self, file_path=None):
        if file_path is not None:
            self.entries = IntegrityFile.read_integrity_entries(file_path)

    @staticmethod
    def read_integrity_entries(file_path):
        integrity_entry_list = None
        rows = IntegrityFile.read_rows(file_path)
        if rows is not None:
            integrity_entry_list = list()
            for row in rows:
                integrity = IntegrityEntry(row)
                integrity_entry_list.append(integrity)

        return integrity_entry_list

    @staticmethod
    def write_integrity_entries(integrity_entry_list, file_path):
        if integrity_entry_list is not None:
            rows = list()
            for integrity_entry in integrity_entry_list:
                data = integrity_entry.get_data()
                row = dict()
                for key in IntegrityFile.FIELD_NAMES:
                    if key in data:
                        row[key] = data[key]
                    else:
                        row[key] = None
                rows.append(row)

            IntegrityFile.write_rows(rows, file_path)

    @staticmethod
    def read_rows(file_path):
        rows = None
        if os.path.exists(file_path):
            i = 0
            with open(file_path, 'r', encoding='utf-8') as csv_file:
                reader = IntegrityFile.get_reader(csv_file)
                for row in reader:
                    if i == 0:
                        i = i + 1
                        continue
                    else:
                        if rows is None:
                            rows = list()
                        rows.append(row)

        return rows

    @staticmethod
    def write_rows(rows, file_path):
        temp_file_name = IntegrityFile.get_temp_filename()
        with open(temp_file_name, 'a', encoding='utf-8') as csv_file:
            writer = IntegrityFile.get_writer(csv_file)
            writer.writeheader()

            for row in rows:
                writer.writerow(row)

        if os.path.exists(file_path):
            os.remove(file_path)

        shutil.move(temp_file_name, file_path)

    @staticmethod
    def get_writer(csv_file):
        return csv.DictWriter(csv_file, delimiter=';', lineterminator='\n', fieldnames=IntegrityFile.FIELD_NAMES)

    @staticmethod
    def get_reader(csv_file):
        return csv.DictReader(csv_file, delimiter=';', lineterminator='\n', fieldnames=IntegrityFile.FIELD_NAMES)

    @staticmethod
    def get_temp_filename():
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        temp_file.close()

        return temp_file.name