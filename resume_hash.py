import json

class JsonDbConn:

    DEFAULT_JSON_FILENAME = "resume_hash_labels.json"

    def initialize_datafile_if_not_exists(self):
        try:
            open(self._datafile, 'r').close()
        except FileNotFoundError:
            with open(self._datafile, 'w') as fobj:
                json.dump({}, fobj)

    def read_decorator(method):
        def _read_json(self, *args, **kwargs):
            json_data = {}
            self.initialize_datafile_if_not_exists()
            with open(self._datafile, 'r') as fobj:
                json_data = json.load(fobj)
                fobj.seek(0)
            for key in json_data:
                self._data[key] = json_data[key]
            return method(self, *args, **kwargs)
        return _read_json

    def write_decorator(method):
        """Overwrites json file with current data immediately following execution
        of the decorated method."""
        def _write_json(self, *args, **kwargs):
            method_return = method(self, *args, **kwargs)
            with open(self._datafile, 'w') as fobj:
                json.dump(self._data, fobj)
            return method_return
        return _write_json

    def __init__(self, json_filename: str=DEFAULT_JSON_FILENAME):
        self._datafile = json_filename
        self._data = {}

    @read_decorator
    @write_decorator
    def create_hash(self, hash: str, date: str, genre: str, notes: str):
        if not hash in self._data:
            self._data[hash] = {
                "date": date,
                "genre": genre,
                "notes": notes
            }
        else:
            raise ValueError("Hash collision")

    @read_decorator
    def lookup(self, hash: str) -> dict:
        """Returns the data associated with the key hash."""
        return self._data[hash]



def main():
    pass

if __name__ == "__main__":
    main()