# app/services/email_service.py

import os
from sib_api_v3_sdk import ApiClient, Configuration, TransactionalEmailsApi
from sib_api_v3_sdk.models import SendSmtpEmail

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
SENDER_EMAIL = os.getenv("BREVO_SENDER_EMAIL")
SENDER_NAME = os.getenv("BREVO_SENDER_NAME")

def send_otp_email(to_email: str, otp: str):
    configuration = Configuration()
    configuration.api_key["api-key"] = BREVO_API_KEY

    api_client = ApiClient(configuration)
    api_instance = TransactionalEmailsApi(api_client)

    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background:#f6f6f6; padding:20px;">
        <div style="max-width:600px; margin:auto; background:#ffffff; padding:20px; border-radius:6px;">
          <h2 style="color:#2c3e50;">Community Registration</h2>
          <p>Hello,</p>
          <p>Your One-Time Password (OTP) is:</p>
          <h1 style="letter-spacing:4px; color:#27ae60;">{otp}</h1>
          <p>This OTP is valid for <b>5 minutes</b>.</p>
          <p style="color:#e74c3c;">Do not share this OTP with anyone.</p>
          <br>
          <p>Regards,<br><b>Community Admin</b></p>
        </div>
      </body>
    </html>
    """

    email = SendSmtpEmail(
        to=[{"email": to_email}],
        sender={"email": SENDER_EMAIL, "name": SENDER_NAME},
        subject="Your OTP for Community Registration",
        html_content=html_content
    )

    api_instance.send_transac_email(email)



def send_approval_email(
    to_email: str,
    desired_name: str,
    membership_id: str
):
    if not to_email:
        return  # safety: skip if email not available

    configuration = Configuration()
    configuration.api_key["api-key"] = BREVO_API_KEY

    api_client = ApiClient(configuration)
    api_instance = TransactionalEmailsApi(api_client)

    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background:#f6f6f6; padding:20px;">
        <div style="max-width:600px; margin:auto; background:#ffffff; padding:20px; border-radius:6px;">
          
          <h2 style="color:#2c3e50;">🎉 Membership Approved</h2>

          <p>Dear <b>{desired_name}</b>,</p>

          <p>
            Congratulations! Your registration has been <b>successfully approved</b>.
          </p>

          <p><b>Your Membership Details:</b></p>
          <ul>
            <li><b>Membership ID:</b> {membership_id}</li>
            <li><b>Name:</b> {desired_name}</li>
          </ul>

          <p>
            You are now an official member of our community.
          </p>

          <hr>

          <p>
            📞 Support: +91-XXXXXXXXXX<br>
            📧 Email: support@community.org
          </p>

          <p>
            Warm regards,<br>
            <b>Community Admin Team</b>
          </p>

        </div>
      </body>
    </html>
    """

    email = SendSmtpEmail(
        to=[{"email": to_email}],
        sender={"email": SENDER_EMAIL, "name": SENDER_NAME},
        subject="🎉 Membership Approved – Welcome!",
        html_content=html_content
    )

    api_instance.send_transac_email(email)





def send_rejection_email(
    to_email: str,
    full_name: str,
    desired_name: str | None,
    reason: str
):
    configuration = Configuration()
    configuration.api_key["api-key"] = BREVO_API_KEY

    api_client = ApiClient(configuration)
    api_instance = TransactionalEmailsApi(api_client)

    display_name = desired_name or full_name

    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background:#f6f6f6; padding:20px;">
        <div style="max-width:600px; margin:auto; background:#ffffff; padding:20px; border-radius:6px;">
          
          <h2 style="color:#c0392b;">Community Registration Update</h2>

          <p>Dear <b>{display_name}</b>,</p>

          <p>
            Thank you for submitting your registration request to our community.
            After careful review, we regret to inform you that your application
            could not be approved at this time.
          </p>

          <p><b>Reason:</b></p>
          <blockquote style="background:#f9f9f9; padding:10px; border-left:4px solid #e74c3c;">
            {reason}
          </blockquote>

          <p>
            If you believe this decision was made in error, or if you wish to
            reapply after making the necessary corrections, please feel free
            to contact our support team.
          </p>

          <p>
            📧 Support Email: <b>support@community.org</b><br>
            📞 Contact: <b>+91-XXXXXXXXXX</b>
          </p>

          <br>
          <p>Regards,<br><b>Community Administration Team</b></p>

        </div>
      </body>
    </html>
    """

    email = SendSmtpEmail(
        to=[{"email": to_email}],
        sender={"email": SENDER_EMAIL, "name": SENDER_NAME},
        subject="Update on Your Community Registration",
        html_content=html_content
    )

    api_instance.send_transac_email(email)
