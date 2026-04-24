from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('postbook', views.postbook, name='postbook'),
    path('displaybooks', views.displaybooks, name='displaybooks'),
    path('book_detail/<int:book_id>', views.book_detail, name='book_detail'),
    path('book/<int:book_id>/comment/', views.add_book_comment, name='add_book_comment'),
    path('book/<int:book_id>/rate/', views.rate_book, name='rate_book'),
    path('book/<int:book_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('mybooks', views.mybooks, name='mybooks'),
    path('book_delete/<int:book_id>', views.book_delete, name='book_delete'),
    path("inbox/", views.inbox, name="inbox"),
    path("compose/", views.compose_message, name="compose_message"),
    path("thread/<int:thread_id>/", views.thread_detail, name="thread_detail"),
    path("thread/<int:thread_id>/mark-read/", views.mark_thread_read, name="mark_thread_read"),
    path('aboutus', views.aboutus, name='aboutus'),
    path('searchbooks', views.searchbooks, name='searchbooks'),
    path('add-to-cart/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('remove-from-cart/<int:book_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('policy/<str:policy_type>/', views.policy_page, name='policy'),
]