import json
from datetime import datetime
import time
import argparse
import sys

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
        if hash in self._data:
            return self._data[hash]
        return {}

    @read_decorator
    @write_decorator
    def delete(self, hash: str) -> None:
        if hash in self._data:
            del self._data[hash]

class ResumeHashEntry:

    db = JsonDbConn()

    genres_map = {  # Keys are input string, values are the finite set of recognized genre labels. I.e. inputs --manyToOne--> labels
                     "lfa": "lfa",  # TODO refactor to support verbose labels while keeping this repo public-GH safe
                     "swe": "swe",
                    "lfnp": "lfnp"
    }

    def __init__(self, hash: str=None, date: str=None, genre: str=None, notes: str=None):
        data = self.db.lookup(hash)
        if not data:
            self.hash = self._create_hash_label()
            self.date = self._get_datestamp(date)
            self.genre = self._validate_genre(genre)
            self.notes = notes
            self.db.create_hash(self.hash, self.date, self.genre, self.notes)
        else:
            self.hash = hash
            self.date = data["date"]
            self.genre = data["genre"]
            self.notes = data["notes"]

    def _create_hash_label(self) -> str:
        return hex(hash(time.time()))[2:]  # Slice off "0x"

    def _get_datestamp(self, hard_coded_date: str=None) -> str:
        if hard_coded_date:
            raise NotImplementedError
        date_obj = datetime.date(datetime.now())
        return date_obj.strftime("%Y-%m-%d")

    def _validate_genre(self, genre_input: str=None) -> str:
        """Returns input string suitable for use as the genre label if possible
        to suitably create from genre_input, else the emtpy string."""
        if not genre_input or not genre_input.lower() in self.genres_map:
            return ''
        return self.genres_map[genre_input.lower()]

class ResumeHashHelperCLI:  # Singleton

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

    # TODO implement the -fname flag in a public-GH safe way

    args = parser.parse_args()

    if not has_command:
        setattr(args, "command", "new")

    def __init__(self):
        if not hasattr(self.args, "command"):
            raise ValueError("Unrecognized command")
        getattr(self, self.args.command)()  # Calling the method returned by getattr()

    def new(self) -> None:
        """Creates a new RH and prints it to the command line."""
        date = genre = notes = None
        if self.args.g is not None:
            genre = self.args.g
        if self.args.n is not None:
            notes = self.args.n
        self._get_rhe_object(date=date, genre=genre, notes=notes)  # TODO prompt if  the genre isn't recognize, allow retry
        print(self._rhe_obj.hash)

    def lookup(self):
        pass

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