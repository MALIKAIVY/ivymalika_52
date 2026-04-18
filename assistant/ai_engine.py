from google import genai
from google.genai import types
import os
import json
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def extract_intent(user_message):
    system_prompt = """You are an AI assistant for Vunoh Global, a platform that helps Kenyans 
living abroad manage tasks back home. Your job is to analyze a customer 
request and return ONLY a valid JSON object with no extra text, no markdown, 
no backticks.

The JSON must have exactly these fields:
{
  "intent": one of [send_money, hire_service, verify_document, airport_transfer, check_status],
  "entities": {
    "amount": number or null,
    "currency": string or null,
    "recipient": string or null,
    "location": string or null,
    "service_type": string or null,
    "document_type": string or null,
    "urgency": one of [low, medium, high] or null,
    "date": string or null,
    "notes": string or null
  }
}

Rules:
- Return ONLY the JSON. No explanation, no preamble, no backticks.
- If a field is not mentioned, set it to null.
- Urgency is high if the user says urgent, ASAP, emergency, today, immediately.
- Urgency is medium if the user mentions a specific date within 3 days.
- Urgency is low otherwise."""

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                max_output_tokens=1024,
            )
        )
        
        # Parse the JSON and return it
        return json.loads(response.text)
    except Exception as e:
        # On error return default fallback
        return {
            "intent": "check_status",
            "entities": {
                "amount": None,
                "currency": None,
                "recipient": None,
                "location": None,
                "service_type": None,
                "document_type": None,
                "urgency": None,
                "date": None,
                "notes": None
            }
        }

def calculate_risk(intent, entities):
    score = 0
    
    # Base scores by intent
    base_scores = {
        "verify_document": 40,
        "send_money": 30,
        "hire_service": 20,
        "airport_transfer": 15,
        "check_status": 5
    }
    score = base_scores.get(intent, 0)
    
    # Risk factor points
    urgency = entities.get("urgency")
    if urgency == "high":
        score += 25
    elif urgency == "medium":
        score += 10
        
    amount = entities.get("amount")
    if amount is not None:
        if amount > 50000:
            score += 20
        elif 10000 <= amount <= 50000:
            score += 10
            
    if entities.get("recipient") is None:
        score += 15
        
    if entities.get("location") is None:
        score += 10
        
    document_type = entities.get("document_type")
    if document_type and document_type.lower() in ["land title", "title deed"]:
        score += 20
        
    service_type = entities.get("service_type")
    if service_type and service_type.lower() in ["legal", "lawyer"]:
        score += 15
        
    # Cap at 100
    score = min(score, 100)
    
    # Label rules
    if score <= 35:
        label = "Low"
    elif score <= 65:
        label = "Medium"
    else:
        label = "High"
        
    return {"score": score, "label": label}

def generate_steps(intent, entities):
    system_prompt = """You are a task planning assistant for Vunoh Global, a diaspora services 
platform for Kenyans abroad. Given a service intent and extracted details, 
return ONLY a JSON array of steps to fulfil the task. 
No markdown, no explanation, just the raw JSON array.

Generate between 4 and 6 steps depending on complexity.

Examples by intent:
- send_money: ['Verify sender identity', 'Confirm recipient details', 
  'Initiate transfer via M-Pesa or bank', 'Send confirmation to both parties', 
  'Archive transaction record']
- hire_service: ['Receive service request', 'Match with verified local provider', 
  'Confirm scheduling with customer', 'Service delivery', 
  'Customer sign-off and feedback']
- verify_document: ['Receive document details', 'Assign to legal officer', 
  'Cross-check with government registry', 'Generate verification report', 
  'Deliver report to customer']
- airport_transfer: ['Confirm flight details', 'Assign verified driver', 
  'Send driver details to customer', 'Complete pickup', 'Confirm safe arrival']
- check_status: ['Retrieve task record', 'Check current status', 
  'Notify customer']"""

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=f"Intent: {intent}. Entities: {json.dumps(entities)}",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                max_output_tokens=1024,
            )
        )
        # Parse and return the list
        return json.loads(response.text)
    except Exception as e:
        # On error return fallback
        return ["Task received", "Being reviewed by our team", "Customer will be notified"]

def generate_messages(intent, entities, task_code, risk_label, customer_name):
    system_prompt = f"""You are a communications assistant for Vunoh Global, a platform helping 
Kenyans in the diaspora manage tasks back home. Generate three confirmation 
messages for a task. Return ONLY a valid JSON object with exactly these 
three keys: whatsapp, email, sms. No markdown, no backticks, no extra text.

The customer name is: {customer_name}.

Rules for each format:

whatsapp:
- Conversational and warm tone
- Address the customer by name: {customer_name}
- Use line breaks naturally
- 1 or 2 emojis maximum
- Include the task code, what was requested, and next steps
- 3 to 5 lines

email:
- Formal and professional
- Start with 'Dear {customer_name},'
- Include: task code, full details of the request, risk level, 
  next steps, and close with 'Warm regards, Vunoh Global Team'
- 150 to 200 words

sms:
- Maximum 160 characters
- Include task code and one key action only
- Mention the customer name briefly if possible
- No emojis"""

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=f"Task Code: {task_code}. Intent: {intent}. Entities: {json.dumps(entities)}. Risk Level: {risk_label}",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                max_output_tokens=1024,
            )
        )
        return json.loads(response.text)
    except Exception as e:
        return {
          "whatsapp": f"Hi {customer_name}! Your task {task_code} has been received. We will be in touch shortly.",
          "email": f"Dear {customer_name}, Your task {task_code} has been received. Warm regards, Vunoh Global Team",
          "sms": f"Vunoh: Task {task_code} received for {customer_name}. We will contact you shortly."
        }

def assign_employee(intent):
    mapping = {
        "send_money": "Finance",
        "verify_document": "Legal",
        "hire_service": "Operations",
        "airport_transfer": "Operations",
        "check_status": "Support"
    }
    return mapping.get(intent, "Support")
