from django.core.mail import send_mail

def send_sms_via_email(phone_number, gateway_domain, message):
    sms_email = f"{phone_number}@{gateway_domain}"
    try:
        send_mail(
            subject="NHS Appointment",
            message=message,
            from_email=None,
            recipient_list=[sms_email],
            fail_silently=False,
        )
        print(f"✅ SMS sent to {sms_email}")
    except Exception as e:
        print(f"❌ Failed to send SMS via email: {e}")