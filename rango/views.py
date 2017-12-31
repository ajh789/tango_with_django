from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm

def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5];
    context_dict = {'categories': category_list, 'pages': page_list}
    return render(request, 'rango/index.html', context=context_dict)

def about(req):
#   return HttpResponse("Rango says here is the about page.<br/><a href='/rango'>Index</a>")
    print(req.method)
    print(req.user)
    return render(req, 'rango/about.html', {})

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

def add_category(req):
    form = CategoryForm()
    if req.method == 'POST':
        print('See POST request')
        form = CategoryForm(req.POST)
        if form.is_valid():
            print('Form is valid')
            cat = form.save(commit=True)
            print(cat, cat.slug)
            return HttpResponseRedirect('/rango/')
        else:
            print('Form is not valid')
            print('Error: %s' % form.errors)
    print('Render page rango/add_category.html')
    return render(req, 'rango/add_category.html', {'form': form});

def add_page(req, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None
    form = PageForm()
    if req.method == 'POST':
        form = PageForm(req.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return HttpResponseRedirect(reverse('show_category', args=(category_name_slug,)))
        else:
            print(form.errors)
    else:
        pass
    context_dict = {'form': form, 'category': category}
    return render(req, 'rango/add_page.html', context_dict)