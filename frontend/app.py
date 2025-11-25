import streamlit as st
import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:5000"

def init_session_state():
    if 'emails' not in st.session_state:
        st.session_state.emails = []
    if 'selected_email' not in st.session_state:
        st.session_state.selected_email = None
    if 'prompts' not in st.session_state:
        st.session_state.prompts = {}
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

def call_backend(endpoint, method='GET', data=None):
    try:
        url = f"{BACKEND_URL}{endpoint}"
        if method == 'GET':
            response = requests.get(url)
        elif method == 'POST':
            response = requests.post(url, json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Backend error: {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

def load_emails():
    result = call_backend('/api/emails')
    if result:
        st.session_state.emails = result

def load_prompts():
    result = call_backend('/api/prompts')
    if result:
        st.session_state.prompts = result

def main():
    st.set_page_config(
        page_title="Email Productivity Agent",
        page_icon="📧",
        layout="wide"
    )
    
    st.title("Email Productivity Agent")
    st.markdown("---")
    
    init_session_state()
    
    # Load data on startup
    if not st.session_state.emails:
        load_emails()
    if not st.session_state.prompts:
        load_prompts()
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        page = st.radio("Go to", ["Inbox", "Prompt Configuration", "Email Agent Chat", "Draft Composer"])
        
        st.markdown("---")
        st.header("Actions")
        
        if st.button("Load Mock Inbox"):
            result = call_backend('/api/emails/load-mock', 'POST')
            if result:
                st.success("Mock inbox loaded!")
                load_emails()
        
        if st.button("Refresh Data"):
            load_emails()
            load_prompts()
            st.success("Data refreshed!")
    
    # Main content based on selected page
    if page == "Inbox":
        show_inbox()
    elif page == "Prompt Configuration":
        show_prompt_config()
    elif page == "Email Agent Chat":
        show_email_agent()
    elif page == "Draft Composer":
        show_draft_composer()

def show_inbox():
    st.header("Email Inbox")
    
    if not st.session_state.emails:
        st.info("No emails loaded. Click 'Load Mock Inbox' to get started.")
        return
    
    # Email list
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Emails")
        for email in st.session_state.emails:
            with st.container():
                # Display email preview
                is_selected = st.session_state.selected_email and st.session_state.selected_email['id'] == email['id']
                
                if st.button(
                    f"**{email['subject']}**\n"
                    f"From: {email['sender']}\n"
                    f"Date: {email['date'][:16]}\n"
                    f"Category: {email.get('category', 'Not processed')}",
                    key=f"email_{email['id']}",
                    use_container_width=True
                ):
                    st.session_state.selected_email = email
                    st.rerun()
    
    with col2:
        if st.session_state.selected_email:
            show_email_detail(st.session_state.selected_email)

def show_email_detail(email):
    st.subheader(email['subject'])
    
    # Email metadata
    st.write(f"From: {email['sender']}")
    st.write(f"Date: {email['date']}")
    st.write(f"Category: {email.get('category', 'Not categorized')}")
    
    # Processing actions
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Process Email"):
            with st.spinner("Processing email..."):
                result = call_backend(f"/api/emails/{email['id']}/process", 'POST', {'type': 'all'})
                if result:
                    st.success("Email processed!")
                    load_emails()
    
    with col2:
        if st.button("Extract Actions"):
            with st.spinner("Extracting actions..."):
                result = call_backend(f"/api/emails/{email['id']}/process", 'POST', {'type': 'actions'})
                if result:
                    st.success("Actions extracted!")
                    load_emails()
    
    with col3:
        if st.button("Generate Reply"):
            with st.spinner("Generating draft..."):
                result = call_backend("/api/drafts/generate", 'POST', {'email_id': email['id']})
                if result:
                    st.session_state.generated_draft = result
                    st.success("Draft generated!")
    
    # Email body
    st.markdown("---")
    st.subheader("Email Content")
    st.text_area("Body", email['body'], height=200, key=f"body_{email['id']}")
    
    # Processing results
    if email.get('category'):
        st.markdown("---")
        st.subheader("Processing Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("Summary:")
            st.write(email.get('summary', 'No summary available'))
        
        with col2:
            st.write("Action Items:")
            actions = email.get('actions', {}).get('tasks', [])
            if actions:
                for i, action in enumerate(actions, 1):
                    st.write(f"{i}. {action.get('task', 'Unknown task')}")
                    if action.get('deadline'):
                        st.write(f"   Deadline: {action['deadline']}")
                    if action.get('priority'):
                        st.write(f"   Priority: {action['priority']}")
            else:
                st.write("No action items found")

def show_prompt_config():
    st.header("Prompt Brain Configuration")
    
    if not st.session_state.prompts:
        st.error("No prompts loaded")
        return
    
    for prompt_name, prompt_data in st.session_state.prompts.items():
        with st.expander(f"{prompt_name.replace('_', ' ').title()}"):
            st.write(f"Description: {prompt_data['description']}")
            
            new_content = st.text_area(
                f"Content for {prompt_name}",
                value=prompt_data['content'],
                height=200,
                key=f"prompt_{prompt_name}"
            )
            
            if st.button(f"Update {prompt_name}", key=f"update_{prompt_name}"):
                result = call_backend('/api/prompts', 'POST', {
                    'name': prompt_name,
                    'content': new_content
                })
                if result:
                    st.success(f"{prompt_name} updated successfully!")
                    load_prompts()

def show_email_agent():
    st.header("Email Agent Chat")
    
    # Chat configuration
    col1, col2 = st.columns([2, 1])
    
    with col1:
        email_options = {email['id']: f"{email['subject']} - {email['sender']}" 
                        for email in st.session_state.emails}
        selected_email_id = st.selectbox(
            "Select email to chat about (optional):",
            options=[""] + list(email_options.keys()),
            format_func=lambda x: "General inbox query" if x == "" else email_options[x]
        )
    
    with col2:
        st.write("")
        st.write("")
        if st.button("Clear Chat History"):
            st.session_state.chat_history = []
    
    # Chat interface
    st.markdown("---")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about your emails..."):
        # Add user message to chat
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = call_backend('/api/chat', 'POST', {
                    'email_id': selected_email_id if selected_email_id else None,
                    'query': prompt
                })
                
                if response and 'response' in response:
                    st.write(response['response'])
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": response['response']
                    })
                else:
                    st.error("Failed to get response from agent")

def show_draft_composer():
    st.header("Draft Composer")
    
    # Draft generation options
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Generate from Email")
        email_options = {email['id']: f"{email['subject']} - {email['sender']}" 
                        for email in st.session_state.emails}
        selected_email_id = st.selectbox(
            "Select email to reply to:",
            options=[""] + list(email_options.keys()),
            format_func=lambda x: "New email" if x == "" else email_options[x]
        )
        
        instructions = st.text_area(
            "Additional instructions for draft generation:",
            placeholder="E.g., 'Make it more formal', 'Ask for clarification on timeline', etc."
        )
        
        if st.button("Generate Draft"):
            with st.spinner("Generating draft..."):
                result = call_backend("/api/drafts/generate", 'POST', {
                    'email_id': selected_email_id if selected_email_id else None,
                    'instructions': instructions
                })
                if result:
                    st.session_state.current_draft = result
                    st.success("Draft generated!")
    
    with col2:
        st.subheader("Manual Draft")
        manual_subject = st.text_input("Subject:", key="manual_subject")
        manual_body = st.text_area("Body:", height=300, key="manual_body")
        manual_to = st.text_input("To:", key="manual_to")
        
        if st.button("Save Manual Draft"):
            if manual_subject and manual_body:
                result = call_backend("/api/drafts", 'POST', {
                    'subject': manual_subject,
                    'body': manual_body,
                    'to': manual_to
                })
                if result:
                    st.success("Draft saved successfully!")
            else:
                st.error("Subject and body are required")
    
    # Display generated draft
    if 'current_draft' in st.session_state:
        st.markdown("---")
        st.subheader("Generated Draft")
        
        draft = st.session_state.current_draft
        
        col1, col2 = st.columns(2)
        
        with col1:
            edited_subject = st.text_input("Subject:", value=draft['subject'])
            edited_to = st.text_input("To:", value=draft['to'])
        
        with col2:
            edited_body = st.text_area("Body:", value=draft['body'], height=200)
        
        if st.button("Save Generated Draft"):
            result = call_backend("/api/drafts", 'POST', {
                'subject': edited_subject,
                'body': edited_body,
                'to': edited_to,
                'in_reply_to': draft.get('in_reply_to')
            })
            if result:
                st.success("Draft saved successfully!")
                del st.session_state.current_draft

if __name__ == "__main__":
    main()