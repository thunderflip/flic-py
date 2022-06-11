
class IntegrityEntry:

    FILE_PATH = "File"
    FILE_SIZE = "Size"
    FILE_MODTIME = "Mod-Time"
    DATE_CHECKED = "Last-Check"

    def __init__(self, data=None):
        self.data: dict = None
        self.set_data(data)

    def get_data(self):
        return self.data

    def set_data(self, data):
        if data is not None:
            self.data = data
        else:
            d = dict()
            d[IntegrityEntry.FILE_PATH] = None
            d[IntegrityEntry.FILE_SIZE] = None
            d[IntegrityEntry.FILE_MODTIME] = None
            d[IntegrityEntry.DATE_CHECKED] = None
            self.data = d

    def get_file_path(self):
        return self.data[self.FILE_PATH]

    def set_file_path(self, value):
        self.data[self.FILE_PATH] = value

    def get_file_size(self):
        return self.data[self.FILE_SIZE]

    def set_file_size(self, value):
        self.data[self.FILE_SIZE] = value

    def get_file_modtime(self):
        return self.data[self.FILE_MODTIME]

    def set_file_modtime(self, value):
        self.data[self.FILE_MODTIME] = value

    def get_date_checked(self):
        return self.data[self.DATE_CHECKED]

    def set_date_checked(self, value):
        self.data[self.DATE_CHECKED] = value
