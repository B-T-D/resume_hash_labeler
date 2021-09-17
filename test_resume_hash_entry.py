import unittest

from resume_hash import ResumeHashEntry, JsonDbConn

class TestHelloWorldThings(unittest.TestCase):

    db = JsonDbConn()

    def setUp(self):
        self.hashes_to_teardown = []
        self.RHE_blank = ResumeHashEntry()
        self.hashes_to_teardown.append(self.RHE_blank.hash)

        self.RHE_persistent_test_hash_data = {
            "genre": "swe",
            "notes": "TEST--persistent test entry"
        }
        self.RHE_persistent_test_hash = ResumeHashEntry(
            genre=self.RHE_persistent_test_hash_data["genre"],
            notes=self.RHE_persistent_test_hash_data["notes"]
        )
        self.persistent_lookup_hash = str(self.RHE_persistent_test_hash.hash)
        self.hashes_to_teardown.append(self.RHE_persistent_test_hash.hash)

    def test_init(self):
        self.assertIsInstance(self.RHE_blank, ResumeHashEntry)

    def test_lookup(self):
        lookup_obj = ResumeHashEntry(self.persistent_lookup_hash)
        self.assertEqual(
            self.RHE_persistent_test_hash_data["genre"],
            lookup_obj.genre
        )

    def test_unrecognized_genre_returns_empty_string(self):
        bad_genre = "foo"
        rhe = ResumeHashEntry()
        self.assertEqual(rhe._validate_genre(bad_genre), '')

    def tearDown(self):
        for hash in self.hashes_to_teardown:
            self.db.delete(hash)

if __name__ == "__main__":
    unittest.main()

