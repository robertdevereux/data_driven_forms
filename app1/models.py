from django.db import models

class ScreenQuestion(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('radio', 'Radio'),
        ('picklist', 'Pick List'),
        ('variant-a', 'Variant A'),  # Placeholder for complex screen types
        ('variant-b', 'Variant B'),
    ]
    ANSWER_TYPE_CHOICES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('date', 'Date'),
    ]
    id = models.CharField(max_length=50, primary_key=True)  # Unique identifier (Q1, Q2, V1, etc.)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES)
    guidance = models.TextField(blank=True, null=True)  # Long guidance text before question
    question_text = models.TextField(blank=True, null=True)  # Main question text
    hint = models.CharField(max_length=255, blank=True, null=True)  # Short hint after the question
    answer_type = models.CharField(max_length=20, choices=ANSWER_TYPE_CHOICES, blank=True, null=True)  # Type of expected answer
    options = models.TextField(blank=True, null=True)  # Semi-colon separated values (for radio/picklist)
    parent_screen = models.ForeignKey(
        'self', on_delete=models.CASCADE, blank=True, null=True,
        related_name='sub_questions'
    )  # Links sub-questions to a variant screen

    def __str__(self):
        return self.id

class ScreenRouting(models.Model):
    service_id = models.CharField(max_length=100, null=True)  # Identifies the service this routing belongs to
    current_id = models.CharField(max_length=50)  # The screen/question currently being answered
    answer_value = models.TextField(blank=True, null=True)  # Used only when routing depends on an answer
    next_id = models.CharField(max_length=50)  # The next screen/question to display

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['service_id', 'current_id', 'answer_value'], name='unique_routing_rule')
        ]

    def __str__(self):
        return f"[{self.service_id}] {self.current_id} ({self.answer_value if self.answer_value else 'Any'}) → {self.next_id}"

class Service(models.Model):
    service_id = models.CharField(max_length=100, primary_key=True)  # Unique identifier for the service
    service_name = models.CharField(max_length=255)  # Human-readable service name

    def __str__(self):
        return self.service_name

class Permissions(models.Model):
    user_id=models.CharField(max_length=100, unique=True)  # Unique identifier for the
    regime_id= models.CharField(max_length=100)  # Unique identifier for the service
    service_id= models.CharField(max_length=100)  # Unique identifier for the service

class Regimes(models.Model):
    regime_id = models.CharField(max_length=100, unique=True)  # Unique identifier for the service
    regime_name = models.CharField(max_length=100)  # Unique identifier for the service
    service_id = models.CharField(max_length=100)  # Unique identifier for the service