from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login
from django.urls import reverse
from bs4 import BeautifulSoup
import requests
from django.contrib import messages
import time
from FinalScraper import settings
from decimal import Decimal
import random
from django.contrib.auth.models import User
from .models import SavedProducts
from .models import TrendSearch
import json
from django.db.models import Count


def account(request):  # sign up
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        try:
            match = User.objects.get(email=email)
            messages.error(request, f"{email} already exists")
        except:
            if password1 == password2:
                user = User.objects.create_user(username, email, password1)
                user.save()
                messages.info(request, f"{username} created")
                user = authenticate(request, username=username, password=password1)
                login(request, user)
                return redirect('search-page')
            else:
                messages.error(request, f"Passwords do not match")
                return redirect('account')

    return render(request, 'account.html')


def loginpage(request):  # login
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('search-page'))
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.info(request, f"You are now logged in as {username}")
            return HttpResponseRedirect(reverse('search-page'))
        else:
            messages.error(request, "Invalid username or password")
            return render(request, "account.html",)
    return render(request, "account.html")


# search page
def button(request):
    return render(request, 'searchpage.html')


# delete saved products
def delete(request, id):
    savedproducts = SavedProducts.objects.get(id=id)
    savedproducts.delete()
    return redirect('saved_products')


# working
def searchresult(request):
    if request.user.is_authenticated:
        search = request.GET.get('productsearch')
        stores = request.GET.getlist('stores[]')
        print(stores)
        if len(stores) == 0 or len(search) == 0:
            messages.error(request, "Please pick a store and input a product")
            return redirect('search-page')
        else:
            trendsearch = TrendSearch()
            trendsearch.search = search
            trendsearch.stores = stores
            trendsearch.save()
            presentpage = ''
            if 'jumia' in stores:
                if 'ebay' and 'aliexpress' and 'jiji' and 'amazon' not in stores:
                    urls = [f"https://www.jumia.com.ng/catalog/?q={search}"]
                    presentpage = f'search/?productsearch={search}&stores%5B%5D=jumia'
            if 'ebay' in stores:
                if 'jumia' and 'aliexpress' and 'jiji' and 'amazon' not in stores:
                    urls = [f"https://www.ebay.com/sch/i.html?_from=R40&_trksid=m570.l1313&_nkw={search}&_sacat=0"]
                    presentpage = f'search/?productsearch={search}&stores%5B%5D=ebay'
            if 'ebay' in stores:
                if 'jumia' in stores:
                    if 'aliexpress' and 'jiji' and 'amazon' not in stores:
                        presentpage = f'search/?productsearch={search}&stores%5B%5D=jumia&stores%5B%5D=ebay'
                        urls = [f"https://www.ebay.com/sch/i.html?_from=R40&_trksid=m570.l1313&_nkw={search}&_sacat=0",
                                f"https://www.jumia.com.ng/catalog/?q={search}"]


        products = []
        starttime = time.time()

        for url in urls:
            res = requests.get(url)
            data = res.text
            products = products + scraper(data)

        numb = len(products)
        print(numb)
        prod = listofproducts(products)
        prod = random.sample(prod, len(prod))
        print(products)

        # trending products
        trending = SavedProducts.objects.values('link', 'store', 'name', 'image', 'price').annotate(dcount=Count('link')).order_by('-dcount')[:5]
        trendsearches = TrendSearch.objects.values('stores', 'search').annotate(dcount=Count('search')).order_by('-dcount')[:5]
        trendquery = []
        for each in trendsearches:
            searchquery = each['search']
            searchplus = searchquery.replace(' ', '+')
            searchstores = each['stores']
            eachstore = ''
            for eachstores in searchstores:
                eachstore += eachstores + ','
            eachstore = eachstore[:-1]
            eachlink = ''
            print(searchquery, searchstores)
            if 'jumia' in searchstores:
                if 'ebay' and 'aliexpress' and 'jiji' and 'amazon' not in searchstores:
                    eachlink = settings.BASE_URL + f'search/?productsearch={searchplus}&stores%5B%5D=jumia'
            if 'ebay' in searchstores:
                if 'jumia' and 'aliexpress' and 'jiji' and 'amazon' not in searchstores:
                    eachlink = settings.BASE_URL + f'search/?productsearch={searchplus}&stores%5B%5D=ebay'
            if 'ebay' in searchstores:
                if 'jumia' in searchstores:
                    if 'aliexpress' and 'jiji' and 'amazon' not in searchstores:
                        eachlink = settings.BASE_URL + f'search/?productsearch={searchplus}&stores%5B%5D=jumia&stores%5B%5D=ebay'

            onetrend = {'search': searchquery,
                        'link': eachlink,
                        'stores': eachstore}
            # print(onetrend)
            trendquery.append(onetrend)
        print('this is trendquery: ')
        print(trendquery)
        print(trendsearches)
        print(trending)

        total = time.time() - starttime
        context = {'res': prod,
                   'numberof': range(len(products)),
                   'presentpage': presentpage,
                   'time': total,
                   'search': search,
                   'trendsearches': trendquery,
                   'save': SavedProducts.objects.filter(account_id=request.user),
                   'saven': SavedProducts.objects.filter(account_id=request.user).count()}
    else:
        return redirect('account')
    return render(request, 'results.html', context)


