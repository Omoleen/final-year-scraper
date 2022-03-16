from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login
from django.urls import reverse
from bs4 import BeautifulSoup
import requests
from django.contrib import messages
from FinalScraper import settings
from decimal import Decimal
import random
from django.contrib.auth.models import User
from .models import SavedProducts
from .models import TrendSearch
import json
from django.db.models import Count
from selenium import webdriver
import os


def account(request):  # sign up
    if not request.user.is_authenticated:
        messages.info(request, 'Please Login or Register')
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
            urls = []
            sel_urls = []
            # individual stores
            if 'jumia' in stores and len(stores) == 1:
                if 'ebay' and 'aliexpress' and 'amazon' not in stores:
                    urls = [f"https://www.jumia.com.ng/catalog/?q={search}"]
                    presentpage = f'search/?productsearch={search}&stores%5B%5D=jumia'
            if 'ebay' in stores and len(stores) == 1:
                if 'jumia' and 'aliexpress' and 'amazon' not in stores:
                    urls = [f"https://www.ebay.com/sch/i.html?_from=R40&_trksid=m570.l1313&_nkw={search}&_sacat=0"]
                    presentpage = f'search/?productsearch={search}&stores%5B%5D=ebay'
            if 'amazon' in stores and len(stores) == 1:
                if 'ebay' and 'aliexpress' and 'jumia' not in stores:
                    sel_urls = [f"https://www.amazon.com/s?k={search}&ref=nb_sb_noss"]
                    presentpage = f'search/?productsearch={search}&stores%5B%5D=amazon'
            if 'aliexpress' in stores and len(stores) == 1:
                if 'ebay' and 'jumia' and 'amazon' not in stores:
                    sel_urls = [f"https://www.aliexpress.com/wholesale?catId=0&initiative_id=SB_20220315093931&SearchText={search}"]
                    presentpage = f'search/?productsearch={search}&stores%5B%5D=aliexpress'

            # two stores
            # jumia and aliexpress
            if 'aliexpress' in stores:
                if 'jumia' in stores:
                    if 'ebay' and 'amazon' not in stores:
                        sel_urls = [f"https://www.aliexpress.com/wholesale?catId=0&initiative_id=SB_20220315093931&SearchText={search}"]
                        urls = [f"https://www.jumia.com.ng/catalog/?q={search}"]
                        presentpage = f'search/?productsearch={search}&stores%5B%5D=jumia&stores%5B%5D=aliexpress'

            # jumia and amazon
            if 'amazon' in stores:
                if 'jumia' in stores:
                    if 'ebay' and 'aliexpress' not in stores:
                        sel_urls = [f"https://www.amazon.com/s?k={search}&ref=nb_sb_noss"]
                        urls = [f"https://www.jumia.com.ng/catalog/?q={search}"]
                        presentpage = f'search/?productsearch={search}&stores%5B%5D=jumia&stores%5B%5D=amazon'

            # aliexpress and amazon
            if 'amazon' in stores:
                if 'aliexpress' in stores:
                    if 'ebay' and 'jumia' not in stores:
                        sel_urls = [f"https://www.amazon.com/s?k={search}&ref=nb_sb_noss",
                                    f"https://www.aliexpress.com/wholesale?catId=0&initiative_id=SB_20220315093931&SearchText={search}"]
                        presentpage = f'search/?productsearch={search}&stores%5B%5D=amazon&stores%5B%5D=aliexpress'

            # ebay and aliexpress
            if 'ebay' in stores:
                if 'aliexpress' in stores:
                    if 'amazon' and 'jumia' not in stores:
                        sel_urls = [f"https://www.aliexpress.com/wholesale?catId=0&initiative_id=SB_20220315093931&SearchText={search}"]
                        urls = [f"https://www.ebay.com/sch/i.html?_from=R40&_trksid=m570.l1313&_nkw={search}&_sacat=0"]
                        presentpage = f'search/?productsearch={search}&stores%5B%5D=ebay&stores%5B%5D=aliexpress'

            # ebay and amazon
            if 'ebay' in stores:
                if 'amazon' in stores:
                    if 'aliexpress' and 'jumia' not in stores:
                        sel_urls = [f"https://www.amazon.com/s?k={search}&ref=nb_sb_noss"]
                        urls = [f"https://www.ebay.com/sch/i.html?_from=R40&_trksid=m570.l1313&_nkw={search}&_sacat=0"]
                        presentpage = f'search/?productsearch={search}&stores%5B%5D=ebay&stores%5B%5D=amazon'

            # ebay and jumia
            if 'ebay' in stores:
                if 'jumia' in stores:
                    if 'aliexpress' and 'amazon' not in stores:
                        presentpage = f'search/?productsearch={search}&stores%5B%5D=jumia&stores%5B%5D=ebay'
                        urls = [f"https://www.jumia.com.ng/catalog/?q={search}", f"https://www.ebay.com/sch/i.html?_from=R40&_trksid=m570.l1313&_nkw={search}&_sacat=0",
                                ]

            # three stores
            # ebay and jumia and aliexpress
            if 'ebay' in stores:
                if 'jumia' in stores:
                    if 'aliexpress' in stores:
                        if 'amazon' not in stores:
                            presentpage = f'search/?productsearch={search}&stores%5B%5D=jumia&stores%5B%5D=ebay&stores%5B%5D=aliexpress'
                            sel_urls = [f"https://www.aliexpress.com/wholesale?catId=0&initiative_id=SB_20220315093931&SearchText={search}"]
                            urls = [f"https://www.ebay.com/sch/i.html?_from=R40&_trksid=m570.l1313&_nkw={search}&_sacat=0",
                                    f"https://www.jumia.com.ng/catalog/?q={search}"]

            # ebay and jumia and amazon
            if 'ebay' in stores:
                if 'jumia' in stores:
                    if 'amazon' in stores:
                        if 'aliexpress' not in stores:
                            presentpage = f'search/?productsearch={search}&stores%5B%5D=jumia&stores%5B%5D=ebay&stores%5B%5D=amazon'
                            sel_urls = [f"https://www.amazon.com/s?k={search}&ref=nb_sb_noss"]
                            urls = [f"https://www.ebay.com/sch/i.html?_from=R40&_trksid=m570.l1313&_nkw={search}&_sacat=0",
                                    f"https://www.jumia.com.ng/catalog/?q={search}"]

            # aliexpress and amazon and jumia
            if 'amazon' in stores:
                if 'aliexpress' in stores:
                    if 'jumia' in stores:
                        if 'ebay' not in stores:
                            sel_urls = [f"https://www.amazon.com/s?k={search}&ref=nb_sb_noss",
                                        f"https://www.aliexpress.com/wholesale?catId=0&initiative_id=SB_20220315093931&SearchText={search}"]
                            urls = [f"https://www.jumia.com.ng/catalog/?q={search}"]
                            presentpage = f'search/?productsearch={search}&stores%5B%5D=jumia&stores%5B%5D=amazon&stores%5B%5D=aliexpress'

            # aliexpress and amazon and ebay
            if 'amazon' in stores:
                if 'aliexpress' in stores:
                    if 'ebay' in stores:
                        if 'jumia' not in stores:
                            sel_urls = [f"https://www.amazon.com/s?k={search}&ref=nb_sb_noss",
                                        f"https://www.aliexpress.com/wholesale?catId=0&initiative_id=SB_20220315093931&SearchText={search}"]
                            urls = [f"https://www.ebay.com/sch/i.html?_from=R40&_trksid=m570.l1313&_nkw={search}&_sacat=0"]
                            presentpage = f'search/?productsearch={search}&stores%5B%5D=ebay&stores%5B%5D=amazon&stores%5B%5D=aliexpress'

            # all the 4 stores
            if 'amazon' in stores:
                if 'aliexpress' in stores:
                    if 'ebay' in stores:
                        if 'jumia' in stores:
                            sel_urls = [f"https://www.amazon.com/s?k={search}&ref=nb_sb_noss",
                                        f"https://www.aliexpress.com/wholesale?catId=0&initiative_id=SB_20220315093931&SearchText={search}"]
                            urls = [f"https://www.ebay.com/sch/i.html?_from=R40&_trksid=m570.l1313&_nkw={search}&_sacat=0",
                                    f"https://www.jumia.com.ng/catalog/?q={search}"]
                            presentpage = f'search/?productsearch={search}&stores%5B%5D=jumia&stores%5B%5D=ebay&stores%5B%5D=amazon&stores%5B%5D=aliexpress'

        products = []
        normhtml = ''
        selhtml = ''
        # for request urls
        if urls != 0:
            for url in urls:
                res = requests.get(url)
                data = res.text
                normhtml = normhtml + '' + data

        # for selenium urls
        if sel_urls != 0:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--no-sandbox")
            driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),
                                      chrome_options=chrome_options)
            for i in sel_urls:
                driver.get(i)
                data = driver.page_source
                selhtml = selhtml + '' + data

            driver.quit()

        # to scrape products from html
        fullhtml = normhtml + '' + selhtml
        products = scraper(fullhtml)

        numb = len(products)
        # print(numb)
        prod = listofproducts(products)
        prod = random.sample(prod, len(prod))
        # print(products)

        # trending products
        # trending = SavedProducts.objects.values('link', 'store', 'name', 'image', 'price').annotate(dcount=Count('link')).order_by('-dcount')[:5]
        trendsearches = TrendSearch.objects.values('stores', 'search').annotate(dcount=Count('search')).order_by('-dcount')[:5]
        trendquery = []
        for each in trendsearches:
            searchquery = each['search']
            searchplus = searchquery.replace(' ', '+')
            searchstores = each['stores']
            eachstore = ''
            # for trend searches
            for eachstores in searchstores:
                eachstore += eachstores + ','
            eachstore = eachstore[:-1]
            onetrend = {'search': searchquery,
                        'link': TrendSearches(searchstores, searchplus),
                        'stores': eachstore}
            # print(onetrend)
            trendquery.append(onetrend)

        context = {'res': prod,
                   'numberof': range(len(products)),
                   'presentpage': presentpage,
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
        # if 'jumia' in searchstores:
        #     if 'ebay' and 'aliexpress' and 'amazon' not in searchstores:
        #         eachlink = settings.BASE_URL + f'search/?productsearch={searchplus}&stores%5B%5D=jumia'
        # if 'ebay' in searchstores:
        #     if 'jumia' and 'aliexpress' and 'amazon' not in searchstores:
        #         eachlink = settings.BASE_URL + f'search/?productsearch={searchplus}&stores%5B%5D=ebay'
        # if 'ebay' in searchstores:
        #     if 'jumia' in searchstores:
        #         if 'aliexpress' and 'amazon' not in searchstores:
        #             eachlink = settings.BASE_URL + f'search/?productsearch={searchplus}&stores%5B%5D=jumia&stores%5B%5D=ebay'

        onetrend = {'search': searchquery,
                    'link': TrendSearches(searchstores, searchplus),
                    'stores': eachstore}
        trendquery.append(onetrend)
    context = {
        'trendsearches': trendquery,
        'save': SavedProducts.objects.filter(account_id=request.user),
        'saven': SavedProducts.objects.filter(account_id=request.user).count(),
    }
    return render(request, 'savedpro.html', context)


def TrendSearches(trendsearches, searchplus):
    # trendsearches = TrendSearch.objects.values('stores', 'search').annotate(dcount=Count('search')).order_by('-dcount')[:5]
    eachlink = ''
    # individual stores
    if 'jumia' in trendsearches and len(trendsearches) == 1:
        if 'ebay' and 'aliexpress' and 'amazon' not in trendsearches:
            eachlink = settings.BASE_URL + f'search/?productsearch={searchplus}&stores%5B%5D=jumia'
    if 'ebay' in trendsearches and len(trendsearches) == 1:
        if 'jumia' and 'aliexpress' and 'amazon' not in trendsearches:
            eachlink = settings.BASE_URL + f'search/?productsearch={searchplus}&stores%5B%5D=ebay'
    if 'amazon' in trendsearches and len(trendsearches) == 1:
        if 'ebay' and 'aliexpress' and 'jumia' not in trendsearches:
            eachlink = settings.BASE_URL + f'search/?productsearch={searchplus}&stores%5B%5D=amazon'
    if 'aliexpress' in trendsearches and len(trendsearches) == 1:
        if 'ebay' and 'jumia' and 'amazon' not in trendsearches:
            eachlink = settings.BASE_URL + f'search/?productsearch={searchplus}&stores%5B%5D=aliexpress'

    # two stores
    # jumia and aliexpress
    if 'aliexpress' in trendsearches:
        if 'jumia' in trendsearches:
            if 'ebay' and 'amazon' not in trendsearches:
                eachlink = settings.BASE_URL + f'search/?productsearch={searchplus}&stores%5B%5D=jumia&stores%5B%5D=aliexpress'

    # jumia and amazon
    if 'amazon' in trendsearches:
        if 'jumia' in trendsearches:
            if 'ebay' and 'aliexpress' not in trendsearches:
                eachlink = settings.BASE_URL + f'search/?productsearch={searchplus}&stores%5B%5D=jumia&stores%5B%5D=amazon'

    # aliexpress and amazon
    if 'amazon' in trendsearches:
        if 'aliexpress' in trendsearches:
            if 'ebay' and 'jumia' not in trendsearches:
                eachlink = settings.BASE_URL + f'search/?productsearch={searchplus}&stores%5B%5D=amazon&stores%5B%5D=aliexpress'

    # ebay and aliexpress
    if 'ebay' in trendsearches:
        if 'aliexpress' in trendsearches:
            if 'amazon' and 'jumia' not in trendsearches:
                eachlink = settings.BASE_URL + f'search/?productsearch={searchplus}&stores%5B%5D=ebay&stores%5B%5D=aliexpress'

    # ebay and amazon
    if 'ebay' in trendsearches:
        if 'amazon' in trendsearches:
            if 'aliexpress' and 'jumia' not in trendsearches:
                eachlink = settings.BASE_URL + f'search/?productsearch={searchplus}&stores%5B%5D=ebay&stores%5B%5D=amazon'

    # ebay and jumia
    if 'ebay' in trendsearches:
        if 'jumia' in trendsearches:
            if 'aliexpress' and 'amazon' not in trendsearches:
                eachlink = settings.BASE_URL + f'search/?productsearch={searchplus}&stores%5B%5D=jumia&stores%5B%5D=ebay'

    # three stores
    # ebay and jumia and aliexpress
    if 'ebay' in trendsearches:
        if 'jumia' in trendsearches:
            if 'aliexpress' in trendsearches:
                if 'amazon' not in trendsearches:
                    eachlink = settings.BASE_URL + f'search/?productsearch={searchplus}&stores%5B%5D=jumia&stores%5B%5D=ebay&stores%5B%5D=aliexpress'

    # ebay and jumia and amazon
    if 'ebay' in trendsearches:
        if 'jumia' in trendsearches:
            if 'amazon' in trendsearches:
                if 'aliexpress' not in trendsearches:
                    eachlink = settings.BASE_URL + f'search/?productsearch={searchplus}&stores%5B%5D=jumia&stores%5B%5D=ebay&stores%5B%5D=amazon'

    # aliexpress and amazon and jumia
    if 'amazon' in trendsearches:
        if 'aliexpress' in trendsearches:
            if 'jumia' in trendsearches:
                if 'ebay' not in trendsearches:
                    eachlink = settings.BASE_URL + f'search/?productsearch={searchplus}&stores%5B%5D=jumia&stores%5B%5D=amazon&stores%5B%5D=aliexpress'

    # aliexpress and amazon and ebay
    if 'amazon' in trendsearches:
        if 'aliexpress' in trendsearches:
            if 'ebay' in trendsearches:
                if 'jumia' not in trendsearches:
                    eachlink = settings.BASE_URL + f'search/?productsearch={searchplus}&stores%5B%5D=ebay&stores%5B%5D=amazon&stores%5B%5D=aliexpress'

    # all the 4 stores
    if 'amazon' in trendsearches:
        if 'aliexpress' in trendsearches:
            if 'ebay' in trendsearches:
                if 'jumia' in trendsearches:
                    eachlink = settings.BASE_URL + f'search/?productsearch={searchplus}&stores%5B%5D=jumia&stores%5B%5D=ebay&stores%5B%5D=amazon&stores%5B%5D=aliexpress'

    return eachlink


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
        # eachlink = ''
        # if 'jumia' in searchstores:
        #     if 'ebay' and 'aliexpress' and 'jiji' and 'amazon' not in searchstores:
        #         eachlink = settings.BASE_URL + f'search/?productsearch={searchplus}&stores%5B%5D=jumia'
        # if 'ebay' in searchstores:
        #     if 'jumia' and 'aliexpress' and 'jiji' and 'amazon' not in searchstores:
        #         eachlink = settings.BASE_URL + f'search/?productsearch={searchplus}&stores%5B%5D=ebay'
        # if 'ebay' in searchstores:
        #     if 'jumia' in searchstores:
        #         if 'aliexpress' and 'jiji' and 'amazon' not in searchstores:
        #             eachlink = settings.BASE_URL + f'search/?productsearch={searchplus}&stores%5B%5D=jumia&stores%5B%5D=ebay'

        onetrend = {'search': searchquery,
                    'link': TrendSearches(searchstores, searchplus),
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
    soup = BeautifulSoup(str(html), 'html.parser')
    jumproducts = soup.findAll('article', class_='prd _fb col c-prd')
    aliexpressproducts = soup.findAll('a', class_='_3t7zg _2f4Ho')
    ebayproducts = soup.findAll('div', class_='s-item__wrapper clearfix')
    amazonproducts = soup.findAll('div', class_='s-result-item')
    alljumproducts = []
    allebayproducts = []
    allamazonproducts = []
    allaliexpressproducts = []
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
            product1 = {
                'id': i,
                'title': title,
                'store': 'eBay',
                'link': item.find('a', {'class': 's-item__link'})['href'],
                'img': item.find('div', {'class': 's-item__image-wrapper'}).find('img', {'class': 's-item__image-img'})[
                    'src'],
                'price': round((float(
                    item.find('span', {'class': 's-item__price'}).text.replace('$', '').replace(',', '').strip()) * 570), 2),
                'condition': item.find('div', {'class': 's-item__subtitle'}).find('span',
                                                                                  {'class': 'SECONDARY_INFO'}).text,
                'reviews_count': item.find('span', {'class': 's-item__reviews-count'}).text.replace(
                    item.find('span', {'class': 's-item__reviews-count'}).find('span', {'class': 'clipped'}).text, ''),
                'shipping': item.find('span', {'class': 's-item__shipping s-item__logisticsCost'}).text,
                'star_rating': round(Decimal((item.find('div', {'class': 'x-star-rating'}).find('span', {
                    'class': 'clipped'}).text.split('out')[0]).strip())),
            }
            allebayproducts.append(product1)
            i = i + 1
        except:
            pass
    for item in amazonproducts:
        try:
            rating = item.find('span', {'class': 'a-icon-alt'}).text
            rating = rating.split()
            rating = round(Decimal(rating[0]))
            title = item.find('span', {'class': 'a-size-medium a-color-base a-text-normal'}).text
            title = title[:40]
            if len(title) < 28:
                title = title + '           '
            product2 = {
                'id': i,
                'store': 'Amazon',
                'img': item.find('span', {'data-component-type': 's-product-image'}).find('img', {'class': 's-image'})['src'],
                'link': 'https://www.amazon.com' + item.find('a', {'class': 'a-link-normal s-no-outline'})['href'],
                'title': title,
                'price': round((float(item.find('span', {'class': 'a-price'}).find('span', {'class': 'a-offscreen'}).text.replace('$', '').strip()) * 570), 2),
                'star_rating': rating,
                'reviews_count': item.find('span', {'class': 'a-size-base s-underline-text'}).text,
            }
            allamazonproducts.append(product2)
            i = i + 1
        except:
            pass
    for item in aliexpressproducts:
        try:
            reviews_count = item.find('span', {'class': '_1kNf9'}).text
            reviews_count = reviews_count.split()
            reviews_count = reviews_count[0]
            title = item.find('h1', {'class': '_18_85'}).text
            title = title[:40]
            if len(title) < 28:
                title = title + '           '
            product3 = {
                'id': i,
                'store': 'Aliexpress',
                'img': item.find('div', {'class': '_3A0hz gYJvK'}).find('img')['src'],
                'link': 'https://www.aliexpress.com' + item['href'],
                'title': title,
                'price': round((float(item.find('div', {'class': 'mGXnE _37W_B'}).find('span', {'style': 'font-size: 20px;'}).text.replace('US $', '').strip()) * 570), 2),
                'star_rating': round(Decimal(item.find('span', {'class': 'eXPaM'}).text.strip())),
                'reviews_count': reviews_count,
            }
            allaliexpressproducts.append(product3)
            i = i + 1
        except:
            pass

    return alljumproducts + allebayproducts + allamazonproducts + allaliexpressproducts


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