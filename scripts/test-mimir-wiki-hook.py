"""Exercise archival data preservation and interrupted-write recovery."""

import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "wiki_hook", Path(__file__).with_name("mimir-wiki-hook.py"))
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.wiki = Path(self.temp.name)
        (self.wiki / "wiki").mkdir()
        (self.wiki / hook.FEEDBACK).write_text(hook.SEED)
        self.note = {"kind": "learning", "tags": ["caching"],
                     "note": "Cache keys need the version prefix.", "source": "Test fixture."}

    def append(self, session="one"):
        return hook.append_notes(self.wiki, session, [self.note])

    def archive(self, snapshot):
        return hook.archive_filed(self.wiki, snapshot["through"], snapshot["sha256"])

    def test_archive_preserves_reviewed_bytes_and_later_appends(self):
        self.append()
        snapshot = hook.pending(self.wiki)
        reviewed = hook.inbox_bytes(self.wiki)
        self.append("two")
        later = hook.inbox_bytes(self.wiki)[snapshot["through"]:]
        self.assertEqual(self.archive(snapshot), 1)
        self.assertTrue((self.wiki / hook.ARCHIVE).read_bytes().endswith(reviewed))
        self.assertEqual(hook.pending(self.wiki)["notes"].encode(), later)
        self.assertEqual(hook.inbox_bytes(self.wiki), hook.REFILE_SEED.encode() + later)
        # Capture retries stay idempotent even after the original is archived.
        self.assertEqual(self.append(), 0)

    def test_changed_reviewed_prefix_is_rejected_without_writes(self):
        self.append()
        snapshot = hook.pending(self.wiki)
        changed = hook.inbox_bytes(self.wiki).replace(b"Cache keys", b"Different")
        (self.wiki / hook.REFILE).write_bytes(changed)
        with self.assertRaisesRegex(RuntimeError, "reviewed complete inbox prefix"):
            self.archive(snapshot)
        self.assertEqual(hook.inbox_bytes(self.wiki), changed)
        self.assertFalse((self.wiki / hook.ARCHIVE).exists())

    def test_legacy_checkpoint_migrates_old_history(self):
        self.append()
        original = hook.inbox_bytes(self.wiki)
        snapshot = hook.pending(self.wiki)
        hook.mark_filed(self.wiki, snapshot["through"], snapshot["sha256"])
        self.assertEqual(hook.pending(self.wiki)["notes"], "")
        self.assertEqual(self.archive(hook.pending(self.wiki)), 1)
        self.assertTrue((self.wiki / hook.ARCHIVE).read_bytes().endswith(original))
        self.assertEqual(hook.inbox_bytes(self.wiki), hook.REFILE_SEED.encode())
        self.assertEqual(hook.pending(self.wiki)["notes"], "")

    def test_every_interrupted_write_recovers_once_before_new_capture(self):
        for failed_write in (1, 2, 3):
            with self.subTest(failed_write=failed_write), tempfile.TemporaryDirectory() as temp:
                wiki = Path(temp)
                (wiki / "wiki").mkdir()
                (wiki / hook.FEEDBACK).write_text(hook.SEED)
                hook.append_notes(wiki, "one", [self.note])
                snapshot = hook.pending(wiki)
                original = hook.inbox_bytes(wiki)
                real_write = hook.write_bytes
                calls = 0

                def interrupted(path, data):
                    nonlocal calls
                    calls += 1
                    if calls == failed_write:
                        raise OSError("simulated interruption")
                    real_write(path, data)

                with patch.object(hook, "write_bytes", interrupted):
                    with self.assertRaisesRegex(OSError, "simulated interruption"):
                        hook.archive_filed(wiki, snapshot["through"], snapshot["sha256"])
                self.assertTrue((wiki / hook.ARCHIVE_JOURNAL).exists())
                hook.append_notes(wiki, "two", [self.note])
                archived = (wiki / hook.ARCHIVE).read_bytes()
                self.assertTrue(archived.endswith(original))
                self.assertEqual(archived.count(b"Cache keys need"), 1)
                self.assertIn("Cache keys need", hook.pending(wiki)["notes"])
                self.assertFalse((wiki / hook.ARCHIVE_JOURNAL).exists())

    def test_recovery_refuses_unexpected_edits(self):
        self.append()
        snapshot = hook.pending(self.wiki)
        with patch.object(hook, "write_bytes", side_effect=OSError("interrupted")):
            with self.assertRaises(OSError):
                self.archive(snapshot)
        edited = b"Manual edit made while operation was interrupted.\n"
        (self.wiki / hook.REFILE).write_bytes(edited)
        with self.assertRaisesRegex(RuntimeError, "changed during interrupted archiving"):
            hook.pending(self.wiki)
        self.assertEqual(hook.inbox_bytes(self.wiki), edited)
        self.assertFalse((self.wiki / hook.ARCHIVE).exists())

    def test_empty_snapshot_does_not_create_an_archive(self):
        snapshot = hook.pending(self.wiki)
        self.assertEqual(self.archive(snapshot), 0)
        self.assertFalse((self.wiki / hook.ARCHIVE).exists())


if __name__ == "__main__":
    unittest.main()
