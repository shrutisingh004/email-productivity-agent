import os
import json
from openai import OpenAI
from database import Database

class EmailProcessor:
    def __init__(self):
        self.db = Database()
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY', 'your-api-key'))
        self.model = "gpt-3.5-turbo"
    
    def call_llm(self, prompt, system_message=None):
        try:
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"LLM Error: {e}")
            return f"Error processing request: {str(e)}"
    
    def process_email(self, email, process_type='all'):
        prompts = self.db.get_prompts()
        results = {}
        
        if process_type in ['all', 'categorize']:
            # Categorize email
            categorization_prompt = prompts['categorization']['content']
            prompt = f"{categorization_prompt}\n\nEmail Content:\nFrom: {email['from']}\nSubject: {email['subject']}\nBody: {email['body']}"
            category = self.call_llm(prompt, "You are an email categorization assistant.")
            results['category'] = category
        
        if process_type in ['all', 'actions']:
            # Extract action items
            action_prompt = prompts['action_extraction']['content']
            prompt = f"{action_prompt}\n\nEmail Content:\n{email['body']}"
            actions = self.call_llm(prompt, "You are an action item extraction assistant.")
            try:
                results['actions'] = json.loads(actions)
            except:
                results['actions'] = {"tasks": []}
        
        if process_type in ['all', 'summary']:
            # Generate summary
            summary_prompt = prompts.get('summary', {}).get('content', 'Summarize this email concisely:')
            prompt = f"{summary_prompt}\n\nEmail: {email['body']}"
            summary = self.call_llm(prompt, "You are an email summarization assistant.")
            results['summary'] = summary
        
        return results
    
    def chat_about_email(self, email, query):
        context = f"""
        Email Details:
        From: {email['from']}
        Subject: {email['subject']}
        Date: {email['date']}
        Body: {email['body']}
        
        Processing Results:
        Category: {email.get('category', 'Not categorized')}
        Actions: {json.dumps(email.get('actions', {}), indent=2)}
        Summary: {email.get('summary', 'Not summarized')}
        """
        
        prompt = f"Context:\n{context}\n\nUser Question: {query}"
        return self.call_llm(prompt, "You are an email productivity assistant. Help the user understand and manage their emails.")
    
    def chat_about_inbox(self, emails, query):
        inbox_context = f"Total emails: {len(emails)}\n\n"
        
        for i, email in enumerate(emails[:10]):  # Limit context
            inbox_context += f"{i+1}. From: {email['from']}, Subject: {email['subject']}, Category: {email.get('category', 'Unknown')}\n"
        
        prompt = f"Inbox Overview:\n{inbox_context}\n\nUser Question: {query}"
        return self.call_llm(prompt, "You are an inbox management assistant. Help the user understand and manage their entire email inbox.")
    
    def generate_draft(self, original_email=None, instructions=""):
        prompts = self.db.get_prompts()
        draft_prompt = prompts['auto_reply']['content']
        
        if original_email:
            context = f"""
            Original Email:
            From: {original_email['from']}
            Subject: {original_email['subject']}
            Body: {original_email['body']}
            
            Additional Instructions: {instructions}
            """
            prompt = f"{draft_prompt}\n\n{context}"
        else:
            prompt = f"{draft_prompt}\n\nNew Email Instructions: {instructions}"
        
        draft = self.call_llm(prompt, "You are an email drafting assistant. Create professional email drafts.")
        
        # Parse the draft to extract subject and body
        lines = draft.split('\n')
        subject = "Draft Email"
        body = draft
        
        for i, line in enumerate(lines):
            if line.lower().startswith('subject:'):
                subject = line.replace('Subject:', '').strip()
                body = '\n'.join(lines[i+1:])
                break
        
        return {
            "subject": subject,
            "body": body.strip(),
            "to": original_email['from'] if original_email else "",
            "in_reply_to": original_email['id'] if original_email else None

        }

