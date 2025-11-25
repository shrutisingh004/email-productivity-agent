import json
import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_path='data/emails.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database tables"""
        os.makedirs('data', exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Emails table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emails (
                id TEXT PRIMARY KEY,
                sender TEXT,
                subject TEXT,
                body TEXT,
                date TEXT,
                category TEXT,
                actions TEXT,
                summary TEXT,
                is_processed BOOLEAN DEFAULT FALSE,
                created_at TEXT
            )
        ''')
        
        # Prompts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prompts (
                name TEXT PRIMARY KEY,
                content TEXT,
                description TEXT,
                updated_at TEXT
            )
        ''')
        
        # Drafts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS drafts (
                id TEXT PRIMARY KEY,
                subject TEXT,
                body TEXT,
                to_email TEXT,
                in_reply_to TEXT,
                created_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Initialize default prompts if not exists
        self.init_default_prompts()
    
    def init_default_prompts(self):
        """Initialize default prompt templates"""
        default_prompts = {
            'categorization': {
                'content': '''Categorize emails into: Important, Newsletter, Spam, To-Do, Project Update.
Important: Urgent emails requiring immediate attention
Newsletter: Marketing or informational emails
Spam: Unwanted or promotional emails
To-Do: Emails containing direct requests requiring user action
Project Update: Progress reports or project status emails

Respond with only the category name.''',
                'description': 'Categorize emails into predefined categories'
            },
            'action_extraction': {
                'content': '''Extract tasks and action items from the email. Respond in JSON format:
{
    "tasks": [
        {
            "task": "description of the task",
            "deadline": "deadline if mentioned",
            "priority": "high/medium/low"
        }
    ]
}

If no tasks are found, return empty tasks array.''',
                'description': 'Extract action items and tasks from emails'
            },
            'auto_reply': {
                'content': '''Draft a polite and professional email reply. Consider the context and tone of the original email.
If it's a meeting request, ask for an agenda.
If it's a task request, acknowledge receipt and provide a tentative timeline.
Keep replies concise and professional.''',
                'description': 'Generate automatic email replies'
            },
            'summary': {
                'content': 'Summarize this email in 2-3 bullet points highlighting key information and required actions.',
                'description': 'Generate email summaries'
            }
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for name, prompt_data in default_prompts.items():
            cursor.execute('''
                INSERT OR IGNORE INTO prompts (name, content, description, updated_at)
                VALUES (?, ?, ?, ?)
            ''', (name, prompt_data['content'], prompt_data['description'], datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def load_mock_data(self):
        """Load mock email data"""
        mock_file = 'data/mock_inbox.json'
        if not os.path.exists(mock_file):
            self.create_mock_data()
        
        with open(mock_file, 'r') as f:
            emails = json.load(f)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for email in emails:
            cursor.execute('''
                INSERT OR REPLACE INTO emails (id, sender, subject, body, date, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                email['id'],
                email['from'],
                email['subject'],
                email['body'],
                email['date'],
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    def create_mock_data(self):
        """Create sample mock email data"""
        mock_emails = [
            {
                "id": "1",
                "from": "project.manager@company.com",
                "subject": "Weekly Project Sync Meeting",
                "body": "Hi team,\n\nLet's schedule our weekly project sync for Thursday at 2 PM. Please come prepared with updates on your respective tasks.\n\nAlso, remember that the Q3 report deadline is next Friday. Please submit your sections by EOD Thursday.\n\nBest regards,\nSarah",
                "date": "2024-01-15 09:30:00"
            },
            {
                "id": "2",
                "from": "hr@company.com",
                "subject": "Benefits Enrollment Reminder",
                "body": "Dear Employee,\n\nThis is a reminder that benefits enrollment closes this Friday. Please log into the portal and make your selections.\n\nIf you have any questions, contact HR.\n\nThank you,\nHR Department",
                "date": "2024-01-15 11:15:00"
            },
            {
                "id": "3",
                "from": "tech-news@newsletter.com",
                "subject": "AI Developments Weekly",
                "body": "This week in AI: New breakthroughs in language models, industry updates, and more...",
                "date": "2024-01-15 08:00:00"
            },
            {
                "id": "4",
                "from": "client@clientcompany.com",
                "subject": "Urgent: Website Issue",
                "body": "Hello,\n\nWe're experiencing a critical issue with our website. The payment gateway is not working. Can you please look into this immediately?\n\nWe need this fixed by end of day today.\n\nThanks,\nJohn Client",
                "date": "2024-01-15 10:45:00"
            },
            {
                "id": "5",
                "from": "marketing@company.com",
                "subject": "Q1 Marketing Campaign Results",
                "body": "Team,\n\nAttached are the Q1 marketing campaign results. We exceeded our KPIs by 15%. Great work everyone!\n\nOur next campaign planning session is scheduled for next Monday.\n\nRegards,\nMarketing Team",
                "date": "2024-01-14 16:20:00"
            },
            {
                "id": "6",
                "from": "noreply@bank.com",
                "subject": "Your statement is ready",
                "body": "Your monthly account statement is now available for download.",
                "date": "2024-01-14 14:30:00"
            },
            {
                "id": "7",
                "from": "ceo@company.com",
                "subject": "All Hands Meeting Next Week",
                "body": "Hello everyone,\n\nWe'll have an all-hands meeting next Wednesday at 10 AM to discuss company strategy and upcoming initiatives.\n\nPlease block your calendars.\n\nBest,\nCEO",
                "date": "2024-01-14 13:15:00"
            },
            {
                "id": "8",
                "from": "colleague@company.com",
                "subject": "Need your feedback on design mockups",
                "body": "Hi,\n\nCould you please review the attached design mockups and provide feedback by tomorrow? We need to finalize the designs for the client presentation on Friday.\n\nThanks!",
                "date": "2024-01-14 11:45:00"
            },
            {
                "id": "9",
                "from": "updates@linkedin.com",
                "subject": "Weekly digest from your network",
                "body": "See what's happening in your professional network this week...",
                "date": "2024-01-14 10:00:00"
            },
            {
                "id": "10",
                "from": "it-support@company.com",
                "subject": "System Maintenance Tonight",
                "body": "Important: There will be system maintenance tonight from 10 PM to 2 AM. Some services may be unavailable during this time.\n\nPlan your work accordingly.\n\nIT Department",
                "date": "2024-01-14 09:30:00"
            }
        ]
        
        os.makedirs('data', exist_ok=True)
        with open('data/mock_inbox.json', 'w') as f:
            json.dump(mock_emails, f, indent=2)
    
    def get_emails(self):
        """Get all emails"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM emails ORDER BY date DESC')
        emails = [dict(row) for row in cursor.fetchall()]
        
        # Parse JSON fields
        for email in emails:
            if email.get('actions'):
                try:
                    email['actions'] = json.loads(email['actions'])
                except:
                    email['actions'] = {}
        
        conn.close()
        return emails
    
    def get_email(self, email_id):
        """Get specific email by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM emails WHERE id = ?', (email_id,))
        email = cursor.fetchone()
        
        if email:
            email_dict = dict(email)
            if email_dict.get('actions'):
                try:
                    email_dict['actions'] = json.loads(email_dict['actions'])
                except:
                    email_dict['actions'] = {}
            return email_dict
        
        return None
    
    def update_email_processing(self, email_id, processing_results):
        """Update email with processing results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE emails 
            SET category = ?, actions = ?, summary = ?, is_processed = TRUE
            WHERE id = ?
        ''', (
            processing_results.get('category'),
            json.dumps(processing_results.get('actions', {})),
            processing_results.get('summary'),
            email_id
        ))
        
        conn.commit()
        conn.close()
    
    def get_prompts(self):
        """Get all prompt templates"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM prompts')
        prompts = {row['name']: dict(row) for row in cursor.fetchall()}
        
        conn.close()
        return prompts
    
    def update_prompt(self, name, content):
        """Update a prompt template"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE prompts 
            SET content = ?, updated_at = ?
            WHERE name = ?
        ''', (content, datetime.now().isoformat(), name))
        
        conn.commit()
        conn.close()
    
    def save_draft(self, draft_data):
        """Save email draft"""
        import uuid
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        draft_id = str(uuid.uuid4())
        
        cursor.execute('''
            INSERT INTO drafts (id, subject, body, to_email, in_reply_to, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            draft_id,
            draft_data['subject'],
            draft_data['body'],
            draft_data['to'],
            draft_data.get('in_reply_to'),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        return draft_id