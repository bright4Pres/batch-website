from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import scholarList, commenter

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
    comments = commenter.objects.filter(targetScholar=scholar_name).values('username', 'comment')
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