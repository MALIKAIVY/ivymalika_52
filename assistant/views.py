import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Task, StatusHistory

def index(request):
    """Serves the frontend HTML page."""
    return render(request, 'index.html')

@csrf_exempt
def process_request(request):
    """Processes user input through AI (stub for now)."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            
            # Placeholder for AI logic
            task_details = {
                "task_code": "VNH-STUB01",
                "intent": "check_status",
                "status": "Pending",
                "received_message": message
            }
            return JsonResponse({"status": "success", "task": task_details})
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

def get_tasks(request):
    """Returns all tasks as JSON."""
    tasks = Task.objects.all().values()
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
