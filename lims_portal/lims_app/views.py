from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from .models import scholarList, commenter, PrivateMessage

def home(request):
    return render(request, "home.html", context={"current_tab": "home"})

def tesla(request):
    tesla_scholar = scholarList.objects.filter(section="Tesla")
    return render(request, "tesla.html", context={"current_tab": "tesla", "scholar": tesla_scholar})

def einstein(request):
    einstein_scholar = scholarList.objects.filter(section="Einstein")
    return render(request, "einstein.html", context={"current_tab": "einstein", "scholar": einstein_scholar})

def curie(request):
    curie_scholar = scholarList.objects.filter(section="Curie")
    return render(request, "curie.html", context={"current_tab": "curie", "scholar": curie_scholar})

def get_comments(request):
    scholar_name = request.GET.get('scholar')
    comments = commenter.objects.filter(targetScholar=scholar_name).values('username', 'comment', 'created_at')
    return JsonResponse(list(comments), safe=False)

@csrf_exempt
def add_comment(request):
    if request.method == 'POST':
        try:
            comment = commenter(
                username=request.POST.get('username'),
                comment=request.POST.get('comment'),
                targetScholar=request.POST.get('targetScholar')
            )
            comment.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid method'})

@csrf_exempt
def send_private_message(request):
    if request.method == 'POST':
        try:
            sender_name = request.POST.get('sender_name')
            sender_email = request.POST.get('sender_email', '')
            message = request.POST.get('message')
            target_scholar = request.POST.get('targetScholar')

            msg = PrivateMessage(
                sender_name=sender_name,
                sender_email=sender_email,
                message=message,
                targetScholar=target_scholar
            )
            msg.save()

            # Send email notification
            reply_info = f'Their email: {sender_email}' if sender_email else 'No email provided'
            email_body = (
                f'You received a private message on Batch 2026!\n\n'
                f'For: {target_scholar}\n'
                f'From: {sender_name}\n'
                f'{reply_info}\n\n'
                f'Message:\n{message}\n\n'
                f'---\nView all messages in the admin panel.'
            )
            send_mail(
                subject=f'[Batch 2026] Private message for {target_scholar}',
                message=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.EMAIL_HOST_USER],
                fail_silently=True,
            )

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid method'})