import unittest
import os
import tempfile
import shutil
import pandas as pd
from database import DatabaseManager

class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_fluxtracker.db")
        self.db = DatabaseManager(self.db_path)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_initialization(self):
        self.assertTrue(os.path.exists(self.db_path))
        self.assertTrue(os.path.exists(self.db.attachments_dir))
        users = self.db.get_users()
        self.assertIn("Alex", users)
        self.assertIn("Jordan", users)
        self.assertIn("Sam", users)

    def test_user_management(self):
        self.assertTrue(self.db.add_user("Taylor"))
        self.assertFalse(self.db.add_user("Taylor")) # Duplicate user
        users = self.db.get_users()
        self.assertIn("Taylor", users)

        self.db.delete_user("Taylor")
        users_after = self.db.get_users()
        self.assertNotIn("Taylor", users_after)

    def test_parts_assemblies_management(self):
        self.assertTrue(self.db.add_part_assembly("Widget-A", "Standard Widget", "Active"))
        self.assertFalse(self.db.add_part_assembly("Widget-A", "Duplicate Widget"))

        parts = self.db.get_parts_assemblies()
        self.assertEqual(len(parts), 1)
        part_id, name = parts[0]
        self.assertEqual(name, "Widget-A")

        detail = self.db.get_part_assembly_by_id(part_id)
        self.assertIsNotNone(detail)
        self.assertEqual(detail[1], "Widget-A")
        self.assertEqual(detail[2], "Standard Widget")

    def test_engineering_changes_and_cascade(self):
        self.db.add_part_assembly("Assembly-1", "Main Assembly")
        parts = self.db.get_parts_assemblies()
        part_id = parts[0][0]

        change_id = self.db.add_engineering_change(
            part_assembly_id=part_id,
            change_number="EC-1001",
            description="Upgraded sensor module",
            reason="Improve accuracy",
            implemented_by="Alex",
            implementation_date="2026-04-01",
            status="Approved",
            notes="Requires reboot"
        )
        self.assertIsNotNone(change_id)

        changes = self.db.get_all_engineering_changes()
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0][2], "EC-1001")

        part_changes = self.db.get_changes_for_part(part_id)
        self.assertEqual(len(part_changes), 1)

        # Test attachment creation & physical directory cleanup on change delete
        change_att_dir = os.path.join(self.db.attachments_dir, str(change_id))
        os.makedirs(change_att_dir, exist_ok=True)
        dummy_file = os.path.join(change_att_dir, "test.txt")
        with open(dummy_file, "w") as f:
            f.write("test attachment")

        att_id = self.db.add_attachment(
            change_id=change_id,
            filename="test.txt",
            filepath=dummy_file,
            filetype="text/plain",
            file_extension=".txt",
            file_size=15,
            description="Test Doc"
        )
        attachments = self.db.get_attachments_for_change(change_id)
        self.assertEqual(len(attachments), 1)

        # Delete engineering change and ensure directory is removed
        self.db.delete_engineering_change(change_id)
        self.assertEqual(len(self.db.get_all_engineering_changes()), 0)
        self.assertFalse(os.path.exists(change_att_dir))

    def test_delete_part_assembly_cleans_attachments(self):
        self.db.add_part_assembly("Assembly-2", "Secondary Assembly")
        part_id = self.db.get_parts_assemblies()[0][0]

        change_id = self.db.add_engineering_change(
            part_assembly_id=part_id,
            change_number="EC-1002",
            description="Replaced connector",
            reason="Faulty component",
            implemented_by="Jordan",
            implementation_date="2026-04-02",
            status="Implemented",
            notes="Done"
        )

        change_att_dir = os.path.join(self.db.attachments_dir, str(change_id))
        os.makedirs(change_att_dir, exist_ok=True)
        dummy_file = os.path.join(change_att_dir, "drawing.dwg")
        with open(dummy_file, "w") as f:
            f.write("drawing data")

        self.db.add_attachment(change_id, "drawing.dwg", dummy_file, "application/dwg", ".dwg", 12)

        # Delete part assembly
        self.db.delete_part_assembly(part_id)
        self.assertEqual(len(self.db.get_parts_assemblies()), 0)
        self.assertEqual(len(self.db.get_all_engineering_changes()), 0)
        self.assertFalse(os.path.exists(change_att_dir))

    def test_delete_attachment_file(self):
        self.db.add_part_assembly("Part-X", "Part X")
        part_id = self.db.get_parts_assemblies()[0][0]
        change_id = self.db.add_engineering_change(part_id, "EC-1003", "Desc", "Reason", "Sam", "2026-04-03", "Pending", "")

        att_dir = os.path.join(self.db.attachments_dir, str(change_id))
        os.makedirs(att_dir, exist_ok=True)
        filepath = os.path.join(att_dir, "spec.pdf")
        with open(filepath, "w") as f:
            f.write("pdf data")

        att_id = self.db.add_attachment(change_id, "spec.pdf", filepath, "application/pdf", ".pdf", 8)
        self.assertTrue(os.path.exists(filepath))

        self.db.delete_attachment(att_id)
        self.assertFalse(os.path.exists(filepath))
        self.assertEqual(len(self.db.get_attachments_for_change(change_id)), 0)

    def test_search_functions(self):
        self.db.add_part_assembly("Bracket-Alpha", "High strength bracket")
        part_id = self.db.get_parts_assemblies()[0][0]
        self.db.add_engineering_change(part_id, "EC-2001", "Modified mounting holes", "Weight reduction", "Alex", "2026-04-01", "Approved", "Check clearance")

        # Part search
        part_results = self.db.search_parts_assemblies("Bracket")
        self.assertEqual(len(part_results), 1)
        self.assertEqual(part_results[0][1], "Bracket-Alpha")

        # Empty query
        self.assertEqual(self.db.search_parts_assemblies(""), [])
        self.assertEqual(self.db.search_engineering_changes(""), [])

        # Change search
        change_results = self.db.search_engineering_changes("Bracket mounting")
        self.assertEqual(len(change_results), 1)
        self.assertEqual(change_results[0][2], "EC-2001")

    def test_settings_methods(self):
        self.assertIsNone(self.db.get_setting("non_existent_key"))
        self.assertEqual(self.db.get_setting("non_existent_key", default="default_val"), "default_val")

        self.db.save_setting("theme", "dark")
        self.assertEqual(self.db.get_setting("theme"), "dark")

        self.db.save_setting("theme", "light")
        self.assertEqual(self.db.get_setting("theme"), "light")

    def test_csv_export_and_import(self):
        self.db.add_part_assembly("Gear-B", "Bevel Gear")
        part_id = self.db.get_parts_assemblies()[0][0]
        self.db.add_engineering_change(part_id, "EC-3001", "Adjust tooth pitch", "Reduce noise", "Jordan", "2026-04-05", "Implemented", "N/A")

        csv_file = os.path.join(self.test_dir, "export_test.csv")
        self.assertTrue(self.db.export_to_csv(csv_file))
        self.assertTrue(os.path.exists(csv_file))

        # Test importing back into a clean DB
        new_db_path = os.path.join(self.test_dir, "imported_fluxtracker.db")
        new_db = DatabaseManager(new_db_path)
        self.assertTrue(new_db.import_from_csv(csv_file))

        changes = new_db.get_all_engineering_changes()
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0][2], "EC-3001")

if __name__ == '__main__':
    unittest.main()
