import sqlite3
import os
import pandas as pd
from datetime import datetime
import shutil # For deleting attachment directories

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.csv_path = os.path.join(os.path.dirname(db_path), "FluxTracker_Master.csv")
        self.attachments_dir = os.path.join(os.path.dirname(db_path), "attachments")
        os.makedirs(self.attachments_dir, exist_ok=True)
        self._initialize_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _initialize_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Users table
            cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )""")
            # Parts/Assemblies table
            cursor.execute("""CREATE TABLE IF NOT EXISTS parts_assemblies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")
            # Engineering Changes table
            cursor.execute("""CREATE TABLE IF NOT EXISTS engineering_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                part_assembly_id INTEGER NOT NULL,
                change_number TEXT UNIQUE NOT NULL,
                description TEXT NOT NULL,
                reason TEXT,
                implemented_by TEXT NOT NULL,
                implementation_date DATE DEFAULT (DATE('now')),
                status TEXT DEFAULT 'Pending',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (part_assembly_id) REFERENCES parts_assemblies(id) ON DELETE CASCADE
            )""")
            # Attachments table - Enhanced for multiple file types
            cursor.execute("""CREATE TABLE IF NOT EXISTS attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                change_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                filepath TEXT UNIQUE NOT NULL,
                filetype TEXT,
                file_extension TEXT,
                file_size INTEGER,
                description TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (change_id) REFERENCES engineering_changes(id) ON DELETE CASCADE
            )""")
            # Settings table
            cursor.execute("""CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )""")
            
            # Initial data for users (if empty)
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                for name in ["Alex", "Jordan", "Sam"]:
                    cursor.execute("INSERT OR IGNORE INTO users (name) VALUES (?)", (name,))
            
            conn.commit()

    # --- SYNC METHODS ---
    def import_from_csv(self, custom_path=None):
        path = custom_path if custom_path else self.csv_path
        if not os.path.exists(path):
            return False
        try:
            df = pd.read_csv(path)
            required_cols = ['CHANGE_NUMBER', 'PART_ASSEMBLY_NAME', 'DESCRIPTION', 'REASON', 'IMPLEMENTED_BY', 'IMPLEMENTATION_DATE', 'STATUS', 'NOTES']
            if all(col in df.columns for col in required_cols):
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    # Clear existing engineering changes for a fresh import
                    cursor.execute("DELETE FROM engineering_changes")
                    # Also clear attachments and their files
                    cursor.execute("DELETE FROM attachments")
                    if os.path.exists(self.attachments_dir):
                        shutil.rmtree(self.attachments_dir)
                        os.makedirs(self.attachments_dir, exist_ok=True)

                    for _, row in df.iterrows():
                        # Get part_assembly_id, create if not exists
                        cursor.execute("SELECT id FROM parts_assemblies WHERE name = ?", (row['PART_ASSEMBLY_NAME'],))
                        part_assembly_id = cursor.fetchone()
                        if not part_assembly_id:
                            cursor.execute("INSERT INTO parts_assemblies (name) VALUES (?)", (row['PART_ASSEMBLY_NAME'],))
                            part_assembly_id = cursor.lastrowid
                        else:
                            part_assembly_id = part_assembly_id[0]

                        cursor.execute("""INSERT INTO engineering_changes (
                            part_assembly_id, change_number, description, reason, implemented_by, implementation_date, status, notes
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", 
                        (part_assembly_id, row['CHANGE_NUMBER'], row['DESCRIPTION'], row['REASON'], 
                         row['IMPLEMENTED_BY'], row['IMPLEMENTATION_DATE'], row['STATUS'], row['NOTES']))
                    conn.commit()
                return True
        except Exception as e:
            print(f"Import Error: {e}")
        return False

    def export_to_csv(self, custom_path=None):
        path = custom_path if custom_path else self.csv_path
        try:
            changes = self.get_all_engineering_changes()
            df = pd.DataFrame(changes, columns=["ID", "PART_ASSEMBLY_ID", "CHANGE_NUMBER", "DESCRIPTION", "REASON", "IMPLEMENTED_BY", "IMPLEMENTATION_DATE", "STATUS", "NOTES", "CREATED_AT"])
            
            # Join with parts_assemblies to get part name
            with self._get_connection() as conn:
                parts_df = pd.read_sql_query("SELECT id, name FROM parts_assemblies", conn)
            df = df.merge(parts_df, left_on='PART_ASSEMBLY_ID', right_on='id', how='left')
            df.rename(columns={'name': 'PART_ASSEMBLY_NAME'}, inplace=True)
            
            df_export = df[[
                'CHANGE_NUMBER', 'PART_ASSEMBLY_NAME', 'DESCRIPTION', 'REASON', 
                'IMPLEMENTED_BY', 'IMPLEMENTATION_DATE', 'STATUS', 'NOTES'
            ]]
            df_export.to_csv(path, index=False)
            return True
        except Exception as e:
            print(f"Export Error: {e}")
        return False

    # --- DATA METHODS ---
    def get_all_engineering_changes(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT * FROM engineering_changes ORDER BY created_at DESC""")
            return cursor.fetchall()

    def add_engineering_change(self, part_assembly_id, change_number, description, reason, implemented_by, implementation_date, status, notes):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO engineering_changes (
                part_assembly_id, change_number, description, reason, implemented_by, implementation_date, status, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", 
            (part_assembly_id, change_number, description, reason, implemented_by, implementation_date, status, notes))
            conn.commit()
            return cursor.lastrowid # Return the ID of the newly inserted change

    def delete_engineering_change(self, change_id):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Attachments are deleted via CASCADE from the foreign key constraint
            cursor.execute("DELETE FROM engineering_changes WHERE id = ?", (change_id,))
            conn.commit()
            # Also remove the attachment directory for this change
            change_attachments_dir = os.path.join(self.attachments_dir, str(change_id))
            if os.path.exists(change_attachments_dir):
                shutil.rmtree(change_attachments_dir)

    # --- USER MANAGEMENT ---
    def get_users(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM users ORDER BY name ASC")
            return [row[0] for row in cursor.fetchall()]

    def add_user(self, name):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def delete_user(self, name):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE name = ?", (name,))
            conn.commit()

    # --- PARTS/ASSEMBLIES MANAGEMENT ---
    def get_parts_assemblies(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM parts_assemblies ORDER BY name ASC")
            return cursor.fetchall()

    def get_part_assembly_by_id(self, part_id):
        """Get detailed information about a specific part/assembly"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, description, status, created_at FROM parts_assemblies WHERE id = ?", (part_id,))
            return cursor.fetchone()

    def get_changes_for_part(self, part_id):
        """Get all engineering changes for a specific part"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT * FROM engineering_changes 
                            WHERE part_assembly_id = ? 
                            ORDER BY created_at DESC""", (part_id,))
            return cursor.fetchall()

    def add_part_assembly(self, name, description="", status="Active"):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO parts_assemblies (name, description, status) VALUES (?, ?, ?)", (name, description, status))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def delete_part_assembly(self, part_assembly_id):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Engineering changes linked to this part will be deleted via CASCADE
            cursor.execute("DELETE FROM parts_assemblies WHERE id = ?", (part_assembly_id,))
            conn.commit()
            # Note: Attachments linked to these engineering changes will also be deleted via CASCADE
            # However, their physical files on disk will need to be cleaned up separately if no other changes reference them.
            # For simplicity, we'll rely on the change deletion to clean up its directory.

    # --- ATTACHMENT MANAGEMENT ---
    def add_attachment(self, change_id, filename, filepath, filetype, file_extension, file_size, description=""):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO attachments (
                change_id, filename, filepath, filetype, file_extension, file_size, description
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)""", 
            (change_id, filename, filepath, filetype, file_extension, file_size, description))
            conn.commit()
            return cursor.lastrowid

    def get_attachments_for_change(self, change_id):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT id, filename, filepath, filetype, file_extension, file_size, description, uploaded_at 
                            FROM attachments WHERE change_id = ? ORDER BY uploaded_at ASC""", (change_id,))
            return cursor.fetchall()

    def delete_attachment(self, attachment_id):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT filepath FROM attachments WHERE id = ?", (attachment_id,))
            filepath = cursor.fetchone()
            if filepath and os.path.exists(filepath[0]):
                os.remove(filepath[0])
            cursor.execute("DELETE FROM attachments WHERE id = ?", (attachment_id,))
            conn.commit()

    # --- SEARCH FUNCTIONALITY ---
    def search_engineering_changes(self, query):
        """Search for engineering changes with basic fuzzy support (multi-word LIKE)"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Split query into words for basic fuzzy matching across fields
            words = query.strip().split()
            if not words:
                return []
            
            # Build dynamic WHERE clause: each word must match at least one field
            where_clauses = []
            params = []
            for word in words:
                term = f'%{word}%'
                where_clauses.append("(ec.change_number LIKE ? OR ec.description LIKE ? OR ec.reason LIKE ? OR ec.notes LIKE ? OR pa.name LIKE ?)")
                params.extend([term, term, term, term, term])
            
            where_sql = " AND ".join(where_clauses)
            sql = f"""SELECT ec.id, pa.name, ec.change_number, ec.description, ec.reason, ec.implemented_by, ec.implementation_date, ec.status, ec.notes
                      FROM engineering_changes ec
                      JOIN parts_assemblies pa ON ec.part_assembly_id = pa.id
                      WHERE {where_sql}
                      ORDER BY ec.created_at DESC"""
            
            cursor.execute(sql, params)
            return cursor.fetchall()

    def search_parts_assemblies(self, query):
        """Search for parts/assemblies by name or description with basic fuzzy support"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            words = query.strip().split()
            if not words:
                return []
            
            where_clauses = []
            params = []
            for word in words:
                term = f'%{word}%'
                where_clauses.append("(name LIKE ? OR description LIKE ?) ")
                params.extend([term, term])
            
            where_sql = " AND ".join(where_clauses)
            sql = f"SELECT id, name, description, status FROM parts_assemblies WHERE {where_sql} ORDER BY name ASC"
            
            cursor.execute(sql, params)
            return cursor.fetchall()

    # --- SETTINGS METHODS ---
    def get_setting(self, key, default=None):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else default

    def save_setting(self, key, value):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
            conn.commit()
