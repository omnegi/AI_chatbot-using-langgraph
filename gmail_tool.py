import os
import base64
from typing import Optional

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from langchain_core.tools import tool

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly"
]


# -------------------
# connect gmail
# -------------------

def gmail_service():
    """
    Connect to Gmail API.
    Creates token.json after login.
    """

    creds = None

    if os.path.exists("token.json"):

        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )

    if not creds or not creds.valid:

        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json",
            SCOPES
        )

        creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:

            token.write(creds.to_json())

    service = build(
        "gmail",
        "v1",
        credentials=creds
    )

    return service


# -------------------
# draft email
# -------------------

@tool
def gmail_draft(
    to: str,
    purpose: str,
    tone: str = "professional"
):
    """
    Generate email draft preview.

    ALWAYS call before gmail_send.
    """

    from langgraph_backend import llm

    prompt = f"""
Write a {tone} email.

Recipient:
{to}

Purpose:
{purpose}

Return format:

Subject:
Body:
"""

    response = llm.invoke(prompt)

    return {

        "status": "draft",

        "to": to,

        "content": response.content

    }


# -------------------
# send email (only after approval)
# -------------------

@tool
def gmail_send(
    to: str,
    subject: str,
    body: str,
    approved: bool = False
):
    """
    Send email using Gmail API.

    ONLY use after user confirms approval.
    """

    if not approved:

        return "Waiting for approval. Email not sent."

    service = gmail_service()

    message = MIMEMultipart()

    message["to"] = to

    message["subject"] = subject

    message.attach(

        MIMEText(body, "plain")

    )

    raw = base64.urlsafe_b64encode(

        message.as_bytes()

    ).decode()

    service.users().messages().send(

        userId="me",

        body={"raw": raw}

    ).execute()

    return f"Email sent successfully to {to}"


# -------------------
# read emails
# -------------------

@tool
def gmail_read_latest(count: int = 3):
    """
    Show latest emails from inbox.
    """

    service = gmail_service()

    results = service.users().messages().list(

        userId="me",

        maxResults=count

    ).execute()

    messages = results.get("messages", [])

    emails = []

    for msg in messages:

        data = service.users().messages().get(

            userId="me",

            id=msg["id"]

        ).execute()

        headers = data["payload"]["headers"]

        sender = ""

        subject = ""

        for h in headers:

            if h["name"] == "From":

                sender = h["value"]

            if h["name"] == "Subject":

                subject = h["value"]

        emails.append({

            "from": sender,

            "subject": subject

        })

    return emails


# -------------------
# search emails
# -------------------

@tool
def gmail_search(query: str):
    """
    Search email inbox using keyword.
    """

    service = gmail_service()

    results = service.users().messages().list(

        userId="me",

        q=query,

        maxResults=3

    ).execute()

    messages = results.get("messages", [])

    emails = []

    for msg in messages:

        data = service.users().messages().get(

            userId="me",

            id=msg["id"]

        ).execute()

        headers = data["payload"]["headers"]

        sender = ""

        subject = ""

        for h in headers:

            if h["name"] == "From":

                sender = h["value"]

            if h["name"] == "Subject":

                subject = h["value"]

        emails.append({

            "from": sender,

            "subject": subject

        })

    return emails