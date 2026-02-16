from django.db import models
from django.contrib.auth.models import User

class ResumeAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resume_file = models.FileField(upload_to='resumes/')
    job_description = models.TextField()

    before_text = models.TextField(blank=True)
    after_text = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

