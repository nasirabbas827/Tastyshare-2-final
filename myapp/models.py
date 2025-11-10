from django.db import models
from django.utils import timezone

class UserRegister(models.Model):
    user_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=100)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    password_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.username


from django.db import models
from django.utils import timezone

class Recipe(models.Model):
    CATEGORY_CHOICES = [
        ('Vegetarian', 'Vegetarian'),
        ('Vegan', 'Vegan'),
        ('Non-Vegetarian', 'Non-Vegetarian'),
        ('Desserts', 'Desserts'),
        ('Snacks', 'Snacks'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    recipe_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserRegister, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    ingredients = models.TextField()
    preparation_steps = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    cooking_time = models.IntegerField()
    image = models.ImageField(upload_to="recipes/", blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.status})"



from django.db import models
from django.utils import timezone

class Rating(models.Model):
    rating_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserRegister, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    review = models.TextField(blank=True, null=True)  # New review field
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.recipe.title} - {self.rating}"


class Favorite(models.Model):
    favorite_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserRegister, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} -> {self.recipe.title}"
