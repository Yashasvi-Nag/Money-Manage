import sqlite3


class Database:
    def __init__(self, db_path="finance.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self):
        if self.conn is not None:
            return
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._create_tables()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def _create_tables(self):
        self.cursor.executescript("""
            CREATE TABLE IF NOT EXISTS raw_files (
                id INTEGER PRIMARY KEY,
                filename TEXT,
                type TEXT,
                upload_date TEXT,
                statement_period TEXT,
                statement_type TEXT
            );
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY,
                date TEXT,
                description TEXT,
                amount REAL,
                type TEXT,
                category TEXT,
                source_file_id INTEGER,
                FOREIGN KEY(source_file_id) REFERENCES raw_files(id)
            );
            CREATE UNIQUE INDEX IF NOT EXISTS idx_transactions_dedup
                ON transactions(date, description, amount);
            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY,
                name TEXT,
                value REAL
            );
            CREATE TABLE IF NOT EXISTS liabilities (
                id INTEGER PRIMARY KEY,
                name TEXT,
                total_amount REAL,
                frequency TEXT,
                monthly_equivalent REAL
            );
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY,
                name TEXT,
                target_amount REAL,
                timeline_months INTEGER
            );
            CREATE TABLE IF NOT EXISTS category_mappings (
                id INTEGER PRIMARY KEY,
                keyword TEXT UNIQUE,
                category TEXT
            );
        """)
        self.conn.commit()

    def insert_raw_file(self, filename, ftype, upload_date, statement_period, statement_type):
        self.cursor.execute(
            "INSERT INTO raw_files (filename, type, upload_date, statement_period, statement_type) VALUES (?,?,?,?,?)",
            (filename, ftype, upload_date, statement_period, statement_type),
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def get_all_raw_files(self):
        self.cursor.execute("SELECT * FROM raw_files")
        return [dict(row) for row in self.cursor.fetchall()]

    def insert_transaction(self, date, description, amount, ttype, category, source_file_id):
        # Duplicate check
        self.cursor.execute(
            "SELECT id FROM transactions WHERE date=? AND description=? AND amount=?",
            (date, description, amount),
        )
        existing = self.cursor.fetchone()
        if existing:
            return existing[0]
        self.cursor.execute(
            "INSERT INTO transactions (date, description, amount, type, category, source_file_id) VALUES (?,?,?,?,?,?)",
            (date, description, amount, ttype, category, source_file_id),
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def get_transactions(self, year=None, month=None):
        if year and month:
            pattern = f"{year}-{month:02d}-%"
            self.cursor.execute(
                "SELECT * FROM transactions WHERE date LIKE ?", (pattern,)
            )
        elif year:
            pattern = f"{year}-%"
            self.cursor.execute(
                "SELECT * FROM transactions WHERE date LIKE ?", (pattern,)
            )
        else:
            self.cursor.execute("SELECT * FROM transactions")
        return [dict(row) for row in self.cursor.fetchall()]

    def insert_asset(self, name, value):
        self.cursor.execute(
            "INSERT INTO assets (name, value) VALUES (?,?)", (name, value)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def get_assets(self):
        self.cursor.execute("SELECT * FROM assets")
        return [dict(row) for row in self.cursor.fetchall()]

    def insert_liability(self, name, total_amount, frequency, monthly_equivalent):
        self.cursor.execute(
            "INSERT INTO liabilities (name, total_amount, frequency, monthly_equivalent) VALUES (?,?,?,?)",
            (name, total_amount, frequency, monthly_equivalent),
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def get_liabilities(self):
        self.cursor.execute("SELECT * FROM liabilities")
        return [dict(row) for row in self.cursor.fetchall()]

    def insert_goal(self, name, target_amount, timeline_months):
        self.cursor.execute(
            "INSERT INTO goals (name, target_amount, timeline_months) VALUES (?,?,?)",
            (name, target_amount, timeline_months),
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def get_goals(self):
        self.cursor.execute("SELECT * FROM goals")
        return [dict(row) for row in self.cursor.fetchall()]

    def insert_category_mapping(self, keyword, category):
        self.cursor.execute(
            "INSERT INTO category_mappings (keyword, category) VALUES (?,?) ON CONFLICT(keyword) DO UPDATE SET category=excluded.category",
            (keyword, category),
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def get_category_mappings(self):
        self.cursor.execute("SELECT * FROM category_mappings")
        return [dict(row) for row in self.cursor.fetchall()]
