from django.contrib import admin
from .models import UserRegister, Recipe, Rating, Favorite

# -------------------------
# UserAdmin
# -------------------------
@admin.register(UserRegister)
class UserRegisterAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'username', 'full_name', 'email', 'phone', 'created_at')
    search_fields = ('username', 'full_name', 'email', 'phone')
    list_filter = ('created_at',)
    ordering = ('-created_at',)


# -------------------------
# RecipeAdmin
# -------------------------
@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe_id', 'title', 'user', 'category', 'status', 'cooking_time', 'created_at')
    search_fields = ('title', 'ingredients', 'preparation_steps', 'user__username')
    list_filter = ('category', 'status', 'created_at')
    ordering = ('-created_at',)
    list_editable = ('status',)  # Allow quick status updates in admin

    # Optional: Show image in admin list view
    def image_tag(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="50" height="50" />'
        return "-"
    image_tag.allow_tags = True
    image_tag.short_description = 'Image'


# -------------------------
# RatingAdmin
# -------------------------
@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('rating_id', 'recipe', 'user', 'rating', 'review', 'created_at')
    search_fields = ('recipe__title', 'user__username', 'review')
    list_filter = ('rating', 'created_at')
    ordering = ('-created_at',)


# -------------------------
# FavoriteAdmin
# -------------------------
@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('favorite_id', 'user', 'recipe', 'created_at')
    search_fields = ('user__username', 'recipe__title')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
