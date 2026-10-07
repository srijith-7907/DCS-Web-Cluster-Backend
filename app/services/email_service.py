import smtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import aiosmtplib

from app.config import settings


class EmailService:
    async def send_booking_confirmation(
        self,
        to_email: str,
        attendee_name: str,
        event_name: str,
        event_datetime: str,
        quantity: int,
        total_amount: float,
        booking_id: int,
    ):
        try:
            subject = f"Booking Confirmation - {event_name}"
            body = f"""
Hi {attendee_name},

Your booking has been confirmed!

Booking ID: {booking_id}
Event: {event_name}
Date & Time: {event_datetime}
Quantity: {quantity}
Total Amount: 

Thank you for booking with us!

Best regards,
Event Ticketing Team
"""
            message = MIMEMultipart()
            message["From"] = settings.SMTP_FROM_EMAIL
            message["To"] = to_email
            message["Subject"] = subject
            message.attach(MIMEText(body, "plain"))

            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USERNAME if settings.SMTP_USERNAME else None,
                password=settings.SMTP_PASSWORD if settings.SMTP_PASSWORD else None,
                use_tls=settings.SMTP_USE_TLS,
            )
        except Exception as e:
            # Log error but don't break transaction - best effort
            print(f"Failed to send email: {e}")


email_service = EmailService()
