import os

import requests

import uuid

BASE_URL = "http://127.0.0.1:8080"
EMAIL = f"test_user_{uuid.uuid4().hex[:8]}@example.com" # Dynamic email for fresh session
PASSWORD = "password123"
RESUME_FILE = "Pukar_Kafle_CV.pdf"
JD_FILE = "job_description.txt"

def run():
    # 1. Signup (Handle existing user)
    print(f"--- 1. Authentication ({EMAIL}) ---")
    resp = requests.post(f"{BASE_URL}/api/auth/signup", json={
        "email": EMAIL,
        "password": PASSWORD,
        "first_name": "Test",
        "last_name": "User"
    })
    
    if resp.status_code == 201:
        print("Signup: Created new user.")
    elif resp.status_code == 409: # Conflict
        print("Signup: User already exists. Proceeding to login.")
    else:
        print(f"Signup Failed: {resp.status_code} {resp.text}")
        return

    # 2. Login
    resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": EMAIL,
        "password": PASSWORD
    })
    if resp.status_code != 200:
        print(f"Login Failed: {resp.status_code} {resp.text}")
        return
    
    token = resp.json()["access"]
    print("Login OK. Token obtained.")
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Chat Loop
    print("\n--- 2. Starting Chat Session ---")
    
    # Validation
    if not os.path.exists(RESUME_FILE):
        print(f"Error: {RESUME_FILE} not found.")
        return
    if not os.path.exists(JD_FILE):
        print(f"Error: {JD_FILE} not found.")
        return

    with open(JD_FILE, "r") as f:
        job_description = f.read()

    # Turn 1: Upload Resume
    print("\n[User]: Uploading Resume...")
    files = {'file': open(RESUME_FILE, 'rb')}
    data = {'message': "Here is my resume. Please help me tailor it."}
    
    resp = requests.post(f"{BASE_URL}/api/v1/adk/chat", 
        data=data, 
        files=files,
        headers=headers) # requests handles multipart headers when 'files' is present
    
    print_response(resp)

    # Turn 2: Send Job Description
    print("\n[User]: Sending Job Description...")
    resp = requests.post(f"{BASE_URL}/api/v1/adk/chat", 
                        json={'message': f"Here is the job description:\n{job_description}"}, 
                        headers=headers)
    print_response(resp)

    # Turn 3: Request Generation (Triggers routing check)
    print("\n[User]: Proceed with identifying the gaps and tailoring the resume.")
    resp = requests.post(f"{BASE_URL}/api/v1/adk/chat", 
                        json={'message': "Please identify gaps and then generate the tailored resume."}, 
                        headers=headers)
    print_response(resp)

    # Turn 4: Confirm Tailoring (The Agent might ask for confirmation or just do it. We ensure we say 'Yes' if asked, or just nudge it)
    print("\n[User]: Yes, please tailor the content now.")
    resp = requests.post(f"{BASE_URL}/api/v1/adk/chat", 
                        json={'message': "Yes, please generate the tailored content."}, 
                        headers=headers)
    print_response(resp)

    # Turn 5: Request PDF (Final Step & Loop)
    print("\n[User]: Go ahead and generate the PDF.")
    resp = requests.post(f"{BASE_URL}/api/v1/adk/chat", 
                        json={'message': "The content looks good. Generate the PDF now."}, 
                        headers=headers)
    print_response(resp)
    
    # Loop to handle follow-up agent steps (YAML -> PDF)
    # The ADK might return "transfer_to_agent" which requires a follow-up trigger
    for i in range(5):
        rj = resp.json() if resp.status_code == 200 else {}
        text = rj.get("response", "")
        
        # Check success condition
        if "generated" in text.lower() and "pdf" in text.lower() and "saved" in text.lower():
            print("\n[User]: (Resolution detected) Thank you!")
            break
            
        print(f"\n[User (Auto-Followup {i+1})]: (Pinging to continue agent chain...)")
        # Sending an empty message or "continue" often prompts the next agent to run
        resp = requests.post(f"{BASE_URL}/api/v1/adk/chat", 
                            json={'message': "Proceed."}, 
                            headers=headers)
        print_response(resp)

    
def print_response(resp):
    if resp.status_code == 200:
        rj = resp.json()
        agent_text = rj.get("response", "")
        print(f"[Agent]: {agent_text}")
        state = rj.get("state", {})
        print(f"   [State]: resume_id={state.get('resume_id')} | steps={state.get('current_step')}")
    else:
        print(f"[Error]: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print("Script Error:", e)
