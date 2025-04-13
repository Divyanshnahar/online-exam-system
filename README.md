# Online Exam System - Supabase Edition

This project has been migrated from MySQL to Supabase, a PostgreSQL-based cloud database service.

## Setup Instructions

### Prerequisites
- Python 3.8+
- PyQt6
- Supabase account

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory with your Supabase credentials:
   ```
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_KEY=your-supabase-anon-key
   ```

4. Set up your Supabase database with the following schema:

```sql
-- Create the users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    user_type VARCHAR(10) NOT NULL CHECK (user_type IN ('Student', 'Teacher', 'Admin'))
);

-- Create the exams table
CREATE TABLE exams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    teacher_username VARCHAR(50) NOT NULL,
    duration INT NOT NULL,
    status VARCHAR(10) DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'completed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    exam_date DATE,
    start_time TIME,
    end_time TIME,
    CONSTRAINT fk_teacher_username FOREIGN KEY (teacher_username) REFERENCES users(username)
);

-- Create the questions table
CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    exam_id INT NOT NULL,
    question_text TEXT NOT NULL,
    option1 VARCHAR(255) NOT NULL,
    option2 VARCHAR(255) NOT NULL,
    option3 VARCHAR(255) NOT NULL,
    option4 VARCHAR(255) NOT NULL,
    correct_answer VARCHAR(255) NOT NULL,
    CONSTRAINT fk_exam_id FOREIGN KEY (exam_id) REFERENCES exams(id)
);

-- Create the exam_results table
CREATE TABLE exam_results (
    id SERIAL PRIMARY KEY,
    exam_id INT NOT NULL,
    student_username VARCHAR(50) NOT NULL,
    score INT NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_exam_id_results FOREIGN KEY (exam_id) REFERENCES exams(id),
    CONSTRAINT fk_student_username FOREIGN KEY (student_username) REFERENCES users(username)
);

-- Create the student_answers table
CREATE TABLE student_answers (
    id SERIAL PRIMARY KEY,
    exam_id INT NOT NULL,
    question_id INT NOT NULL,
    student_username VARCHAR(50) NOT NULL,
    selected_answer VARCHAR(255) NOT NULL,
    is_correct BOOLEAN NOT NULL,
    CONSTRAINT fk_exam_id_answers FOREIGN KEY (exam_id) REFERENCES exams(id),
    CONSTRAINT fk_question_id FOREIGN KEY (question_id) REFERENCES questions(id),
    CONSTRAINT fk_student_username_answers FOREIGN KEY (student_username) REFERENCES users(username)
);
```

5. Run the application:
   ```
   python online_exam_system/main.py
   ```

## Features

- User authentication (students, teachers, admins)
- Create and manage exams with time scheduling
- Take exams during scheduled time slots
- Auto-submit when time expires
- View exam results
- Beautiful PyQt6 modern UI

## Database Migration Notes

This system has been fully migrated from MySQL to Supabase. Key changes include:

1. Added Supabase connection handler
2. Updated all database queries to use Supabase's API
3. Enhanced error handling for cloud database
4. Added validation for existing users during signup

## Testing the Connection

To test if your Supabase connection is working:

```python
python -c "from supabase_connection import test_connection; test_connection()"
``` 