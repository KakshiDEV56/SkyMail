from fastapi_mail import FastMail, MessageSchema, MessageType
from app.utils.mail.mail_config import mail_config
from loguru import logger
import random, string
import time

class EmailService:

    @staticmethod
    def generate_otp(length: int = 6) -> str:
        return ''.join(random.choices(string.digits, k=length))

    @staticmethod
    async def send_otp_email(email: str, otp: str, company_name: str = "") -> bool:
        try:
            message = MessageSchema(
                subject="Verify your SkyMail account",
                recipients=[email],
                body=f"""
                <h2>Email Verification</h2>
                <p>Hi {company_name},</p>
                <p>Your OTP is:</p>
                <h1>{otp}</h1>
                <p>This OTP is valid for 10 minutes.</p>
                """,
                subtype=MessageType.html,
            )

            fm = FastMail(mail_config)
            start = time.time()
            await fm.send_message(message)
            elapsed = time.time() - start
            logger.info(f"OTP email sent to {email} (elapsed={elapsed:.2f}s)")
            return True

        except Exception as e:
            logger.error(f"OTP email failed: {e}")
            return False

    @staticmethod
    async def send_verification_email(email: str, company_name: str = "") -> bool:
        try:
            message = MessageSchema(
                subject="Welcome to SkyMail",
                recipients=[email],
                body=f"""
                <h2>Welcome to SkyMail</h2>
                <p>Hi {company_name},</p>
                <p>Your account has been verified successfully. Welcome aboard!</p>
                """,
                subtype=MessageType.html,
            )

            fm = FastMail(mail_config)
            start = time.time()
            await fm.send_message(message)
            elapsed = time.time() - start
            logger.info(f"Verification email sent to {email} (elapsed={elapsed:.2f}s)")
            return True

        except Exception as e:
            logger.error(f"Verification email failed: {e}")
            return False

    @staticmethod
    async def send_password_reset_otp(email: str, otp: str) -> bool:
        try:
            message = MessageSchema(
                subject="Password Reset OTP - SkyMail",
                recipients=[email],
                body=f"""
                <h2>Password Reset Request</h2>
                <p>You requested to reset your SkyMail password.</p>
                <p>Your OTP is:</p>
                <h1>{otp}</h1>
                <p>This OTP is valid for 10 minutes.</p>
                <p>If you didn't request this, please ignore this email.</p>
                """,
                subtype=MessageType.html,
            )

            fm = FastMail(mail_config)
            start = time.time()
            await fm.send_message(message)
            elapsed = time.time() - start
            logger.info(f"Password reset OTP sent to {email} (elapsed={elapsed:.2f}s)")
            return True

        except Exception as e:
            logger.error(f"Password reset email failed: {e}")
            return False

    @staticmethod
    async def send_subscription_welcome_email(
        email: str, 
        company_name: str, 
        website_url: str = None
    ) -> bool:
        """Send welcome email to new newsletter subscriber"""
        try:
            # Create a beautiful HTML email
            website_link = f'<a href="{website_url}" style="color: #4F46E5; text-decoration: none; font-weight: 600;">{website_url}</a>' if website_url else ""
            
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
            </head>
            <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f3f4f6;">
                <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f3f4f6; padding: 40px 20px;">
                    <tr>
                        <td align="center">
                            <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); overflow: hidden;">
                                <!-- Header -->
                                <tr>
                                    <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center;">
                                        <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 700;">
                                            🎉 Welcome to {company_name}!
                                        </h1>
                                    </td>
                                </tr>
                                
                                <!-- Content -->
                                <tr>
                                    <td style="padding: 40px 30px;">
                                        <h2 style="color: #1f2937; margin: 0 0 20px 0; font-size: 22px; font-weight: 600;">
                                            Thank You for Subscribing! 🚀
                                        </h2>
                                        
                                        <p style="color: #4b5563; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                                            We're thrilled to have you join our newsletter community! You've successfully subscribed to receive updates, news, and exclusive content from <strong>{company_name}</strong>.
                                        </p>
                                        
                                        <div style="background-color: #f9fafb; border-left: 4px solid #667eea; padding: 20px; margin: 25px 0; border-radius: 6px;">
                                            <p style="color: #374151; font-size: 15px; line-height: 1.6; margin: 0;">
                                                <strong>What to expect:</strong><br>
                                                ✨ Regular updates and newsletters<br>
                                                📰 Exclusive content and announcements<br>
                                                🎁 Special offers and early access
                                            </p>
                                        </div>
                                        
                                        {f'<p style="color: #4b5563; font-size: 16px; line-height: 1.6; margin: 20px 0;">Visit our website: {website_link}</p>' if website_url else ''}
                                        
                                        <p style="color: #6b7280; font-size: 14px; line-height: 1.6; margin: 30px 0 0 0;">
                                            You can unsubscribe at any time by clicking the unsubscribe link in any of our emails.
                                        </p>
                                    </td>
                                </tr>
                                
                                <!-- Footer -->
                                <tr>
                                    <td style="background-color: #f9fafb; padding: 30px; text-align: center; border-top: 1px solid #e5e7eb;">
                                        <p style="color: #9ca3af; font-size: 13px; margin: 0; line-height: 1.5;">
                                            © {company_name}. All rights reserved.<br>
                                            This email was sent because you subscribed to our newsletter.
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </body>
            </html>
            """

            message = MessageSchema(
                subject=f"Welcome to {company_name} Newsletter! 🎉",
                recipients=[email],
                body=html_body,
                subtype=MessageType.html,
            )

            fm = FastMail(mail_config)
            start = time.time()
            await fm.send_message(message)
            elapsed = time.time() - start
            logger.info(f"Subscription welcome email sent to {email} for {company_name} (elapsed={elapsed:.2f}s)")
            return True

        except Exception as e:
            logger.error(f"Subscription welcome email failed for {email}: {e}")
            return False

    @staticmethod
    async def send_unsubscribe_confirmation_email(
        email: str, 
        company_name: str, 
        website_url: str = None
    ) -> bool:
        """Send confirmation email when user unsubscribes from newsletter"""
        try:
            # Create a beautiful, empathetic HTML email
            website_link = f'<a href="{website_url}" style="color: #4F46E5; text-decoration: none; font-weight: 600;">{website_url}</a>' if website_url else ""
            resubscribe_text = f'<p style="color: #4b5563; font-size: 16px; line-height: 1.6; margin: 20px 0;">If you change your mind, you can always resubscribe at {website_link}</p>' if website_url else ""
            
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
            </head>
            <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f3f4f6;">
                <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f3f4f6; padding: 40px 20px;">
                    <tr>
                        <td align="center">
                            <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); overflow: hidden;">
                                <!-- Header -->
                                <tr>
                                    <td style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); padding: 40px 30px; text-align: center;">
                                        <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 700;">
                                            👋 We're Sorry to See You Go
                                        </h1>
                                    </td>
                                </tr>
                                
                                <!-- Content -->
                                <tr>
                                    <td style="padding: 40px 30px;">
                                        <h2 style="color: #1f2937; margin: 0 0 20px 0; font-size: 22px; font-weight: 600;">
                                            You've Been Unsubscribed
                                        </h2>
                                        
                                        <p style="color: #4b5563; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                                            We're sorry to have let you go! You've successfully unsubscribed from <strong>{company_name}</strong>'s newsletter.
                                        </p>
                                        
                                        <p style="color: #4b5563; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                                            You will no longer receive emails from us. We hope we were able to provide you with valuable content during your time with us.
                                        </p>
                                        
                                        <div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 20px; margin: 25px 0; border-radius: 6px;">
                                            <p style="color: #92400e; font-size: 15px; line-height: 1.6; margin: 0;">
                                                <strong>💡 Was this a mistake?</strong><br>
                                                If you didn't mean to unsubscribe or would like to hear from us again in the future, you're always welcome back!
                                            </p>
                                        </div>
                                        
                                        {resubscribe_text}
                                        
                                        <div style="margin: 30px 0; padding: 20px; background-color: #f9fafb; border-radius: 8px; text-align: center;">
                                            <p style="color: #6b7280; font-size: 15px; line-height: 1.6; margin: 0;">
                                                <strong>Thank you for being part of our community!</strong><br>
                                                We appreciate the time you spent with us and wish you all the best.
                                            </p>
                                        </div>
                                        
                                        <p style="color: #9ca3af; font-size: 14px; line-height: 1.6; margin: 30px 0 0 0; text-align: center;">
                                            If you have any feedback about why you unsubscribed, we'd love to hear from you.
                                        </p>
                                    </td>
                                </tr>
                                
                                <!-- Footer -->
                                <tr>
                                    <td style="background-color: #f9fafb; padding: 30px; text-align: center; border-top: 1px solid #e5e7eb;">
                                        <p style="color: #9ca3af; font-size: 13px; margin: 0; line-height: 1.5;">
                                            © {company_name}. All rights reserved.<br>
                                            This is a confirmation that you've unsubscribed from our newsletter.
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </body>
            </html>
            """

            message = MessageSchema(
                subject=f"You've Unsubscribed from {company_name}",
                recipients=[email],
                body=html_body,
                subtype=MessageType.html,
            )

            fm = FastMail(mail_config)
            start = time.time()
            await fm.send_message(message)
            elapsed = time.time() - start
            logger.info(f"Unsubscribe confirmation email sent to {email} for {company_name} (elapsed={elapsed:.2f}s)")
            return True

        except Exception as e:
            logger.error(f"Unsubscribe confirmation email failed for {email}: {e}")
            return False