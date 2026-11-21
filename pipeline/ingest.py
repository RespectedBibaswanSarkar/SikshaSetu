"""SikshaSetu Ingestion Pipeline
Constructs content/sikshasetu_content.sqlite for the three core MIT OCW courses:
  - 6.006 (Intro to Algorithms, Spring 2020)
  - 6.100L (Intro to CS and Programming in Python, Fall 2022)
  - 18.06 (Linear Algebra, Spring 2010)

Creates tables: courses, modules, documents, chunks, chunks_fts, concepts, exercises, questions, question_sources.
Also exports JSON bundles for client offline use and hub serving.
"""

import json
import os
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"
DB_PATH = CONTENT_DIR / "sikshasetu_content.sqlite"

def init_db(con: sqlite3.Connection):
    cur = con.cursor()
    cur.executescript("""
    DROP TABLE IF EXISTS question_sources;
    DROP TABLE IF EXISTS questions;
    DROP TABLE IF EXISTS exercises;
    DROP TABLE IF EXISTS chunks_fts;
    DROP TABLE IF EXISTS chunks;
    DROP TABLE IF EXISTS documents;
    DROP TABLE IF EXISTS concepts;
    DROP TABLE IF EXISTS modules;
    DROP TABLE IF EXISTS courses;

    CREATE TABLE courses (
        slug TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        term TEXT NOT NULL,
        ocw_url TEXT NOT NULL,
        description TEXT,
        prerequisites TEXT,
        license TEXT DEFAULT 'CC BY-NC-SA 4.0',
        attribution TEXT
    );

    CREATE TABLE modules (
        id TEXT PRIMARY KEY,
        course_slug TEXT NOT NULL REFERENCES courses(slug),
        title TEXT NOT NULL,
        sort_order INTEGER NOT NULL,
        description TEXT
    );

    CREATE TABLE documents (
        id TEXT PRIMARY KEY,
        course_slug TEXT NOT NULL REFERENCES courses(slug),
        module_id TEXT REFERENCES modules(id),
        doc_type TEXT NOT NULL,
        title TEXT NOT NULL,
        url TEXT,
        page_count INTEGER DEFAULT 1,
        license TEXT DEFAULT 'CC BY-NC-SA 4.0',
        date_accessed TEXT
    );

    CREATE TABLE chunks (
        id TEXT PRIMARY KEY,
        document_id TEXT NOT NULL REFERENCES documents(id),
        course_slug TEXT NOT NULL REFERENCES courses(slug),
        module_id TEXT REFERENCES modules(id),
        title TEXT NOT NULL,
        page_number INTEGER DEFAULT 1,
        content TEXT NOT NULL,
        word_count INTEGER DEFAULT 0,
        source_ref TEXT
    );

    CREATE VIRTUAL TABLE chunks_fts USING fts5(
        chunk_id UNINDEXED,
        title,
        content,
        course_slug,
        source_ref
    );

    CREATE TABLE concepts (
        id TEXT PRIMARY KEY,
        course_slug TEXT NOT NULL REFERENCES courses(slug),
        name TEXT NOT NULL,
        description TEXT,
        prerequisites TEXT, -- JSON array of concept IDs
        module_ref TEXT,
        difficulty INTEGER DEFAULT 3
    );

    CREATE TABLE exercises (
        id TEXT PRIMARY KEY,
        course_slug TEXT NOT NULL REFERENCES courses(slug),
        module_id TEXT REFERENCES modules(id),
        concept_id TEXT REFERENCES concepts(id),
        title TEXT NOT NULL,
        problem_text TEXT NOT NULL,
        solution_text TEXT,
        source_ref TEXT,
        attribution TEXT
    );

    CREATE TABLE questions (
        id TEXT PRIMARY KEY,
        course_slug TEXT NOT NULL REFERENCES courses(slug),
        concept_id TEXT NOT NULL REFERENCES concepts(id),
        qtype TEXT NOT NULL, -- mcq, numeric, short_answer, code_trace, true_false
        question TEXT NOT NULL,
        options TEXT, -- JSON array of 4 choices for MCQ
        answer_index INTEGER, -- 0-3 for MCQ
        answer_text TEXT, -- expected text or numeric answer
        difficulty INTEGER DEFAULT 3,
        time_limit_sec INTEGER DEFAULT 60,
        explanation TEXT,
        source_ref TEXT,
        reviewed BOOLEAN DEFAULT 1
    );

    CREATE TABLE question_sources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id TEXT NOT NULL REFERENCES questions(id),
        chunk_id TEXT REFERENCES chunks(id),
        exercise_id TEXT REFERENCES exercises(id)
    );
    """)
    con.commit()

print("Initialized schema definitions.")
