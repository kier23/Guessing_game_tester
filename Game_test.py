import unittest
from unittest.mock import patch, MagicMock
import server  
import json
import os

class TestServerLogic(unittest.TestCase):
    def setUp(self):
        self.leaderboard_path = "leaderboard.json"
        if os.path.exists(self.leaderboard_path):
            os.rename(self.leaderboard_path, self.leaderboard_path + ".bak")

    def tearDown(self):
        if os.path.exists(self.leaderboard_path):
            os.remove(self.leaderboard_path)
        if os.path.exists(self.leaderboard_path + ".bak"):
            os.rename(self.leaderboard_path + ".bak", self.leaderboard_path)

    def simulate_client(self, inputs):
        conn = MagicMock()
        recv_iter = iter(inputs)

        def fake_recv(_):
            return next(recv_iter).encode()
        conn.recv.side_effect = fake_recv
        conn.send = MagicMock()
        conn.close = MagicMock()
        return conn

    def test_password_rejection(self):
        conn = self.simulate_client(["wrongpass"])
        server.handle_client(conn)
        conn.send.assert_any_call(b"Incorrect password. Connection closing.\n")
        conn.close.assert_called()

    def test_easy_bot_game_success(self):
        with patch("random.randint", side_effect=[20, 10, 30, 20]):
            conn = self.simulate_client([
                "letmein123",  
                "yes",         
                "easy"         
            ])
            server.handle_client(conn)

            sent_data = b''.join(call.args[0] for call in conn.send.call_args_list)
            self.assertIn(b"Congratulations!", sent_data)
            self.assertIn(b"Performance Rating", sent_data)

    def test_medium_manual_game_success(self):
        with patch("random.randint", return_value=42):
            conn = self.simulate_client([
                "letmein123",  # password
                "no",          # bot play
                "Kier",       # name
                "medium",      # difficulty
                "abc",         # invalid guess
                "100",         # too high
                "1",           # too low
                "42"           # correct
            ])
            server.handle_client(conn)

            sent_data = b''.join(call.args[0] for call in conn.send.call_args_list)
            self.assertIn(b"Please enter a valid number!", sent_data)
            self.assertIn(b"Congratulations!", sent_data)

    def test_hard_bot_game_with_multiple_guesses(self):
        guesses = [300, 200, 260, 250, 256]
        with patch("random.randint", side_effect=[256] + guesses):
            conn = self.simulate_client([
                "letmein123",
                "yes",
                "hard"
            ])
            server.handle_client(conn)

            calls = [call.args[0] for call in conn.send.call_args_list]
            combined = b''.join(calls)
            self.assertIn(b"Bot guesses: 256", combined)
            self.assertIn(b"The correct number was: 256", combined)

    def test_invalid_difficulty(self):
        conn = self.simulate_client([
            "letmein123",
            "yes",
            "insane"  
        ])
        server.handle_client(conn)

        conn.send.assert_any_call(b"Invalid difficulty!\n")
        conn.close.assert_called()

    def test_leaderboard_update(self):
        leaderboard = {"Kier": 10}
        server.update_leaderboard(leaderboard, "Kier", 5)
        self.assertEqual(leaderboard["Kier"], 5)

    def test_generate_number_difficulty(self):
        with patch("random.randint") as mock_rand:
            mock_rand.return_value = 10
            self.assertEqual(server.generate_number("easy"), 10)
            self.assertEqual(server.generate_number("medium"), 10)
            self.assertEqual(server.generate_number("hard"), 10)
            self.assertIsNone(server.generate_number("invalid"))

if __name__ == "__main__":
    unittest.main()
