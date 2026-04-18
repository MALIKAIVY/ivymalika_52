import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .models import Task, TaskStep, TaskMessage, StatusHistory, generate_task_code
from .ai_engine import (
    extract_intent,
    calculate_risk,
    generate_steps,
    generate_messages,
    assign_employee
)

def index(request):
    """Renders the Customer Intake Portal."""
    return render(request, 'index.html')

def dashboard(request):
    """Renders the internal Operations Dashboard."""
    return render(request, 'dashboard.html')

@csrf_exempt
def process_request(request):
    """Processes user input through AI and saves to database."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            customer_name = data.get('customer_name', 'Valued Customer')
            customer_phone = data.get('customer_phone', '')
            customer_email = data.get('customer_email', '')
            
            if not message:
                return JsonResponse({"status": "error", "message": "Message is required"}, status=400)

            # 1. Extract intent and entities
            ai_data = extract_intent(message)
            intent = ai_data.get('intent', 'check_status')
            entities = ai_data.get('entities', {})

            # 2. Risk Evaluation
            risk_data = calculate_risk(intent, entities)
            risk_score = risk_data['score']
            risk_label = risk_data['label']

            # 3. Generate Steps
            steps = generate_steps(intent, entities)

            # 4. Assign Employee/Team
            team = assign_employee(intent)

            # 5. Generate unique task code
            task_code = generate_task_code()

            # 6. Generate Messages
            messages = generate_messages(intent, entities, task_code, risk_label, customer_name)

            # 7. Save to Database (Atomic)
            with transaction.atomic():
                task = Task.objects.create(
                    task_code=task_code,
                    customer_name=customer_name,
                    customer_phone=customer_phone,
                    customer_email=customer_email,
                    intent=intent,
                    entities=entities,
                    risk_score=risk_score,
                    risk_label=risk_label,
                    employee_assignment=team,
                    status='Pending'
                )

                # Create Task Steps
                for i, step_desc in enumerate(steps, 1):
                    TaskStep.objects.create(
                        task=task,
                        step_number=i,
                        description=step_desc
                    )

                # Create Task Messages
                TaskMessage.objects.create(
                    task=task,
                    whatsapp_message=messages.get('whatsapp'),
                    email_message=messages.get('email'),
                    sms_message=messages.get('sms')
                )

            return JsonResponse({
                "status": "success",
                "task_code": task_code,
                "customer_name": customer_name,
                "customer_phone": customer_phone,
                "customer_email": customer_email,
                "intent": intent,
                "entities": entities,
                "risk_score": risk_score,
                "risk_label": risk_label,
                "task_status": task.status,
                "employee_assignment": team,
                "steps": steps,
                "messages": messages,
                "created_at": task.created_at.isoformat()
            })

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
            
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

def get_task_detail(request, task_code):
    """Returns full task details including steps and messages."""
    task = get_object_or_404(Task, task_code=task_code)
    steps = list(task.steps.all().values_list('description', flat=True))
    
    # Get the latest message record
    message_rec = task.messages.order_by('-created_at').first()
    
    return JsonResponse({
        "status": "success",
        "task_code": task.task_code,
        "customer_name": task.customer_name,
        "customer_phone": task.customer_phone,
        "customer_email": task.customer_email,
        "intent": task.intent,
        "entities": task.entities,
        "risk_score": task.risk_score,
        "risk_label": task.risk_label,
        "employee_assignment": task.employee_assignment,
        "task_status": task.status,
        "created_at": task.created_at.isoformat(),
        "steps": steps,
        "messages": {
            "whatsapp": message_rec.whatsapp_message if message_rec else "",
            "email": message_rec.email_message if message_rec else "",
            "sms": message_rec.sms_message if message_rec else ""
        }
    })

def get_tasks(request):
    """Returns all tasks as JSON."""
    tasks = Task.objects.all().order_by('-created_at').values()
    return JsonResponse(list(tasks), safe=False)

@csrf_exempt
def update_status(request, task_code):
    """Updates task status and saves to StatusHistory."""
    if request.method == 'PATCH':
        try:
            task = get_object_or_404(Task, task_code=task_code)
            data = json.loads(request.body)
            new_status = data.get('status')
            
            if new_status:
                old_status = task.status
                task.status = new_status
                task.save()
                
                # Save to history
                StatusHistory.objects.create(
                    task=task,
                    old_status=old_status,
                    new_status=new_status
                )
                
                return JsonResponse({"status": "success", "new_status": new_status})
            return JsonResponse({"status": "error", "message": "Status field is required"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)
