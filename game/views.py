from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.cache import cache_page
from django.views.generic import ListView
from game.forms import AddPostForm, CommentForm
from game.models import Game, TagPost, UserVote, Comments, Basket


class Index(ListView):
    model = Game
    template_name = 'game/index.html'
    context_object_name = 'games'
    paginate_by = 9

    def get_queryset(self):
        page_number = self.request.GET.get('page', 1)
        cache_key = f'published_games_list_page_{page_number}'
        games = cache.get(cache_key)

        if not games:
            games = Game.objects.filter(is_published=Game.Status.PUBLISHED).select_related('author')
            cache.set(cache_key, games, 60 * 15)  # Кэшируем на 15 минут

        return games


class YourPosts(ListView):
    model = Game
    template_name = 'game/edit_posts.html'
    context_object_name = 'games'
    paginate_by = 9

    def get_queryset(self):
        page_number = self.request.GET.get('page', 1)
        cache_key = f'your_posts_{self.request.user.id}_page_{page_number}'
        games = cache.get(cache_key)

        if not games:
            games = Game.objects.filter(
                Q(is_published=Game.Status.PUBLISHED) & Q(author=self.request.user)).select_related('author')
            cache.set(cache_key, games, 60 * 15)  # Кэшируем на 15 минут

        return games


class Search(ListView):
    paginate_by = 9
    model = Game
    template_name = 'game/index.html'
    context_object_name = 'games'

    def get_queryset(self):
        query = self.request.GET.get('q')
        page_number = self.request.GET.get('page', 1)
        cache_key = f'search_results_{query}_page_{page_number}'
        games = cache.get(cache_key)

        if not games:
            games = Game.objects.filter(
                Q(title__icontains=query) |
                Q(author__username__icontains=query)
            ).select_related('author')
            cache.set(cache_key, games, 60 * 15)  # Кэшируем на 15 минут

        return games

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['q'] = self.request.GET.get('q')
        return context


def post(request, post_slug):
    game = Game.objects.select_related('author').filter(slug=post_slug).first()
    baskets = Basket.objects.filter(user=request.user,).select_related('product')
    user = request.user

    # Кэширование данных
    cache_key = f'game_{post_slug}_data'
    cached_data = cache.get(cache_key)

    if cached_data:
        user_data, comments, user_vote, total_likes, total_dislikes, rating = cached_data
    else:

        user_data = None
        if game.author:
            aut = game.author
            user_data = {
                "username": aut.username,
                "email": aut.email,
                "photo": aut.photo,
                "date_birth": aut.date_birth
            }

        if user.is_authenticated:
            user_comments = game.comments.filter(author=user).order_by('-created_at').select_related('author')
            other_comments = game.comments.exclude(author=user).order_by('-created_at').select_related('author')
            comments = list(user_comments) + list(other_comments)
            user_vote = UserVote.objects.filter(user=user, game=game).first()
        else:
            comments = game.comments.all().order_by('-created_at').select_related('author')
            user_vote = None

        game_votes = game.votes.aggregate(
            total_likes=Count('id', filter=Q(vote=UserVote.LIKE)),
            total_dislikes=Count('id', filter=Q(vote=UserVote.DISLIKE))
        )

        total_likes = game_votes['total_likes'] or 0
        total_dislikes = game_votes['total_dislikes'] or 0
        total_votes = total_likes + total_dislikes
        rating = 0
        if total_votes > 0:
            rating = 5 * (total_likes / total_votes)

        cache.set(cache_key, (user_data, comments, user_vote, total_likes, total_dislikes, rating),
                  60 * 10)  # Кэшируем на 15 минут

    if request.method == 'POST':
        if 'like' in request.POST:
            UserVote.objects.update_or_create(
                user=user, game=game, defaults={'vote': UserVote.LIKE}
            )
            cache.delete(cache_key)  # Удаление кэша после лайка
            return redirect('post', post_slug=post_slug)

        elif 'dislike' in request.POST:
            UserVote.objects.update_or_create(
                user=user, game=game, defaults={'vote': UserVote.DISLIKE}
            )
            cache.delete(cache_key)  # Удаление кэша после дизлайка
            return redirect('post', post_slug=post_slug)

        else:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = game
                comment.author = user
                comment.save()
                cache.delete(cache_key)  # Удаление кэша при добавлении комментария
                return redirect('post', post_slug=post_slug)

    form = CommentForm()

    return render(request, 'game/game_page.html', {
        'post_content': game,
        'comments': comments,
        'form': form,
        'user_vote': user_vote,
        't_likes': total_likes,
        't_dislikes': total_dislikes,
        'rat': rating,
        'user_data': user_data,
        'basket_count': baskets
    })


