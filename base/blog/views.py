from django.shortcuts import render, redirect, get_object_or_404
from django.core.cache import cache
from django.db.models import Q, Prefetch
from django.contrib import messages
from .models import Post, Category, Tag, UserProfile, Contacts, SocialNetworks
from .forms import ContactForm, CommentForm, SubscriberForm

# Кэширование часто используемых данных
def get_cached_data():
    categories = cache.get('categories')
    if not categories:
        categories = Category.objects.all()
        cache.set('categories', categories, 60 * 15)  # Кэширование на 15 минут

    popular_posts = cache.get('popular_posts')
    if not popular_posts:
        popular_posts = Post.objects.filter(status=Post.Status.PUBLISHED).order_by('-views')[:3]
        cache.set('popular_posts', popular_posts, 60 * 15)  # Кэширование на 15 минут

    social = cache.get('social')
    if not social:
        social = SocialNetworks.objects.all()
        cache.set('social', social, 60 * 15)  # Кэширование на 15 минут

    contacts = cache.get('contacts')
    if not contacts:
        contacts = Contacts.objects.all()
        cache.set('contacts', contacts, 60 * 15)  # Кэширование на 15 минут

    return categories, popular_posts, social, contacts

def home(request):
    categories, popular_posts, social, contacts = get_cached_data()
    latest_posts = Post.objects.filter(status=Post.Status.PUBLISHED).order_by('-publish')[:3]
    hero_post = Post.objects.filter(status=Post.Status.PUBLISHED).order_by('-publish').first()

    return render(request, 'blog/home.html', {
        'latest_posts': latest_posts,
        'popular_posts': popular_posts,
        'categories': categories,
        'hero_post': hero_post,
        'social': social,
        'contacts': contacts
    })

def blog(request):
    categories, popular_posts, social, contacts = get_cached_data()
    posts = Post.objects.filter(status=Post.Status.PUBLISHED).order_by('-publish').select_related('author', 'category').prefetch_related('tags')

    return render(request, 'blog/blog.html', {
        'posts': posts,
        'categories': categories,
        'latest_posts': popular_posts,
        'popular_posts': popular_posts,
        'social': social,
        'contacts': contacts
    })

def post_detail(request, slug):
    categories, popular_posts, social, contacts = get_cached_data()
    post = get_object_or_404(Post.objects.select_related('author', 'category').prefetch_related('tags'), slug=slug)
    formatted_content = post.get_formatted_content()
    post.views += 1  # Увеличиваем количество просмотров
    post.save()  # Сохраняем изменения в базе данных
    similar_posts = post.get_similar_posts().select_related('author', 'category').prefetch_related('tags')  # Вызываем метод на экземпляре post
    author_profile = get_object_or_404(UserProfile, user=post.author)

    comments = post.comments.filter(active=True)
    new_comment = None
    
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
            return redirect(new_comment.get_absolute_url())
    else:
        comment_form = CommentForm()
    
    return render(request, 'blog/post_detail.html', {
        'post': post,
        'categories': categories,
        'popular_posts': popular_posts,
        'formatted_content': formatted_content,
        'similar_posts': similar_posts,
        'author_profile': author_profile,
        'social': social,
        'contacts': contacts,
        'comments': comments,
        'comment_form': comment_form,
        'new_comment': new_comment
    })

def category_list(request, slug):
    categories, popular_posts, social, contacts = get_cached_data()
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=category).filter(status=Post.Status.PUBLISHED).order_by('-publish').select_related('author', 'category').prefetch_related('tags')

    return render(request, 'blog/category_list.html', {
        'category': category,
        'categories': categories,
        'posts': posts,
        'popular_posts': popular_posts,
        'social': social,
        'contacts': contacts
    })

def contacts(request):
    _, _, social, contacts = get_cached_data()

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            # Вывод данных в консоль
            print(f'Имя: {name}')
            print(f'Email: {email}')
            print(f'Тема: {subject}')
            print(f'Сообщение: {message}')

            # Перенаправление после успешной отправки
            return redirect('contact_success')
    else:
        form = ContactForm()

    return render(request, 'blog/contacts.html', {
        'contacts': contacts,
        'social': social,
        'form': form,
    })

def about(request):
    authors = UserProfile.objects.all()
    _, _, _, contacts = get_cached_data()
    return render(request, 'blog/about.html', {
        'authors': authors,
        'contacts': contacts
    })

def tag_list(request, slug):
    categories, popular_posts, social, contacts = get_cached_data()
    tag = get_object_or_404(Tag, slug=slug)
    posts = Post.objects.filter(tags=tag).filter(status=Post.Status.PUBLISHED).order_by('-publish').select_related('author', 'category').prefetch_related('tags')

    return render(request, 'blog/tag_list.html', {
        'tag': tag,
        'categories': categories,
        'posts': posts,
        'popular_posts': popular_posts,
        'social': social,
        'contacts': contacts
    })

def search(request):
    query = request.GET.get('q')
    _, _, _, contacts = get_cached_data()
    if query:
        results = Post.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        ).select_related('author', 'category').prefetch_related('tags')
    else:
        results = []

    return render(request, 'blog/search_results.html', {'results': results,
                                                        'query': query,
                                                        'contacts': contacts})

def contact_success(request):
    _, _, _, contacts = get_cached_data()
    return render(request, 'blog/contact_success.html', {
        'contacts': contacts
    })


def subscribe(request):
    if request.method == 'POST':
        form = SubscriberForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Вы успешно подписались на рассылку!')
            return redirect('home')  # Перенаправление на главную страницу
    else:
        form = SubscriberForm()
    return render(request, 'blog/subscribe.html', {'form': form})