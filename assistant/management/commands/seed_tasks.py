import random
import string
from django.core.management.base import BaseCommand
from django.db import transaction
from assistant.models import Task, TaskStep, TaskMessage, generate_task_code
from assistant.ai_engine import calculate_risk, assign_employee

class Command(BaseCommand):
    help = 'Seeds 5 realistic sample tasks into the database'

    def handle(self, *args, **options):
        scenarios = [
            {
                "intent": "send_money",
                "entities": {"amount": 25000, "currency": "KES", "recipient": "John Kamau", "location": "Nairobi", "urgency": "high"},
                "status": "In Progress",
                "steps": [
                    "Verify John Kamau's M-Pesa account status",
                    "Confirm KES 25,000 funds availability in primary account",
                    "Execute secure international transfer via authorized channel",
                    "Initiate M-Pesa disbursement to recipient in Nairobi",
                    "Send digital transaction receipt to customer"
                ],
                "messages": {
                    "whatsapp": "Hello! We have initiated your urgent transfer of KES 25,000 to John Kamau. Next steps: verifying receipt.",
                    "email": "Dear Valued Customer, Your task VNH-XXXXXX (Send Money) has been received. Risk level: Medium. We are currently processing the disbursement. Warm regards, Vunoh Global Team",
                    "sms": "Vunoh: Task VNH-XXXXXX started. KES 25k being sent to John Kamau."
                }
            },
            {
                "intent": "verify_document",
                "entities": {"document_type": "land title", "location": "Karen, Nairobi", "urgency": "medium"},
                "status": "Pending",
                "steps": [
                    "Collect parcel number and title deed copy from customer",
                    "Assign request to registered land surveyor in Nairobi",
                    "Conduct official search at Ministry of Lands (Ardhi House)",
                    "Verify boundaries and ownership history in Karen registry",
                    "Generate comprehensive verification report"
                ],
                "messages": {
                    "whatsapp": "Hi! We've assigned an officer to verify your land title in Karen. We'll update you after the Ardhi House search.",
                    "email": "Dear Valued Customer, Your task VNH-XXXXXX (Verify Document) has been received. Risk level: High. A legal officer has been assigned. Warm regards, Vunoh Global Team",
                    "sms": "Vunoh: Document verification for Karen plot started. Ref: VNH-XXXXXX."
                }
            },
            {
                "intent": "hire_service",
                "entities": {"service_type": "cleaner", "location": "Westlands", "date": "this Friday", "urgency": "low"},
                "status": "Pending",
                "steps": [
                    "Filter verified cleaning providers in Westlands area",
                    "Confirm availability for the requested Friday slot",
                    "Provide service quote and equipment requirements to customer",
                    "Schedule professional cleaner and confirm access details",
                    "Follow up for service quality feedback"
                ],
                "messages": {
                    "whatsapp": "Jambo! We are matching you with a cleaner in Westlands for Friday. Access details confirmed?",
                    "email": "Dear Valued Customer, Your task VNH-XXXXXX (Hire Service) has been received. Risk level: Low. Matching with providers now. Warm regards, Vunoh Global Team",
                    "sms": "Vunoh: Hiring cleaner for Westlands. Task VNH-XXXXXX in progress."
                }
            },
            {
                "intent": "airport_transfer",
                "entities": {"location": "JKIA", "date": "Saturday 6am", "urgency": "medium"},
                "status": "Completed",
                "steps": [
                    "Confirm arrival flight number and estimated time",
                    "Assign a verified driver with large vehicle for luggage",
                    "Share driver identity and plate number with customer",
                    "Monitor flight status for early arrival or delays",
                    "Pickup completed at JKIA arrivals terminal"
                ],
                "messages": {
                    "whatsapp": "Safe flight! Your driver Moses (KDL 123X) will meet you at JKIA Saturday 6am. He's at the arrivals gate.",
                    "email": "Dear Valued Customer, Your task VNH-XXXXXX (Airport Transfer) is COMPLETED. Your driver arrived on time. Warm regards, Vunoh Global Team",
                    "sms": "Vunoh: Airport pickup at JKIA finished. Welcome to Nairobi!"
                }
            },
            {
                "intent": "check_status",
                "entities": {"notes": "Previous medical bill task", "urgency": "low"},
                "status": "In Progress",
                "steps": [
                    "Retrieve database record for previous medical task",
                    "Contact processing agent for latest status update",
                    "Generate status summary for the diaspora customer",
                    "Update customer via WhatsApp and dashboard"
                ],
                "messages": {
                    "whatsapp": "Hi, just checked your medical bill task. It's currently being reviewed by the local clinic.",
                    "email": "Dear Valued Customer, Your task VNH-XXXXXX (Check Status) is in progress. We are fetching your records. Warm regards, Vunoh Global Team",
                    "sms": "Vunoh: Checking status of your previous task VNH-XXXXXX."
                }
            }
        ]

        with transaction.atomic():
            for s in scenarios:
                t_code = generate_task_code()
                intent = s["intent"]
                entities = s["entities"]
                
                # Use project logic for risk and assignment
                risk = calculate_risk(intent, entities)
                team = assign_employee(intent)

                task = Task.objects.create(
                    task_code=t_code,
                    intent=intent,
                    entities=entities,
                    risk_score=risk["score"],
                    risk_label=risk["label"],
                    status=s["status"],
                    employee_assignment=team
                )

                # Create Steps
                for i, step_desc in enumerate(s["steps"], 1):
                    TaskStep.objects.create(
                        task=task,
                        step_number=i,
                        description=step_desc
                    )

                # Create Message (update task_code placeholders in strings if any)
                msg_data = s["messages"]
                TaskMessage.objects.create(
                    task=task,
                    whatsapp_message=msg_data["whatsapp"].replace("VNH-XXXXXX", t_code),
                    email_message=msg_data["email"].replace("VNH-XXXXXX", t_code),
                    sms_message=msg_data["sms"].replace("VNH-XXXXXX", t_code)
                )

                self.stdout.write(self.style.SUCCESS(f'Successfully created task {t_code} ({intent})'))

        self.stdout.write(self.style.SUCCESS(f'Seed complete: 5 tasks added to the database.'))
