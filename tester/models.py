from django.db import models

class DBTest(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-incrementing ID field
    colour = models.CharField(max_length=50)  # Colour field with max 50 characters

    class Meta:
        db_table = 'basic5_dbtest'  # Explicitly set the table name in the DB

    def __str__(self):
        return f"{self.id} - {self.colour}"

