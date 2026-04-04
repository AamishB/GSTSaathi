"""
WhatsApp Agent - Generates and sends vendor reminder messages in Indian languages.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Dict, List

from smolagents import Tool


WHATSAPP_LOG_DIR = Path("exports") / "whatsapp_messages"


def _persist_whatsapp_message(phone_number: str, message: str) -> Dict[str, str]:
    """Persist sent WhatsApp messages in UTF-8 files for demos and audit."""
    WHATSAPP_LOG_DIR.mkdir(parents=True, exist_ok=True)

    sent_at = datetime.now(timezone.utc).isoformat()
    message_id = datetime.now().strftime("%Y%m%d%H%M%S%f")

    jsonl_path = WHATSAPP_LOG_DIR / "messages_hi.jsonl"
    text_path = WHATSAPP_LOG_DIR / "messages_hi_readable.txt"

    record = {
        "message_id": message_id,
        "phone_number": phone_number,
        "message": message,
        "sent_at": sent_at,
    }

    with jsonl_path.open("a", encoding="utf-8") as jf:
        jf.write(json.dumps(record, ensure_ascii=False) + "\n")

    with text_path.open("a", encoding="utf-8") as tf:
        tf.write(f"समय: {sent_at}\n")
        tf.write(f"फोन नंबर: {phone_number}\n")
        tf.write("संदेश:\n")
        tf.write(message.strip() + "\n")
        tf.write("-" * 80 + "\n")

    return {
        "message_id": message_id,
        "sent_at": sent_at,
        "jsonl_path": str(jsonl_path),
        "text_path": str(text_path),
    }


class HindiMessageGenerator(Tool):
    """Generate Hindi messages for vendor GST reminders."""

    name = "hindi_message_generator"
    description = "Generates polite Hindi messages for vendors to file their GST returns"
    inputs = {
        "vendor_name": {"type": "string", "description": "Name of the vendor"},
        "missing_invoices": {"type": "any", "description": "List of missing invoice numbers"},
        "total_amount": {"type": "any", "description": "Total amount of missing invoices"},
    }
    output_type = "any"

    def forward(self, vendor_name: str, missing_invoices: list, total_amount: float) -> str:
        invoice_list = ", ".join(missing_invoices[:3])
        if len(missing_invoices) > 3:
            invoice_list += f" और {len(missing_invoices) - 3} अन्य"

        return f"""नमस्ते {vendor_name},

आपका दिन मंगलमय हो।

हमारे रिकॉर्ड के अनुसार, निम्नलिखित चालान GST पोर्टल पर अपलोड नहीं हुए हैं:
{invoice_list}

कुल राशि: ₹{total_amount:,.2f}

कृपया अपना GSTR-1 जल्द से जल्द फाइल करें ताकि हमें इनपुट टैक्स क्रेडिट मिल सके।

धन्यवाद,
GSTSaathi द्वारा"""


class EnglishMessageGenerator(Tool):
    """Generate English messages for vendor GST reminders."""

    name = "english_message_generator"
    description = "Generates professional English messages for vendor GST reminders"
    inputs = {
        "vendor_name": {"type": "string", "description": "Name of the vendor"},
        "missing_invoices": {"type": "any", "description": "List of missing invoice numbers"},
        "total_amount": {"type": "any", "description": "Total amount of missing invoices"},
    }
    output_type = "any"

    def forward(self, vendor_name: str, missing_invoices: list, total_amount: float) -> str:
        invoice_list = ", ".join(missing_invoices[:3])
        if len(missing_invoices) > 3:
            invoice_list += f" and {len(missing_invoices) - 3} others"

        return f"""Dear {vendor_name},

Hope you're doing well.

Our records indicate the following invoices are not uploaded on the GST portal:
{invoice_list}

Total Amount: ₹{total_amount:,.2f}

Kindly file your GSTR-1 at the earliest so we can claim Input Tax Credit.

Thank you,
Team GSTSaathi"""


class MockWhatsAppSender(Tool):
    """Mock WhatsApp sender (for prototype - stores messages in UTF-8 files)."""

    name = "mock_whatsapp_sender"
    description = "Sends WhatsApp message (mock - persists in UTF-8 files for prototype)"
    inputs = {
        "phone_number": {"type": "string", "description": "Recipient phone number"},
        "message": {"type": "string", "description": "Message content to send"},
    }
    output_type = "any"

    def forward(self, phone_number: str, message: str) -> dict:
        log_info = _persist_whatsapp_message(phone_number, message)

        return {
            "success": True,
            "sent_to": phone_number,
            "message_length": len(message),
            "message_id": log_info["message_id"],
            "timestamp": log_info["sent_at"],
            "saved_to": {
                "jsonl": log_info["jsonl_path"],
                "readable_text": log_info["text_path"],
            },
        }


def generate_vendor_reminders(mismatches: List[Dict], language: str = "hi") -> List[Dict]:
    """Generate grouped reminder messages for vendors with missing invoices."""
    vendor_groups = {}
    for mismatch in mismatches:
        if mismatch["status"] != "missing":
            continue

        gstin = mismatch["vendor_gstin"]
        if gstin not in vendor_groups:
            vendor_groups[gstin] = {
                "vendor_name": mismatch["vendor_name"],
                "vendor_gstin": gstin,
                "invoice_numbers": [],
                "total_amount": 0,
            }

        vendor_groups[gstin]["invoice_numbers"].append(mismatch["invoice_number"])
        vendor_groups[gstin]["total_amount"] += mismatch["our_record_amount"]

    reminders = []
    hindi_gen = HindiMessageGenerator()
    english_gen = EnglishMessageGenerator()

    for gstin, data in vendor_groups.items():
        if language == "hi":
            message = hindi_gen.forward(
                data["vendor_name"],
                data["invoice_numbers"],
                data["total_amount"],
            )
        else:
            message = english_gen.forward(
                data["vendor_name"],
                data["invoice_numbers"],
                data["total_amount"],
            )

        reminders.append(
            {
                "vendor_name": data["vendor_name"],
                "vendor_gstin": gstin,
                "phone_number": "+91XXXXXXXXXX",
                "message": message,
                "missing_count": len(data["invoice_numbers"]),
                "total_amount": data["total_amount"],
                "language": language,
                "status": "ready_to_send",
            }
        )

    return reminders


def send_mock_whatsapp(reminder: Dict) -> Dict:
    """Send mock WhatsApp message."""
    sender = MockWhatsAppSender()
    result = sender.forward(reminder["phone_number"], reminder["message"])
    return {
        "vendor_gstin": reminder["vendor_gstin"],
        "sent": result["success"],
        "timestamp": result["timestamp"],
        "message_id": result["message_id"],
        "saved_to": result["saved_to"],
    }


__all__ = [
    "HindiMessageGenerator",
    "EnglishMessageGenerator",
    "MockWhatsAppSender",
    "generate_vendor_reminders",
    "send_mock_whatsapp",
]
