import random
import string
from django.db import models

def generate_task_code():
    """Generates a unique task code like VNH-XXXXXX."""
    return 'VNH-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

class Task(models.Model):
    INTENT_CHOICES = [
        ('send_money', 'Send Money'),
        ('hire_service', 'Hire Service'),
        ('verify_document', 'Verify Document'),
        ('airport_transfer', 'Airport Transfer'),
        ('check_status', 'Check Status'),
    ]

    RISK_LABEL_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    EMPLOYEE_ASSIGNMENT_CHOICES = [
        ('Finance', 'Finance'),
        ('Operations', 'Operations'),
        ('Legal', 'Legal'),
        ('Support', 'Support'),
    ]

    task_code = models.CharField(max_length=10, unique=True, default=generate_task_code, editable=False)
    customer_name = models.CharField(max_length=100, blank=True, null=True)
    customer_phone = models.CharField(max_length=20, blank=True, null=True)
    customer_email = models.EmailField(max_length=100, blank=True, null=True)
    intent = models.CharField(max_length=50, choices=INTENT_CHOICES)
    entities = models.JSONField(default=dict)
    risk_score = models.IntegerField(default=0)
    risk_label = models.CharField(max_length=10, choices=RISK_LABEL_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    employee_assignment = models.CharField(max_length=20, choices=EMPLOYEE_ASSIGNMENT_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.task_code

class TaskStep(models.Model):
    task = models.ForeignKey(Task, related_name='steps', on_delete=models.CASCADE)
    step_number = models.IntegerField()
    description = models.TextField()

    class Meta:
        ordering = ['step_number']

    def __str__(self):
        return f"{self.task.task_code} - Step {self.step_number}"

class TaskMessage(models.Model):
    task = models.ForeignKey(Task, related_name='messages', on_delete=models.CASCADE)
    whatsapp_message = models.TextField(blank=True, null=True)
    email_message = models.TextField(blank=True, null=True)
    sms_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message for {self.task.task_code} at {self.created_at}"

class StatusHistory(models.Model):
    task = models.ForeignKey(Task, related_name='status_history', on_delete=models.CASCADE)
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Status Histories"

    def __str__(self):
        return f"{self.task.task_code}: {self.old_status} -> {self.new_status}"
