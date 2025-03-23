from django import forms
from .models import User, Regime, Schedule,Section, Permission


class RegimeForm(forms.ModelForm):
    class Meta:
        model = Regime
        fields = ["regime_id", "regime_name"]  # Adjust based on your model

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ["regime", "schedule_id", "schedule_name"]  # Adjust based on your model

class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ["schedule", "section_id", "section_name", "section_type"]  # Adjust based on your model

