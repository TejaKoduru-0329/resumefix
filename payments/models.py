from django.db import models

from django.db import models
from django.contrib.auth.models import User


class UserPlan(models.Model):
    """Tracks free resume usage and payment status per user."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='plan')
    free_resumes_used = models.PositiveIntegerField(default=0)
    total_paid_resumes = models.PositiveIntegerField(default=0)  # total credits bought
    paid_resumes_used = models.PositiveIntegerField(default=0)

    FREE_LIMIT = 2
    PRICE_PER_RESUME = 49  # ₹49

    def resumes_remaining(self):
        free_left = max(0, self.FREE_LIMIT - self.free_resumes_used)
        paid_left = max(0, self.total_paid_resumes - self.paid_resumes_used)
        return free_left + paid_left

    def can_generate(self):
        return self.resumes_remaining() > 0

    def use_resume(self):
        """Call this when a resume is successfully generated."""
        if self.free_resumes_used < self.FREE_LIMIT:
            self.free_resumes_used += 1
        elif self.paid_resumes_used < self.total_paid_resumes:
            self.paid_resumes_used += 1
        else:
            raise ValueError("No resumes remaining. Please purchase more.")
        self.save()

    def __str__(self):
        return f"{self.user.username} | Free used: {self.free_resumes_used}/{self.FREE_LIMIT} | Paid: {self.total_paid_resumes - self.paid_resumes_used} left"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('created', 'Created'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    razorpay_order_id = models.CharField(max_length=100, unique=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)

    amount = models.PositiveIntegerField()          # in paise (₹49 = 4900)
    resumes_purchased = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def amount_in_rupees(self):
        return self.amount // 100

    def __str__(self):
        return f"{self.user.username} | ₹{self.amount_in_rupees()} | {self.status}"