# saved products
def savedproductspage(request):
    trendsearches = TrendSearch.objects.values('stores', 'search').annotate(dcount=Count('search')).order_by('-dcount')[:5]
    trendquery = []
    for each in trendsearches:
        searchquery = each['search']
        searchplus = searchquery.replace(' ', '+')
        searchstores = each['stores']
        eachstore = ''
        for eachstores in searchstores:
            eachstore += eachstores + ','
        eachstore = eachstore[:-1]
        eachlink = ''
        print(searchquery, searchstores)
        if 'jumia' in searchstores:
            if 'ebay' and 'aliexpress' and 'jiji' and 'amazon' not in searchstores:
                eachlink = settings.BASE_URL + f'search/?productsearch={searchplus}&stores%5B%5D=jumia'
        if 'ebay' in searchstores:
            if 'jumia' and 'aliexpress' and 'jiji' and 'amazon' not in searchstores:
                eachlink = settings.BASE_URL + f'search/?productsearch={searchplus}&stores%5B%5D=ebay'
        if 'ebay' in searchstores:
            if 'jumia' in searchstores:
                if 'aliexpress' and 'jiji' and 'amazon' not in searchstores:
                    eachlink = settings.BASE_URL + f'search/?productsearch={searchplus}&stores%5B%5D=jumia&stores%5B%5D=ebay'

        onetrend = {'search': searchquery,
                    'link': eachlink,
                    'stores': eachstore}
        trendquery.append(onetrend)
    context = {
        'trendsearches': trendquery,
        'save': SavedProducts.objects.filter(account_id=request.user),
        'saven': SavedProducts.objects.filter(account_id=request.user).count(),
    }
    return render(request, 'savedpro.html', context)


# saved products
def trendingproducts(request):
    # trending products
    trending = SavedProducts.objects.values('link', 'store', 'name', 'image', 'price').annotate(dcount=Count('link')).order_by('-dcount')[:5]
    print(trending)

    trendsearches = TrendSearch.objects.values('stores', 'search').annotate(dcount=Count('search')).order_by('-dcount')[:5]
    trendquery = []
    for each in trendsearches:
        searchquery = each['search']
        searchplus = searchquery.replace(' ', '+')
        searchstores = each['stores']
        eachstore = ''
        for eachstores in searchstores:
            eachstore += eachstores + ','
        eachstore = eachstore[:-1]
        eachlink = ''
        if 'jumia' in searchstores:
            if 'ebay' and 'aliexpress' and 'jiji' and 'amazon' not in searchstores:
                eachlink = settings.BASE_URL + f'search/?productsearch={searchplus}&stores%5B%5D=jumia'
        if 'ebay' in searchstores:
            if 'jumia' and 'aliexpress' and 'jiji' and 'amazon' not in searchstores:
                eachlink = settings.BASE_URL + f'search/?productsearch={searchplus}&stores%5B%5D=ebay'
        if 'ebay' in searchstores:
            if 'jumia' in searchstores:
                if 'aliexpress' and 'jiji' and 'amazon' not in searchstores:
                    eachlink = settings.BASE_URL + f'search/?productsearch={searchplus}&stores%5B%5D=jumia&stores%5B%5D=ebay'

        onetrend = {'search': searchquery,
                    'link': eachlink,
                    'stores': eachstore}
        trendquery.append(onetrend)
    context = {
        'trending': trending,
        'trendsearches': trendquery,
        'saven': SavedProducts.objects.filter(account_id=request.user).count(),
    }
    return render(request, 'trending.html', context)


