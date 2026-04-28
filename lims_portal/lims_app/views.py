from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.cache import cache
from django.conf import settings
from .models import scholarList, commenter, PrivateMessage


def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


def rate_limit(request, key_prefix, max_hits, window_seconds):
    """Returns True (blocked) if the IP has exceeded max_hits in window_seconds."""
    ip = get_client_ip(request)
    cache_key = f'rl:{key_prefix}:{ip}'
    count = cache.get(cache_key, 0)
    if count >= max_hits:
        return True
    cache.set(cache_key, count + 1, timeout=window_seconds)
    return False


def recipient_cooldown(key_prefix, recipient_key, window_seconds):
    """Returns True (blocked) if the recipient is still inside the cooldown window."""
    cache_key = f'cooldown:{key_prefix}:{recipient_key}'
    return not cache.add(cache_key, True, timeout=window_seconds)

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


def scholar_detail(request, pk):
    scholar = get_object_or_404(scholarList, pk=pk)
    return render(
        request,
        "scholar_detail.html",
        context={
            "current_tab": scholar.section.lower(),
            "scholar": scholar,
            "section_url": reverse(scholar.section.lower()),
        },
    )

def get_comments(request):
    scholar_name = request.GET.get('scholar')
    comments = commenter.objects.filter(targetScholar=scholar_name).values('username', 'comment', 'created_at')
    return JsonResponse(list(comments), safe=False)

@csrf_exempt
def add_comment(request):
    if request.method == 'POST':
        if rate_limit(request, 'comment', max_hits=5, window_seconds=60):
            return JsonResponse({'success': False, 'error': 'Too many comments. Please slow down a bit.'}, status=429)
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
            sender_name = request.POST.get('sender_name', '').strip()
            sender_email = request.POST.get('sender_email', '')
            message = request.POST.get('message', '').strip()
            target_scholar = request.POST.get('targetScholar', '').strip()

            if not target_scholar:
                return JsonResponse({'success': False, 'error': 'Missing target scholar.'}, status=400)

            if recipient_cooldown('privmsg', target_scholar.lower().strip(), window_seconds=5):
                return JsonResponse({'success': False, 'error': 'That student was just messaged. Please wait a few seconds before sending again.'}, status=429)

            msg = PrivateMessage(
                sender_name=sender_name,
                sender_email=sender_email,
                message=message,
                targetScholar=target_scholar
            )
            msg.save()

            # Build recipient list: student's email + admin
            recipients = [settings.EMAIL_HOST_USER]
            scholar = scholarList.objects.filter(name=target_scholar).only('email').first()
            if scholar and scholar.email:
                try:
                    validate_email(scholar.email)
                    recipients.insert(0, scholar.email)
                except ValidationError:
                    pass

            # Send email notification
            reply_info = f'Reply to them: {sender_email}' if sender_email else 'No reply email provided'
            email_body = (
                f'Hi {target_scholar},\n\n'
                f'Someone sent you a palanca!\n\n'
                f'From: {sender_name}\n'
                f'{reply_info}\n\n'
                f'Message:\n{message}\n\n'
            )
            send_mail(
                subject=f'To {target_scholar}',
                message=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=False,
            )

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid method'})