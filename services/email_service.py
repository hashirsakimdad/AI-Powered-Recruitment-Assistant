from threading import Thread

from flask import current_app
from flask_mail import Message

from extensions import mail


def send_status_email_async(app, msg: Message) -> None:
    with app.app_context():
        mail.send(msg)


def notify_candidate(app, submission, new_status: str) -> None:
    """Send email for shortlisted, selected, or rejected statuses only."""
    if new_status not in ("shortlisted", "selected", "rejected"):
        return

    status_messages = {
        "shortlisted": "Congratulations! You've been shortlisted.",
        "selected": "Great news! You've been selected.",
        "rejected": "Thank you for applying. Unfortunately, you were not selected.",
    }
    job_title = submission.job.title if submission.job else "your application"
    msg = Message(
        subject=f"Application Update: {job_title}",
        recipients=[submission.email],
        body=status_messages.get(
            new_status, f"Your status has been updated to: {new_status}"
        ),
    )
    Thread(
        target=send_status_email_async, args=(app._get_current_object(), msg), daemon=True
    ).start()
