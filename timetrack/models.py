# models.py

from django.db import models

class TimeTrack(models.Model):
    tmt_id = models.AutoField(primary_key=True)
    tmt_resource = models.CharField(max_length=255)
    tmt_date = models.DateField()
    tmt_hours = models.DecimalField(max_digits=5, decimal_places=2)
    tmt_customers = models.CharField(max_length=255)
    tmt_project = models.CharField(max_length=255)

    class Meta:
        db_table = 'op_time_timetrack'
