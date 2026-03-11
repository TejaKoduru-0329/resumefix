from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from payments.models import UserPlan
import json

def get_or_create_plan(user):
    plan, _ = UserPlan.objects.get_or_create(user=user)
    return plan

@login_required(login_url='login')
def payment_page(request):
    plan = get_or_create_plan(request.user)
    free_range = range(plan.FREE_LIMIT)
    paid_remaining = plan.total_paid_resumes - plan.paid_resumes_used
    paid_range = range(max(0, paid_remaining))

    return render(request, 'payments/checkout.html', {
        'plan': plan,
        'free_range': free_range,
        'paid_range': paid_range,
    })

@login_required(login_url='login')
def add_credits(request):
    if request.method == "POST":
        data = json.loads(request.body)
        quantity = int(data.get("quantity", 1))
        plan = get_or_create_plan(request.user)
        plan.total_paid_resumes += quantity
        plan.save()
        return JsonResponse({
            "success": True,
            "credits": plan.resumes_remaining()
        })
    return JsonResponse({"success": False})