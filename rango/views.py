# Shoud set TIME_ZONE in settings.py first, default is UTC instead of local timezone
from datetime import datetime

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm
from rango.forms import UserForm, UserProfileForm

def visitor_cookie_handler(req, rsp):
    visits = int(req.COOKIES.get('visits', '1'))
    last_visit_cookie = req.COOKIES.get('last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')
    current_time = datetime.now()
#   print 'Local timezone: %s' % timezone.get_current_timezone()
#   print 'Current time: %s' % current_time
    if (current_time - last_visit_time).seconds > 0:
        visits = visits + 1
        rsp.set_cookie('last_visit', str(current_time))
    else:
        visits = 1
        rsp.set_cookie('last_visit', last_visit_cookie)
    rsp.set_cookie('visits', visits)

def index(req):
    req.session.set_test_cookie()
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5];
    context_dict = {'categories': category_list, 'pages': page_list}
    rsp =  render(req, 'rango/index.html', context=context_dict)
    visitor_cookie_handler(req, rsp)

    return rsp

def about(req):
    if req.session.test_cookie_worked():
        print("TEST COOKIE WORKED!")
        req.session.delete_test_cookie()
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

@login_required
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

@login_required
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

def register(req):
    registered = False
    if req.method == 'POST':
        user_form = UserForm(data=req.POST)
        profile_form = UserProfileForm(data=req.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password) # Hash the password with the set_password method
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            if 'picture' in req.FILES:
                profile.picture = req.FILES['picture']
            profile.save()
            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        # Not a HTTP POST
        user_form = UserForm()
        profile_form = UserProfileForm()
    return render(
        req, 'rango/register.html',
        {'user_form': user_form, 'profile_form': profile_form, 'registered': registered}
    )

def user_login(req):
    if req.method == 'POST':
        username = req.POST.get('username')
        password = req.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(req, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse('Your account is disabled!')
        else:
            print("Invalid login details: {0}, {1}".format(username, password))
#           return HttpResponse('Invalid login details supplied.')
            return render(req, 'rango/invalid_auth.html')
    else:
        return render(req, 'rango/login.html', {})

@login_required
def user_logout(req):
    logout(req)
    return redirect(reverse('index'))