def tags(request):
    cache_key = 'tags_list'
    tags_list = cache.get(cache_key)

    if not tags_list:
        tags_list = TagPost.objects.all()
        cache.set(cache_key, tags_list, 60 * 60)  # Кэшируем на 1 час

    return render(request, 'game/tags.html', {'tags': tags_list})


def show_tag_postlist(request, tag_slug):
    cache_key = f'tag_postlist_{tag_slug}'
    posts = cache.get(cache_key)

    if not posts:
        tag = get_object_or_404(TagPost, slug=tag_slug)
        posts = tag.tags.filter(is_published=Game.Status.PUBLISHED).select_related('author')
        cache.set(cache_key, posts, 60 * 15)

    context = {
        'games': posts,
    }

    return render(request, 'game/index.html', context)


@cache_page(60 * 15)
@login_required
def add_page(request):
    if request.method == 'POST':
        form = AddPostForm(request.POST, request.FILES)

        if form.is_valid():
            cache.delete_pattern('published_games_list*')
            cd = form.cleaned_data
            tag_ids = request.POST.getlist("tags")

            tags = TagPost.objects.filter(id__in=tag_ids)

            game = Game(
                title=cd['title'],
                content=cd['content'],
                is_published=cd['is_published'],
                price=cd['price'],
                image=cd['image'],
                author=request.user
            )
            flag = True
            titles = Game.objects.all()
            for t in titles:
                if t.title == game.title:
                    flag = False
            if flag:
                game.save()
                game.tags.set(tags)

            return redirect('home')

    form = AddPostForm()
    data = {
        'form': form,
    }
    return render(request, 'game/add_page.html', context=data)


def handle_uploaded_file(f):
    with open(f"uploads/{f.name}", "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def edit_game(request, post_slug):
    game = Game.objects.select_related('author').filter(slug=post_slug).first()

    if game.author != request.user:
        return HttpResponseForbidden("Вы не можете редактировать этот пост.")
    if request.method == 'POST':
        form = AddPostForm(request.POST, request.FILES, instance=game)
        if form.is_valid():
            cache.delete(f'game_{post_slug}_data')
            form.save()
            return redirect('post', post_slug=game.slug)  # перенаправляем на страницу поста
    else:
        form = AddPostForm(instance=game)
    return render(request, 'game/edit_game.html', {'form': form, 'game': game})


@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comments, id=comment_id, author=request.user)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            data = {'games': Game.objects.all().filter(is_published=Game.Status.PUBLISHED)}
            return render(request, 'game/index.html', context=data)
    else:
        form = CommentForm(instance=comment, )

    return render(request, 'game/edit_comment.html', {'form': form})


def contact(request):
    return render(request, 'game/contact.html')


def game_list(request):
    order = request.GET.get('order')

    if order == 'newest':
        games = Game.objects.all().order_by('-time_create').select_related('author')  # сортировка по дате добавления
    elif order == 'price':
        games = Game.objects.all().order_by('price').select_related('author')  # сортировка по дате добавления
    else:
        games = Game.objects.all().select_related('author')  # если фильтр не выбран, показываем все игры

    context = {
        'games': games,

    }

    return render(request, 'game/index.html', context)


def basket_add(request,post_slug):
    game = Game.objects.get(slug=post_slug)
    baskets = Basket.objects.filter(user=request.user,product=game)

    if not baskets.exists():
        Basket.objects.create(user=request.user,product=game,quantity=1,all_price=game.price)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        baskets = baskets.first()
        baskets.quantity += 1
        baskets.all_price += game.price
        baskets.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def basket_delete(request,post_slug):
    game = Game.objects.get(slug=post_slug)
    baskets = Basket.objects.filter(user=request.user,product=game)
    baskets = baskets.first()
    if baskets.quantity - 1 < 0:
        pass
    else:
        baskets.quantity -= 1
        baskets.all_price -= game.price
        baskets.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))