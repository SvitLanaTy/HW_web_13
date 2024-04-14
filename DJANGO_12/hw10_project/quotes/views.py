from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect

from .forms import AuthorForm, QuoteForm
from .models import Quote, Author, Tag


def main(request, page=1):
    quotes = Quote.objects.select_related('author').prefetch_related('tags').all()
    per_page = 10
    paginator = Paginator(list(quotes), per_page)
    quotes_on_page = paginator.page(page)
    top_tags = Tag.objects.annotate(num_quotes=Count('quote')).order_by('-num_quotes')[:10]
    return render(request, 'quotes/index.html',
                  context={'quotes': quotes_on_page, 'paginator': paginator, 'top_tags': top_tags})


def author_detail(request, author_id):
    author = get_object_or_404(Author, pk=author_id)
    return render(request, 'quotes/author_detail.html', {'author': author})



@login_required
def add_author(request):
    if not request.user.is_authenticated:
        return redirect(to='quotes:root')

    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(to='quotes:add_quote')
        else:
            return render(request, 'quotes/add_author.html', {'form': form})
    return render(request, 'quotes/add_author.html', {'form': AuthorForm()})


@login_required
def add_quote(request):
    if not request.user.is_authenticated:
        return redirect(to='quotes:root')

    authors = Author.objects.all()
    tags = Tag.objects.all()

    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            new_quote = form.save(commit=False)  
            new_quote.author_id = request.POST.get(
                'author') 
            new_quote.save()            

            tags_selected = request.POST.getlist('tags')
            print("Tags selected:", tags_selected)

            choice_tags = Tag.objects.filter(id__in=tags_selected)
            print("Choice tags:", choice_tags)

            for tag in choice_tags.iterator():
                new_quote.tags.add(tag)

            return redirect('/')
        else:
            return render(request, 'quotes/add_quote.html', {'form': form})

    return render(request, 'quotes/add_quote.html', {'tags': tags, 'authors': authors})


def quotes_by_tag(request, tag_id, page=1):
    tag = Tag.objects.get(pk=tag_id)
    quotes = Quote.objects.filter(tags=tag)

      
    top_tags = Tag.objects.annotate(num_quotes=Count('quote')).order_by('-num_quotes')[:10]

    return render(request, 'quotes/quotes_by_tag.html',
                  {'tag': tag, 'quotes': quotes, 'top_tags': top_tags})