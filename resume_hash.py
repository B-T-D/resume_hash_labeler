import json
from datetime import datetime
import time
import argparse
import sys

CONFIG_FILENAME = "config.json"

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
                try:
                    json_data = json.load(fobj)
                except json.decoder.JSONDecodeError: # If it was a new file, initialize to blank dict
                    json_data = {}
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
    def create(self, id: str, date: str, genre: str, notes: str):
        print(f"in db create():\n{id=} {date=} {genre=} {notes=}")
        if not id in self._data:
            self._data[id] = {
                "date": date,
                "genre": genre,
                "notes": notes
            }
        else:
            raise ValueError("Hash collision")

    @read_decorator
    def lookup(self, hash: str) -> dict:
        """Returns the data associated with the key hash."""
        if hash in self._data:
            return self._data[hash]
        return {}

    @read_decorator
    def all_objects(self) -> dict:
        """Returns a dict of all objects in the database."""
        return self._data

    @read_decorator
    @write_decorator
    def delete(self, hash: str) -> None:
        if hash in self._data:
            del self._data[hash]

class ResumeHashEntry:

    with open(CONFIG_FILENAME) as fobj:
        config_data = json.load(fobj)
    genres_map = config_data["genres"]
    resume_owner_name = config_data["name"]
    file_extension = config_data["default_file_extension"]


    def __init__(self, id: str=None, date: str=None, genre: str=None, notes: str=None):
        if not id:
            self.id = self._create_hash_label()
            self.date = self._get_datestamp(date)
            self.genre = self._validate_genre(genre)
            self.notes = notes
        else:
            self.id = id
            self.date = date
            self.genre = genre
            self.notes = notes

    @property
    def filename(self):
        return f"{self.resume_owner_name}_resume_{self.id}.{self.file_extension}"

    def _create_hash_label(self) -> str:
        return hex(hash(time.time()))[2:8]  # Slice off "0x" and limit to 6 chars total

    def _get_datestamp(self, hard_coded_date: str=None) -> str:
        date_obj = datetime.date(datetime.now())
        return date_obj.strftime("%Y-%m-%d")

    def _validate_genre(self, genre_input: str=None) -> str:
        """Returns input string suitable for use as the genre label if possible
        to suitably create from genre_input, else the emtpy string."""
        if not genre_input or not genre_input.lower() in self.genres_map:
            return ''
        return self.genres_map[genre_input.lower()]

class RHInterface:

    db = JsonDbConn()
    data = db.all_objects()

    def create(self,
               date: str=None,
               genre: str=None,
               notes: str=None):
        rhe_obj = ResumeHashEntry(date=date, genre=genre, notes=notes)
        print(f"{rhe_obj.date=}")
        self.db.create(rhe_obj.id, rhe_obj.date, rhe_obj.genre, rhe_obj.notes)
        return rhe_obj

    def lookup_one(self, id: str):
        data = self.db.lookup(id)
        return self._instantiate_rhe_obj(data)

    def _instantiate_rhe_obj(self, data: dict):
        return ResumeHashEntry(data["id"],
                               data["date"],
                               data["genre"],
                               data["notes"])


class ResumeHashHelperCLI:

    data_interface = RHInterface()

    usage_message = \
        """
        Usage message here
        """

    parser = argparse.ArgumentParser(
        usage=usage_message,
    )

    has_command = len(sys.argv) > 1 and not sys.argv[1].startswith("-")
    if has_command:parser.add_argument("command", default="new",
                        help="Optional subcommand to run")

    parser.add_argument("-g")  # action defaults to "store", i.e. store the value
    parser.add_argument("-n")
    parser.add_argument("-d", help="Optional hardcoded date")
    parser.add_argument("-fn", action='store_true')

    args = parser.parse_args()

    if not has_command:
        setattr(args, "command", "new")

    def __init__(self):
        if not hasattr(self.args, "command"):
            raise ValueError("Unrecognized command")
        getattr(self, self.args.command)()  # Calling the method returned by getattr()

    def new(self) -> None:
        """Creates a new RH."""
        date = genre = notes = None
        if self.args.g is not None:
            genre = self.args.g
        if self.args.n is not None:
            notes = self.args.n
        if self.args.d is not None:
            date = self.args.d
        rhe_obj = self.data_interface.create(date=date, genre=genre, notes=notes)
        self._output_one(rhe_obj)

    def _output_one(self, rhe_obj) -> None:
        print(f"{self.args.fn=}")
        if self.args.fn == True:
            print(rhe_obj.filename)
        else:
            print(rhe_obj.id)

    def lookup(self):
        pass

    def list(self):
        id_column_format = "{:^10}"
        date_column_format = "{:^10}"
        genre_column_format = "{:^10}"
        notes_column_format = "{:^10}"
        column_formatting = f"{id_column_format}|{date_column_format}|{genre_column_format}|{notes_column_format}"
        print(column_formatting.format("id", "date", "genre", "notes"))
        for id, fields in self.data_interface.data.items():
            date = genre = notes = ''
            if fields["date"]:
                date = fields["date"]
            if fields["genre"]:
                genre = fields["genre"]
            if fields["notes"]:
                notes = fields["notes"]
            print(column_formatting.format(id, date, genre, notes))

    def _get_rhe_object(self,
                        hash: str=None,
                        date: str=None,
                        genre: str=None,
                        notes: str=None):
        self._rhe_obj = None
        if hash:
            self._rhe_obj = ResumeHashEntry(hash)
        else:
            self._rhe_obj = ResumeHashEntry(date=date, genre=genre, notes=notes)

def main():
    ResumeHashHelperCLI()

if __name__ == "__main__":
    main()