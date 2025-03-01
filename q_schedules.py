from app1.models import Schedule, Regime

Schedule.objects.all().delete()
print("✅ All existing schedule data deleted!")

# Schedule data
schedules = [
    {"schedule_id": "Schedule_1", "schedule_name": "Jewelry", "regime_ids": ["Regime_1"]},
    {"schedule_id": "Schedule_2", "schedule_name": "Schedule for land and building", "regime_ids": ["Regime_1"]},
    {"schedule_id": "Schedule_1", "schedule_name": "Personal Details", "regime_ids": ["Regime_2"]},
    {"schedule_id": "Schedule_3", "schedule_name": "Other Details", "regime_ids": ["Regime_2"]},
    {"schedule_id": "Schedule_2", "schedule_name": "Driving licence details", "regime_ids": ["Regime_3"]}
]

# Insert into the database
for sched in schedules:
    schedule, created = Schedule.objects.update_or_create(
        schedule_id=sched["schedule_id"],
        defaults={"schedule_name": sched["schedule_name"]}
    )
    # Link the schedule to regimes
    for regime_id in sched["regime_ids"]:
        regime = Regime.objects.filter(regime_id=regime_id).first()
        if regime:
            schedule.regimes.add(regime)

print("✅ New Schedule data added successfully!")
