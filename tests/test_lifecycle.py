import os
import tempfile
import unittest
from unittest.mock import patch

import start
import stop
from codex_arcade.app import read_session, session_path
from codex_arcade.stats import atomic_json


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old = os.environ.get("LOCALAPPDATA")
        os.environ["LOCALAPPDATA"] = self.tmp.name

    def tearDown(self):
        if self.old is None: os.environ.pop("LOCALAPPDATA", None)
        else: os.environ["LOCALAPPDATA"] = self.old
        self.tmp.cleanup()

    def test_stop_during_delay_prevents_launch(self):
        def delay_then_stop(_): stop.stop("project-a")
        with patch("start.time.sleep", delay_then_stop), patch("start.subprocess.Popen") as popen:
            self.assertFalse(start.start("project-a"))
            popen.assert_not_called()

    def test_other_workspace_stop_does_not_end_active_session(self):
        atomic_json(session_path(), {"token":"x", "workspace":"project-a", "status":"running", "pid":0})
        self.assertFalse(stop.stop("project-b"))
        self.assertEqual(read_session()["status"], "running")

    def test_stale_state_is_replaced_without_taskkill(self):
        atomic_json(session_path(), {"token":"old", "workspace":"project-a", "status":"running", "pid":99999999})
        with patch("start.time.sleep", lambda _: stop.stop("project-b")), patch("start.subprocess.Popen"):
            self.assertFalse(start.start("project-b"))
        self.assertNotEqual(read_session().get("token"), "old")
