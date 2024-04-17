from django.db import models
from django.utils.translation import gettext_lazy as _


class FAQ(models.Model):
    specialist = models.ForeignKey(
        'User', on_delete=models.CASCADE, db_column='specialist'
    )
    department = models.ForeignKey(
        'Department', on_delete=models.CASCADE, db_column='department'
    )
    subsection = models.ForeignKey(
        'Subsection', on_delete=models.CASCADE, db_column='subsection'
    )
    question = models.CharField(max_length=250, blank=False)
    answer = models.CharField(max_length=750, blank=False)

    class Meta:
        ordering = ['department', 'subsection', 'specialist']
