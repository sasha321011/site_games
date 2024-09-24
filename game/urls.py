from django.urls import path

from . import views

urlpatterns = [
    path('', views.Index.as_view(), name='home'),
    path('contacts', views.contact, name='contacts'),
    path('game/<slug:post_slug>', views.post, name='post'),
    path('tag', views.tags, name='tags'),
    path('tag/<slug:tag_slug>', views.ShowTagPostList.as_view(), name='tag'),
    path('add_page/', views.add_page, name='add_page'),

    path('basket-add/<slug:post_slug>',views.basket_add,name='basket_add'),
    path('basket-delete/<slug:post_slug>', views.basket_delete, name='basket_delete'),

    path('game/<slug:post_slug>/edit/', views.edit_game, name='edit_game'),
    path('your-posts/', views.YourPosts.as_view(), name='your_posts'),
    path('comment/edit/<int:comment_id>/', views.edit_comment, name='edit_comment'),

    path('search/', views.Search.as_view(), name='search_results'),
    path('filter/',views.GameListFilters.as_view(),name='game_filter')

]
