import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from config import DATABASE_URL

def get_connection():
    """Get database connection"""
    return psycopg2.connect(DATABASE_URL)

def init_db():
    """Initialize database with tables"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reports (
                    id SERIAL PRIMARY KEY,
                    
                    -- User info
                    user_id BIGINT NOT NULL,
                    user_name TEXT NOT NULL,
                    
                    -- Report details
                    report_type TEXT NOT NULL,
                    report_text TEXT NOT NULL,
                    
                    -- Status tracking
                    status TEXT DEFAULT 'pending',
                    
                    -- Responsible person
                    responsible_user_id BIGINT,
                    responsible_user_name TEXT,
                    
                    -- Response
                    admin_response TEXT,
                    
                    -- Timestamps
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    taken_at TIMESTAMP,
                    completed_at TIMESTAMP
                )
            ''')
            
            # Indexes for faster queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_reports_user_id ON reports(user_id);
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status);
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_reports_responsible ON reports(responsible_user_id);
            ''')
            
            conn.commit()

def save_report(user_id: int, user_name: str, report_type: str, report_text: str) -> int:
    """Save new report"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO reports (user_id, user_name, report_type, report_text)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            ''', (user_id, user_name, report_type, report_text))
            report_id = cursor.fetchone()[0]
            conn.commit()
            return report_id

def take_report(report_id: int, worker_id: int, worker_name: str):
    """Worker takes report and starts working on it"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                UPDATE reports
                SET status = 'in_progress',
                    responsible_user_id = %s,
                    responsible_user_name = %s,
                    taken_at = CURRENT_TIMESTAMP
                WHERE id = %s
            ''', (worker_id, worker_name, report_id))
            conn.commit()

def complete_report(report_id: int, admin_response: str):
    """Complete report with answer"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                UPDATE reports
                SET status = 'completed',
                    admin_response = %s,
                    completed_at = CURRENT_TIMESTAMP
                WHERE id = %s
            ''', (admin_response, report_id))
            conn.commit()

def get_report(report_id: int) -> dict:
    """Get full report details"""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT * FROM reports WHERE id = %s', (report_id,))
            return cursor.fetchone()

def get_user_reports(user_id: int) -> list:
    """Get all reports by specific user"""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('''
                SELECT * FROM reports 
                WHERE user_id = %s 
                ORDER BY created_at DESC
            ''', (user_id,))
            return cursor.fetchall()

def get_reports_by_status(status: str) -> list:
    """Get all reports with specific status"""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('''
                SELECT * FROM reports 
                WHERE status = %s 
                ORDER BY created_at DESC
            ''', (status,))
            return cursor.fetchall()

def get_worker_reports(worker_id: int) -> list:
    """Get all reports assigned to specific worker"""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('''
                SELECT * FROM reports 
                WHERE responsible_user_id = %s 
                ORDER BY created_at DESC
            ''', (worker_id,))
            return cursor.fetchall()

def get_all_reports(limit: int = 50) -> list:
    """Get all reports with limit"""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('''
                SELECT * FROM reports 
                ORDER BY created_at DESC
                LIMIT %s
            ''', (limit,))
            return cursor.fetchall()

def get_report_stats() -> dict:
    """Get statistics about reports"""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
                    COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed
                FROM reports
            ''')
            return cursor.fetchone()

def delete_report(report_id: int) -> bool:
    """Delete report by ID (admin only)"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('DELETE FROM reports WHERE id = %s', (report_id,))
            conn.commit()
            return cursor.rowcount > 0

def search_reports(search_text: str) -> list:
    """Search reports by text"""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('''
                SELECT * FROM reports 
                WHERE report_text ILIKE %s 
                   OR user_name ILIKE %s
                   OR report_type ILIKE %s
                ORDER BY created_at DESC
                LIMIT 50
            ''', (f'%{search_text}%', f'%{search_text}%', f'%{search_text}%'))
            return cursor.fetchall()
def get_old_pending_reports(hours: int = 1) -> list:
    """Get pending reports older than specified hours"""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('''
                SELECT * FROM reports 
                WHERE status = 'pending'
                AND created_at < NOW() - INTERVAL '%s hours'
                ORDER BY created_at ASC
            ''', (hours,))
            return cursor.fetchall()
