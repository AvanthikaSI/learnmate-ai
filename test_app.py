"""
test_app.py - Comprehensive test suite for LearnMate AI.

Tests all core components:
1. Database operations (sessions, interactions, cascade delete, update)
2. Prompts and persona construction
3. Multi-format export engine (Markdown, TXT, PDF)
4. Environment variable and secret protection
"""

import os
import unittest
import database
import prompts
import exporter


class TestLearnMateAI(unittest.TestCase):
    def setUp(self):
        """Set up an isolated test database for each test run."""
        self.test_db = "test_learnmate_suite.db"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        database.init_db(self.test_db)

    def tearDown(self):
        """Clean up the test database after each test run."""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    # -----------------------------------------------------
    # Phase 3 & 4: Database & Session Management Tests
    # -----------------------------------------------------
    def test_database_session_crud(self):
        """Tests session creation, retrieval, updating, and cascade deletion."""
        # 1. Create Session
        s_id = database.create_session("Operating Systems", "OS Virtual Memory", db_path=self.test_db)
        self.assertIsNotNone(s_id)

        # 2. Retrieve Session
        session = database.get_session(s_id, db_path=self.test_db)
        self.assertEqual(session["topic"], "Operating Systems")
        self.assertEqual(session["title"], "OS Virtual Memory")

        # 3. Add Interactions
        i1 = database.add_interaction(
            s_id,
            "Explain Concept",
            "What is paging?",
            "Paging is a memory management scheme...",
            db_path=self.test_db
        )
        i2 = database.add_interaction(
            s_id,
            "Real-Life Example",
            "How does Linux use paging?",
            "Linux divides physical memory into fixed-size 4KB pages...",
            db_path=self.test_db
        )
        self.assertIsNotNone(i1)
        self.assertIsNotNone(i2)

        # 4. Fetch interactions
        interactions = database.get_interactions_for_session(s_id, db_path=self.test_db)
        self.assertEqual(len(interactions), 2)
        self.assertEqual(interactions[0]["activity"], "Explain Concept")
        self.assertEqual(interactions[1]["activity"], "Real-Life Example")

        # 5. Update Title
        renamed = database.update_session_title(s_id, "Advanced OS Paging", db_path=self.test_db)
        self.assertTrue(renamed)
        updated_s = database.get_session(s_id, db_path=self.test_db)
        self.assertEqual(updated_s["title"], "Advanced OS Paging")

        # 6. Delete Session (Test Cascade Delete)
        deleted = database.delete_session(s_id, db_path=self.test_db)
        self.assertTrue(deleted)
        self.assertIsNone(database.get_session(s_id, db_path=self.test_db))
        self.assertEqual(len(database.get_interactions_for_session(s_id, db_path=self.test_db)), 0)

    # -----------------------------------------------------
    # Phase 2 & 5: Prompts & Persona Tests
    # -----------------------------------------------------
    def test_prompts_and_persona(self):
        """Verifies persona instructions and prompt building across all activities."""
        # Persona checks
        self.assertIn("LearnMate AI", prompts.TUTOR_PERSONA)
        self.assertIn("pedagogical", prompts.TUTOR_PERSONA.lower())

        # Test activities
        p_concept = prompts.build_prompt("Explain Concept", "Binary Search")
        self.assertIn("Binary Search", p_concept)
        self.assertIn("TL;DR", p_concept)
        self.assertIn("Analogy", p_concept)

        p_quiz = prompts.build_prompt("Generate Quiz", "Recursion")
        self.assertIn("Recursion", p_quiz)
        self.assertIn("Answer Key", p_quiz)

        p_example = prompts.build_prompt("Real-Life Example", "Kafka")
        self.assertIn("Kafka", p_example)
        self.assertIn("Deep-Dive Case Study", p_example)

        p_ask = prompts.build_prompt("Ask Anything", "SQL", question="What is 3NF?")
        self.assertIn("3NF", p_ask)

        p_eval = prompts.build_prompt(
            "Evaluate Answer",
            "Sorting",
            question="What is the worst-case time complexity of QuickSort?",
            answer="O(n^2) when the pivot chosen is always the minimum or maximum element."
        )
        self.assertIn("Verdict", p_eval)
        self.assertIn("Strengths", p_eval)
        self.assertIn("O(n^2)", p_eval)

        p_followup = prompts.build_prompt("Follow-up", "Sorting", question="Can you show me randomized pivot?")
        self.assertIn("randomized pivot", p_followup)

    # -----------------------------------------------------
    # Phase 6: Export Utility Tests
    # -----------------------------------------------------
    def test_export_utilities(self):
        """Verifies Markdown, Plain Text, and PDF export generation."""
        mock_session = {
            "id": 99,
            "topic": "Computer Networks",
            "title": "TCP 3-Way Handshake",
            "created_at": "2026-11-18 20:00:00"
        }
        mock_interactions = [
            {
                "activity": "Explain Concept",
                "user_prompt": "Explain SYN, SYN-ACK, ACK",
                "ai_response": "The 3-way handshake establishes a reliable TCP connection.",
                "created_at": "2026-11-18 20:01:00"
            },
            {
                "activity": "Evaluate Answer",
                "user_prompt": "My answer: SYN synchronizes sequence numbers.",
                "ai_response": "Correct! It negotiates initial sequence numbers (ISN).",
                "created_at": "2026-11-18 20:05:00"
            }
        ]

        # 1. Test Markdown
        md = exporter.export_to_markdown(mock_session, mock_interactions)
        self.assertIn("# LearnMate AI", md)
        self.assertIn("TCP 3-Way Handshake", md)
        self.assertIn("SYN, SYN-ACK, ACK", md)

        # 2. Test Plain Text
        txt = exporter.export_to_txt(mock_session, mock_interactions)
        self.assertIn("LEARNMATE AI", txt)
        self.assertIn("Computer Networks", txt)

        # 3. Test PDF (Includes Unicode character sanitization)
        pdf_bytes = exporter.export_to_pdf(mock_session, mock_interactions)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), 1000)
        # PDF files always begin with the magic header '%PDF-'
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))

    # -----------------------------------------------------
    # Security & Configuration Tests
    # -----------------------------------------------------
    def test_security_and_gitignore(self):
        """Ensures that sensitive files (.env, *.db) are excluded in .gitignore."""
        with open(".gitignore", "r") as f:
            gitignore_content = f.read()

        self.assertIn(".env", gitignore_content)
        self.assertIn(".venv/", gitignore_content)
        self.assertIn("*.db", gitignore_content)


if __name__ == "__main__":
    unittest.main()
