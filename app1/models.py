from django.db import models

### 🔹 Top Level: Regime (e.g., a Tax or Benefit System) ###
class Regime(models.Model):
    regime_id = models.CharField(max_length=100, unique=True)
    regime_name = models.CharField(max_length=255)

    def __str__(self):
        return self.regime_name

### 🔹 Middle Level: Schedule (A grouping of Sections, eg IHT schedule) ###
class Schedule(models.Model):
    schedule_id = models.CharField(max_length=100, unique=True)
    schedule_name = models.CharField(max_length=255)
    regime_id =   models.CharField(max_length=100, default='Regime_1') # A Schedule can belong to multiple Regimes

    def __str__(self):
        return self.schedule_name

### 🔹 Bottom Level: Section (A collection of questions in a logical order eg 'menu' item) ###
class Section(models.Model):
    section_id = models.CharField(max_length=100, unique=True)
    section_name = models.CharField(max_length=255)
    schedule_id = models.CharField(max_length=100, default='Schedule_1')  # A Section can be used in multiple Schedules

    def __str__(self):
        return self.section_name

### 🔹 Master List of Questions (Independent of Sections) ###
class Question(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('radio', 'Radio'),
        ('picklist', 'Pick List'),
        ('variant-a', 'Variant A'),
        ('variant-b', 'Variant B'),
    ]
    ANSWER_TYPE_CHOICES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('date', 'Date'),
    ]

    question_id = models.CharField(max_length=50, primary_key=True)  # Unique identifier (Q1, Q2, etc.)
    question_text = models.TextField(blank=True, null=True)  # Main question text
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES)
    guidance = models.TextField(blank=True, null=True)  # Long guidance text before the question
    hint = models.CharField(max_length=255, blank=True, null=True)  # Short hint after the question
    answer_type = models.CharField(max_length=20, choices=ANSWER_TYPE_CHOICES, blank=True, null=True)  # Expected answer type
    options = models.TextField(blank=True, null=True)  # Semi-colon separated values for radio/picklist
    parent_question = models.ForeignKey(
        'self', on_delete=models.CASCADE, blank=True, null=True, related_name='sub_questions'
    )  # Links sub-questions to a variant screen

    def __str__(self):
        return f"{self.question_id} - {self.question_text}"

### 🔹 Routing (Defines the flow of questions within a Section) ###
class QuestionRouting(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="routings")
    current_question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="current_routes")
    answer_value = models.TextField(blank=True, null=True)  # Optional: Only needed for branching logic
    next_question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="next_routes", null=True, blank=True)
    end_process = models.BooleanField(default=False)  # If True, marks the end of the section

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['section', 'current_question', 'answer_value'], name="unique_routing_rule")
        ]

    def __str__(self):
        return f"Route in {self.section.section_name}: {self.current_question.question_text} → {self.next_question or 'END'}"


### 🔹 Permissions (Controls Access to Regimes, Schedules, or Sections) ###
class Permission(models.Model):
    user_id = models.CharField(max_length=100)  # User identifier (assumed external system handles users)
    regime_id = models.CharField(max_length=100, default='Regime_1')
    schedule_id = models.CharField(max_length=100, default='Schedule_1')
    section_id = models.CharField(max_length=100, default='Section_1')

    class Meta:
        unique_together = ('user_id', 'regime_id', 'schedule_id', 'section_id')  # Ensure no duplicate permissions


