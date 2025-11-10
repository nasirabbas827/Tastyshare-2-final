from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("", views.index_view, name="index"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("logout/", views.logout_view, name="logout"),
    path('profile/', views.profile_view, name='profile'),
    path('delete-account/', views.delete_account_view, name='delete_account'),
    path("recipes/", views.recipe_list, name="recipe_list"),
    path("recipes/add/", views.recipe_create, name="recipe_create"),
    path("recipes/<int:pk>/edit/", views.recipe_update, name="recipe_update"),
    path("recipes/<int:pk>/delete/", views.recipe_delete, name="recipe_delete"),
    path("favorites/add/<int:recipe_id>/", views.add_favorite, name="add_favorite"),
    path("favorites/remove/<int:recipe_id>/", views.remove_favorite, name="remove_favorite"),
    path("recipes/<int:recipe_id>/ratings/", views.ratings_view, name="ratings"),
    path("favorites/", views.favorite_list, name="favorite_list"),
    path('about/', views.about_us_view, name='about_us'),
    path('terms/', views.terms_view, name='terms'),
    path('contact/', views.contact_view, name='contact'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)