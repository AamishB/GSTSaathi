"""
WhatsApp Agent - Generates and sends vendor reminder messages in Indian languages
Updated for smolagents 1.24.0
"""
from typing import List, Dict, Any
from smolagents import Tool


class HindiMessageGenerator(Tool):
    """Generate Hindi messages for vendor GST reminders"""
    name = "hindi_message_generator"
    description = "Generates polite Hindi messages for vendors to file their GST returns"
    inputs = {
        "vendor_name": {"type": "string", "description": "Name of the vendor"},
        "missing_invoices": {"type": "any", "description": "List of missing invoice numbers"},
        "total_amount": {"type": "any", "description": "Total amount of missing invoices"}
    }
    output_type = "any"
    
    def forward(self, vendor_name: str, missing_invoices: list, total_amount: float) -> str:
        """Generate Hindi reminder message"""
        
        invoice_list = ", ".join(missing_invoices[:3])  # Show first 3
        if len(missing_invoices) > 3:
            invoice_list += f" और {len(missing_invoices) - 3} अन्य"
        
        message = f"""नमस्ते {vendor_name},

आपका दिन मंगलमय हो।

हमारे रिकॉर्ड के अनुसार, निम्नलिखित चालान GST पोर्टल पर अपलोड नहीं हुए हैं:
{invoice_list}

कुल राशि: ₹{total_amount:,.2f}

कृपया अपना GSTR-1 जल्द से जल्द फाइल करें ताकि हमें इनपुट टैक्स क्रेडिट मिल सके।

धन्यवाद,
GSTSaathi द्वारा"""
        
        return message


class EnglishMessageGenerator(Tool):
    """Generate English messages for vendor GST reminders"""
    name = "english_message_generator"
    description = "Generates professional English messages for vendor GST reminders"
    inputs = {
        "vendor_name": {"type": "string", "description": "Name of the vendor"},
        "missing_invoices": {"type": "any", "description": "List of missing invoice numbers"},
        "total_amount": {"type": "any", "description": "Total amount of missing invoices"}
    }
    output_type = "any"
    
    def forward(self, vendor_name: str, missing_invoices: list, total_amount: float) -> str:
        """Generate English reminder message"""
        
        invoice_list = ", ".join(missing_invoices[:3])
        if len(missing_invoices) > 3:
            invoice_list += f" and {len(missing_invoices) - 3} others"
        
        message = f"""Dear {vendor_name},

Hope you're doing well.

Our records indicate the following invoices are not uploaded on the GST portal:
{invoice_list}

Total Amount: ₹{total_amount:,.2f}

Kindly file your GSTR-1 at the earliest so we can claim Input Tax Credit.

Thank you,
Team GSTSaathi"""
        
        return message


class MockWhatsAppSender(Tool):
    """Mock WhatsApp sender (for prototype - logs to console)"""
    name = "mock_whatsapp_sender"
    description = "Sends WhatsApp message (mock - prints to console for prototype)"
    inputs = {
        "phone_number": {"type": "string", "description": "Recipient phone number"},
        "message": {"type": "string", "description": "Message content to send"}
    }
    output_type = "any"
    
    def forward(self, phone_number: str, message: str) -> dict:
        """Mock send - in production, this would call WhatsApp Business API"""
        # For prototype, just log
        print(f"\n📱 WhatsApp Message Sent to {phone_number}:")
        print("-" * 50)
        print(message)
        print("-" * 50)
        
        return {
            "success": True,
            "sent_to": phone_number,
            "message_length": len(message)
        }


def generate_vendor_reminders(mismatches: List[Dict], language: str = "hi") -> List[Dict]:
    """
    Generate reminder messages for vendors with missing invoices
    Groups by vendor and creates personalized messages
    """
    try:
        # Group mismatches by vendor
        vendor_groups = {}
        for mismatch in mismatches:
            if mismatch['status'] != 'missing':
                continue
                
            gstin = mismatch['vendor_gstin']
            if gstin not in vendor_groups:
                vendor_groups[gstin] = {
                    "vendor_name": mismatch['vendor_name'],
                    "vendor_gstin": gstin,
                    "invoice_numbers": [],
                    "total_amount": 0
                }
            
            vendor_groups[gstin]['invoice_numbers'].append(mismatch['invoice_number'])
            vendor_groups[gstin]['total_amount'] += mismatch['our_record_amount']
        
        # Generate messages
        reminders = []
        hindi_gen = HindiMessageGenerator()
        english_gen = EnglishMessageGenerator()
        
        for gstin, data in vendor_groups.items():
            if language == "hi":
                message = hindi_gen.forward(
                    data['vendor_name'],
                    data['invoice_numbers'],
                    data['total_amount']
                )
            else:
                message = english_gen.forward(
                    data['vendor_name'],
                    data['invoice_numbers'],
                    data['total_amount']
                )
            
            reminders.append({
                "vendor_name": data['vendor_name'],
                "vendor_gstin": gstin,
                "phone_number": f"+91XXXXXXXXXX",  # Mock phone
                "message": message,
                "missing_count": len(data['invoice_numbers']),
                "total_amount": data['total_amount'],
                "language": language,
                "status": "ready_to_send"
            })
        
        return reminders
    
    except Exception as e:
        return []


def send_mock_whatsapp(reminder: Dict) -> Dict:
    """Send mock WhatsApp message"""
    sender = MockWhatsAppSender()
    result = sender.forward(reminder['phone_number'], reminder['message'])
    return {
        "vendor_gstin": reminder['vendor_gstin'],
        "sent": result['success'],
        "timestamp": "2025-04-15T10:30:00Z"
    }
