from __future__ import annotations
import json
import sqlite3
from pathlib import Path

class Store:
    """A single-process SQLite checkpoint/side-effect ledger.

    The idempotency boundary is this database only, not arbitrary external APIs.
    Successful nodes are reused only under an exact workload signature.
    """
    def __init__(self, path: Path | str = ":memory:"):
        self.conn = sqlite3.connect(str(path))
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=FULL")
        self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS scopes(scope TEXT PRIMARY KEY, signature TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS checkpoints(scope TEXT, task INTEGER, stage TEXT, output TEXT,
                PRIMARY KEY(scope,task,stage));
            CREATE TABLE IF NOT EXISTS ledger(id INTEGER PRIMARY KEY, scope TEXT, task INTEGER, body TEXT);
            CREATE TABLE IF NOT EXISTS effects(scope TEXT, task INTEGER, body TEXT,
                PRIMARY KEY(scope,task));
        ''')
        self.conn.commit()

    def bind(self, scope, signature):
        row = self.conn.execute("SELECT signature FROM scopes WHERE scope=?", (scope,)).fetchone()
        if row and row[0] != signature:
            raise ValueError("checkpoint scope has a different workload/config/version")
        self.conn.execute("INSERT OR IGNORE INTO scopes VALUES(?,?)", (scope, signature))
        self.conn.commit()

    def get(self, scope, task, stage):
        row = self.conn.execute("SELECT output FROM checkpoints WHERE scope=? AND task=? AND stage=?",
                                (scope,task,stage)).fetchone()
        return json.loads(row[0]) if row else None

    def save(self, scope, task, stage, output):
        self.conn.execute("INSERT OR REPLACE INTO checkpoints VALUES(?,?,?,?)",
                          (scope,task,stage,json.dumps(output, sort_keys=True)))
        self.conn.commit()

    def commit(self, scope, task, output, idempotent):
        body = json.dumps(output, sort_keys=True)
        if idempotent:
            prior = self.conn.execute("SELECT body FROM effects WHERE scope=? AND task=?", (scope,task)).fetchone()
            if prior and prior[0] != body:
                raise ValueError("idempotency conflict")
            if prior:
                return False
            with self.conn:
                self.conn.execute("INSERT INTO effects VALUES(?,?,?)", (scope,task,body))
                self.conn.execute("INSERT INTO ledger(scope,task,body) VALUES(?,?,?)", (scope,task,body))
        else:
            with self.conn:
                self.conn.execute("INSERT INTO ledger(scope,task,body) VALUES(?,?,?)", (scope,task,body))
        return True

    def stats(self, scope):
        total, unique = self.conn.execute("SELECT COUNT(*),COUNT(DISTINCT task) FROM ledger WHERE scope=?", (scope,)).fetchone()
        return {"side_effects":total, "committed_tasks":unique, "duplicate_effects":total-unique}

    def close(self):
        self.conn.close()
