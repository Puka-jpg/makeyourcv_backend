#!/usr/bin/env python3
"""
Simple Resume Generator using the working /api/v1/adk/chat endpoint
"""

import requests
import time
from pathlib import Path

BASE_URL = "http://localhost:8080"

def gen_resume(resume_pdf: str, jd_txt: str):
    """Generate resume using the API"""
    
    # 1. Create user and login
    email = f"user_{int(time.time())}@example.com"
    password = "test123"
    
    print("1. Creating account...")
    resp = requests.post(f"{BASE_URL}/api/v1/auth/signup", json={
        "email": email,
        "password": password
    })
    if resp.status_code != 200:
        print(f"Signup failed: {resp.text}")
        return
    
    print("2. Logging in...")
    resp = requests.post(f"{BASE_URL}/api/v1/auth/login", json={
        "email": email,
        "password": password
    })
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Upload resume
    print("3. Uploading resume...")
    with open(resume_pdf, "rb") as f:
        files = {"file": f}
        data = {"message": "Here is my resume"}
        resp = requests.post(f"{BASE_URL}/api/v1/adk/chat", data=data, files=files, headers=headers)
    
    if resp.status_code != 200:
        print(f"Upload failed: {resp.text}")
        return
    print(f"   → {resp.json().get('response', 'OK')}")
    
   # 3. Send job description
    print("4. Sending job description...")
    with open(jd_txt, "r") as f:
        jd_text = f.read()
    
    data = {"message": f"Here's the job description:\n\n{jd_text}"}
    resp = requests.post(f"{BASE_URL}/api/v1/adk/chat", data=data, headers=headers)
    
    if resp.status_code != 200:
        print(f"JD send failed: {resp.text}")
        return
    print(f"   → {resp.json().get('response', 'OK')}")
    
    # 4. Request tailoring
    print("5. Requesting resume tailoring...")
    data = {"message": "Please analyze the gaps and tailor my resume for this job"}
    resp = requests.post(f"{BASE_URL}/api/v1/adk/chat", data=data, headers=headers)
    
    if resp.status_code != 200:
        print(f"Tailor request failed: {resp.text}")
        return
    print(f"   → {resp.json().get('response', 'OK')}")
    
    # 5. Confirm and generate
    print("6. Generating tailored resume...")
    data = {"message": "Yes, please generate the tailored resume"}
    resp = requests.post(f"{BASE_URL}/api/v1/adk/chat", data=data, headers=headers)
    
    if resp.status_code != 200:
        print(f"Generate failed: {resp.text}")
        return
        
    response_text = resp.json().get('response', '')
    print(f"   → {response_text}")
    
    # Check for download URL
    if "/generated_resumes/" in response_text or "resume" in response_text.lower():
        print(f"\n✅ SUCCESS! Check the response above for the download link")
        print(f"   Or check: generated_resumes/ folder")
    else:
        print(f"\n⚠️  Response received but no PDF link found")
        print(f"   You may need to send another message to continue")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python simple_resume_gen.py <resume.pdf> <job_description.txt>")
        print("\nExample:")
        print("  python simple_resume_gen.py my_resume.pdf target_job.txt")
        sys.exit(1)
    
    resume_file = sys.argv[1]
    jd_file = sys.argv[2]
    
    if not Path(resume_file).exists():
        print(f"❌ Resume file not found: {resume_file}")
        sys.exit(1)
    
    if not Path(jd_file).exists():
        print(f"❌ Job description file not found: {jd_file}")
        sys.exit(1)
    
    gen_resume(resume_file, jd_file)