# list of products
def listofproducts(products):
    return products


# scrape jumia and ebay
def scraper(html):
    soup = BeautifulSoup(str(html), 'lxml')
    jumproducts = soup.findAll('article', class_='prd _fb col c-prd')
    ebayproducts = soup.findAll('div', class_='s-item__wrapper clearfix')
    alljumproducts = []
    allebayproducts = []
    i = 0
    for item in jumproducts:
        try:
            title = item.find('h3', {'class': 'name'}).text
            title = title[:40]
            if len(title) < 28:
                title = title + '            '
            product = {
                'id': i,
                'img': item.find('div', {'class': 'img-c'}).find('img')['data-src'],
                'link': 'https://www.jumia.com.ng' + item.find('a', {'class': 'core'})['href'],
                'title': title,
                'store': 'Jumia',
                'price': float(item.find('div', {'class': 'prc'}).text.replace('₦', '').replace(',', '').strip()),
                'star_rating': round(Decimal((item.find('div', {'class': 'rev'}).find('div', {'class': 'stars _s'}).text.split(
                    'out')[0]).strip())),
                'reviews_count': item.find('div', {'class': 'rev'}).text.replace('(', '').replace(')', '').replace(
                    item.find('div', {'class': 'rev'}).find('div', {'class': 'stars _s'}).text, ''),
            }
            i = i + 1
            alljumproducts.append(product)
        except:
            pass
    for item in ebayproducts:
        try:
            title = item.find('h3', {'class': 's-item__title'}).text
            title = title[:40]
            if len(title) < 28:
                title = title + '           '
            product = {
                'id': i,
                'title': title,
                'store': 'eBay',
                'link': item.find('a', {'class': 's-item__link'})['href'],
                'img': item.find('div', {'class': 's-item__image-wrapper'}).find('img', {'class': 's-item__image-img'})[
                    'src'],
                'price': float(
                    item.find('span', {'class': 's-item__price'}).text.replace('$', '').replace(',', '').strip()),
                'condition': item.find('div', {'class': 's-item__subtitle'}).find('span',
                                                                                  {'class': 'SECONDARY_INFO'}).text,
                'reviews_count': item.find('span', {'class': 's-item__reviews-count'}).text.replace(
                    item.find('span', {'class': 's-item__reviews-count'}).find('span', {'class': 'clipped'}).text, ''),
                'shipping': item.find('span', {'class': 's-item__shipping s-item__logisticsCost'}).text,
                'star_rating': round(Decimal((item.find('div', {'class': 'x-star-rating'}).find('span', {
                    'class': 'clipped'}).text.split('out')[0]).strip())),
            }
            allebayproducts.append(product)
            i = i + 1
        except:
            pass

    return alljumproducts + allebayproducts


def updateItem(request):
    data = json.loads(request.body)
    print(data)
    productID = data["productId"]
    action = data["action"]
    print('Action: %s' % action)
    print('Product: %s' % productID)

    savedproduct = SavedProducts()
    savedproduct.account = request.user
    savedproduct.productId = data['productId']
    savedproduct.name = data['name']
    savedproduct.image = data['image']
    savedproduct.price = data['price']
    savedproduct.link = data['link']
    savedproduct.store = data['store']
    savedproduct.save()
    return JsonResponse('Item was added', safe=False)