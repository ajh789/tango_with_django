from django.shortcuts import render
from django.http import HttpResponse

from rango.models import Category, Page

def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5];
    context_dict = {'categories': category_list, 'pages': page_list}
    return render(request, 'rango/index.html', context=context_dict)

def about(req):
    return HttpResponse("Rango says here is the about page.<br/><a href='/rango'>Index</a>")

def show_category(req, category_name_slug):
    context_dict = {}
    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category)
        context_dict['category'] = category
        context_dict['pages'] = pages
    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None
    return render(req, 'rango/category.html', context_dict)