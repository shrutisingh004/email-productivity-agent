from flask import Flask, request, jsonify
from flask_cors import CORS
from email_processor import EmailProcessor
from database import Database
import json
import os

app = Flask(__name__)
CORS(app)

# Initialize components
db = Database()
email_processor = EmailProcessor()

@app.route('/api/emails', methods=['GET'])
def get_emails():
    emails = db.get_emails()
    return jsonify(emails)

@app.route('/api/emails/load-mock', methods=['POST'])
def load_mock_emails():
    try:
        db.load_mock_data()
        return jsonify({"message": "Mock data loaded successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/emails/<email_id>', methods=['GET'])
def get_email(email_id):
    email = db.get_email(email_id)
    if email:
        return jsonify(email)
    return jsonify({"error": "Email not found"}), 404

@app.route('/api/emails/example@gmail.com/process', methods=['POST'])
def process_email(email_id):
    try:
        email = db.get_email(email_id)
        if not email:
            return jsonify({"error": "Email not found"}), 404
        
        # Get processing type from request
        data = request.get_json()
        process_type = data.get('type', 'all')
        
        result = email_processor.process_email(email, process_type)
        db.update_email_processing(email_id, result)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/prompts', methods=['GET'])
def get_prompts():
    prompts = db.get_prompts()
    return jsonify(prompts)

@app.route('/api/prompts', methods=['POST'])
def update_prompt():
    try:
        data = request.get_json()
        prompt_name = data.get('name')
        prompt_content = data.get('content')
        
        if not prompt_name or not prompt_content:
            return jsonify({"error": "Name and content are required"}), 400
        
        db.update_prompt(prompt_name, prompt_content)
        return jsonify({"message": "Prompt updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat_with_agent():
    try:
        data = request.get_json()
        email_id = data.get('email_id')
        query = data.get('query')
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        if email_id:
            # Chat about specific email
            email = db.get_email(email_id)
            response = email_processor.chat_about_email(email, query)
        else:
            # General inbox chat
            emails = db.get_emails()
            response = email_processor.chat_about_inbox(emails, query)
        
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/drafts', methods=['POST'])
def create_draft():
    try:
        data = request.get_json()
        draft_data = {
            'subject': data.get('subject'),
            'body': data.get('body'),
            'to': data.get('to'),
            'in_reply_to': data.get('in_reply_to')
        }
        
        draft_id = db.save_draft(draft_data)
        return jsonify({"draft_id": draft_id, "message": "Draft saved successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/drafts/generate', methods=['POST'])
def generate_draft():
    try:
        data = request.get_json()
        email_id = data.get('email_id')
        instructions = data.get('instructions', '')
        
        email = db.get_email(email_id) if email_id else None
        draft = email_processor.generate_draft(email, instructions)
        
        return jsonify(draft)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)