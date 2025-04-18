from django.db import models
import json

### 🔹 Top Level: Regime (e.g., a Tax or Benefit System) ###
class Regime(models.Model):
    regime_id = models.CharField(max_length=100, primary_key=True)
    regime_name = models.CharField(max_length=255)

    def __str__(self):
        return self.regime_name

### 🔹 Middle Level: Schedule (A grouping of Sections, eg IHT schedule) ###
class Schedule(models.Model):
    schedule_id = models.CharField(max_length=100, primary_key=True)
    schedule_name = models.CharField(max_length=255)

    # Link to Regime
    regime = models.ForeignKey(
        Regime,
        to_field="regime_id",
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.schedule_name

### 🔹 Bottom Level: Section (may belong to a Schedule or directly to a Regime) ###
class Section(models.Model):
    SECTION_MODE_CHOICES = [
        ("single", "One question per page"),
        ("multi", "All questions on one page"),
        ("flexible", "Flexible layout"),
        ("custom", "Custom section with bespoke view"),
    ]

    section_id = models.CharField(max_length=100, primary_key=True)
    section_name = models.CharField(max_length=255)
    section_type = models.IntegerField(default=0)
    section_records = models.IntegerField(default=0)

    section_mode = models.CharField(
        max_length=10,
        choices=SECTION_MODE_CHOICES,
        default="flexible",
        help_text="Controls how this section is rendered"
    )

    custom_view_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Django view name to use if section_mode is 'custom'"
    )

    schedule = models.ForeignKey(
        Schedule,
        to_field="schedule_id",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    regime = models.ForeignKey(
        'Regime',
        to_field="regime_id",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.section_name

    def get_regime(self):
        if self.schedule:
            return self.schedule.regime
        return self.regime

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
class Routing(models.Model):
    section_id = models.CharField(max_length=100, default="section_1")
    current_question = models.CharField(max_length=50)
    answer_value = models.TextField(blank=True, null=True)  # Optional: branching logic
    next_question = models.CharField(max_length=50, default="Q1")
    order_in_section = models.PositiveIntegerField(default=0)
    totalled = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['section_id', 'current_question', 'answer_value'],
                name="unique_routing_rule"
            )
        ]
        ordering = ['section_id', 'order_in_section']  # Default sort order


### 🔹 Permissions (Controls Access to Sections, which in turn define access to Schedule/Regime) ###
class Permission(models.Model):
    user_id = models.CharField(max_length=100)  # External user system assumed
    section = models.ForeignKey(
        Section,
        to_field="section_id",
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('user_id', 'section')  # Prevent duplicates

    def __str__(self):
        return f"{self.user_id} can access {self.section.section_name}"

class AnswerBasic(models.Model):
    user_id = models.CharField(max_length=100)
    regime_id = models.CharField(max_length=100)
    question_id = models.CharField(max_length=100)
    answer = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the answer is created

    class Meta:
        unique_together = ("user_id", "regime_id", "question_id")  # Ensures only 1 record per (user, regime, question)

    def set_answer(self, value):
        """Handles conversion of lists to JSON for checkbox answers."""
        if isinstance(value, list):  # Convert list to JSON string
            self.answer = json.dumps(value)
        else:  # Store text as-is
            self.answer = value

    def get_answer(self):
        """Handles conversion of JSON string back to Python list if necessary."""
        try:
            return json.loads(self.answer)  # Convert back to list if it's JSON
        except json.JSONDecodeError:
            return self.answer  # Return as-is if it's plain text

class AnswerTable(models.Model):
    user_id = models.CharField(max_length=100)
    regime_id = models.CharField(max_length=100)
    question_id = models.CharField(max_length=100)  # Reference to the table (usually section_id)
    answer = models.JSONField(default=list)  # ✅ Stores multiple rows of answers; default = empty list
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user_id", "regime_id", "question_id")  # One table per user/regime/section

    def __str__(self):
        return f"User {self.user_id} - Table {self.question_id}"


class SectionStatus(models.Model):
    STATUS_CHOICES = [
        ("not_started", "Not Started"),
        ("in_progress", "In Progress"),
        ("complete", "Complete"),
    ]

    user_id = models.CharField(max_length=100)
    regime_id = models.CharField(max_length=100)
    section_id = models.CharField(max_length=100)  # One status per section
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="not_started")  # Overall section status

    def __str__(self):
        return f"User {self.user_id} - Section {self.section_id} ({self.status})"

class User(models.Model):
    user_id = models.CharField(max_length=100, unique=True)  # User identifier (assumed external system handles users)
    user_name = models.CharField(max_length=255, default="AN Other")

    def __str__(self):
        return self.user_id

class ScheduleStatus(models.Model):
    STATUS_CHOICES = [
        ("not_started", "Not Started"),
        ("in_progress", "In Progress"),
        ("complete", "Complete"),
    ]

    user_id = models.CharField(max_length=100)
    regime_id = models.CharField(max_length=100)
    schedule_id = models.CharField(max_length=100)  # One status per schedule
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="not_started")  # Overall schedule status

    def __str__(self):
        return f"User {self.user_id} - Schedule {self.schedule_id} ({self.status})"
