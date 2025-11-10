from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.http import HttpResponseRedirect
from .models import UserRegister
from .forms import RegisterForm

# Register
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.password_hash = form.cleaned_data['password_hash']
            user.save()
            messages.success(request, "Registration successful! Please login.")
            return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})

# Login
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = UserRegister.objects.get(username=username)
            if check_password(password, user.password_hash):
                request.session["user_id"] = user.user_id
                request.session["username"] = user.username
                return redirect("dashboard")
            else:
                messages.error(request, "Invalid password.")
        except UserRegister.DoesNotExist:
            messages.error(request, "User not found.")
    return render(request, "login.html")


# Logout
def logout_view(request):
    request.session.flush()
    return redirect("login")


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Recipe, UserRegister
from .forms import RecipeForm

# List recipes of logged-in user
def recipe_list(request):
    if not request.session.get("user_id"):
        return redirect("login")
    user_id = request.session["user_id"]
    recipes = Recipe.objects.filter(user_id=user_id)
    return render(request, "recipe_list.html", {"recipes": recipes})

# Create new recipe
def recipe_create(request):
    if not request.session.get("user_id"):
        return redirect("login")
    if request.method == "POST":
        form = RecipeForm(request.POST, request.FILES)  # include request.FILES
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.user_id = request.session["user_id"]
            recipe.save()
            messages.success(request, "Recipe added successfully.")
            return redirect("recipe_list")
    else:
        form = RecipeForm()
    return render(request, "recipe_form.html", {"form": form, "title": "Add Recipe"})


def recipe_update(request, pk):
    if not request.session.get("user_id"):
        return redirect("login")
    recipe = get_object_or_404(Recipe, pk=pk, user_id=request.session["user_id"])
    if request.method == "POST":
        form = RecipeForm(request.POST, request.FILES, instance=recipe)  # include request.FILES
        if form.is_valid():
            form.save()
            messages.success(request, "Recipe updated successfully.")
            return redirect("recipe_list")
    else:
        form = RecipeForm(instance=recipe)
    return render(request, "recipe_form.html", {"form": form, "title": "Edit Recipe"})

# Delete recipe
def recipe_delete(request, pk):
    if not request.session.get("user_id"):
        return redirect("login")
    recipe = get_object_or_404(Recipe, pk=pk, user_id=request.session["user_id"])
    if request.method == "POST":
        recipe.delete()
        messages.success(request, "Recipe deleted successfully.")
    return redirect("recipe_list")


from django.shortcuts import render, redirect
from django.db.models import Q, Count
from .models import Recipe, Favorite, Rating

def dashboard_view(request):
    if not request.session.get("user_id"):
        return redirect("index")

    user_id = request.session["user_id"]

    # Only show approved recipes
    recipes = Recipe.objects.filter(status='Approved')

    # Search & Filter
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    cooking_time = request.GET.get("cooking_time", "").strip()
    sort_by = request.GET.get("sort_by", "")  # optional sorting

    if query:
        recipes = recipes.filter(
            Q(title__icontains=query) | Q(ingredients__icontains=query)
        )

    if category:
        recipes = recipes.filter(category=category)

    if cooking_time:
        try:
            recipes = recipes.filter(cooking_time__lte=int(cooking_time))
        except ValueError:
            pass  # ignore invalid input

    # Sorting
    if sort_by == "popularity":
        recipes = recipes.annotate(num_ratings=Count('rating')).order_by('-num_ratings')
    elif sort_by == "recent":
        recipes = recipes.order_by('-created_at')
    else:
        recipes = recipes.order_by('title')  # default alphabetical

    # Favorites for current user
    favorite_recipes = Favorite.objects.filter(user_id=user_id).values_list("recipe_id", flat=True)

    return render(request, "dashboard.html", {
        "username": request.session.get("username"),
        "recipes": recipes,
        "favorite_recipes": favorite_recipes,
        "categories": Recipe.CATEGORY_CHOICES,
        "request_get": request.GET  # to retain form values
    })



# Add to favorites
def add_favorite(request, recipe_id):
    if not request.session.get("user_id"):
        return redirect("login")
    user_id = request.session["user_id"]
    Favorite.objects.get_or_create(user_id=user_id, recipe_id=recipe_id)
    return redirect("dashboard")

# Remove from favorites
def remove_favorite(request, recipe_id):
    if not request.session.get("user_id"):
        return redirect("login")
    user_id = request.session["user_id"]
    Favorite.objects.filter(user_id=user_id, recipe_id=recipe_id).delete()
    return redirect("dashboard")

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Recipe, Rating
from .forms import RatingForm

def ratings_view(request, recipe_id):
    if not request.session.get("user_id"):
        return redirect("login")

    user_id = request.session["user_id"]
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    ratings = Rating.objects.filter(recipe=recipe).select_related("user")

    # Check if the user already left a rating
    try:
        user_rating = Rating.objects.get(user_id=user_id, recipe=recipe)
    except Rating.DoesNotExist:
        user_rating = None

    if request.method == "POST":
        form = RatingForm(request.POST, instance=user_rating)
        if form.is_valid():
            rating_obj = form.save(commit=False)
            rating_obj.user_id = user_id
            rating_obj.recipe = recipe
            rating_obj.save()
            messages.success(request, "Rating submitted successfully.")

            # Send email notification to recipe owner if someone rates their recipe
            if recipe.user.email:  # Make sure recipe owner has email
                subject = f"New Review on Your Recipe: {recipe.title}"
                message = f"Hello {recipe.user.full_name},\n\n" \
                          f"{request.session.get('username')} has left a rating of {rating_obj.rating}/5" \
                          f"{' and a review' if rating_obj.review else ''} on your recipe '{recipe.title}'.\n\n" \
                          f"Check it out on your dashboard."
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipe.user.email])

            return redirect("ratings", recipe_id=recipe_id)
    else:
        form = RatingForm(instance=user_rating)

    return render(request, "ratings.html", {
        "recipe": recipe,
        "ratings": ratings,
        "form": form,
        "user_rating": user_rating,
    })



def favorite_list(request):
    if not request.session.get("user_id"):
        return redirect("login")
    user_id = request.session["user_id"]
    favorites = Recipe.objects.filter(favorite__user_id=user_id)
    return render(request, "favorites.html", {"favorites": favorites})


def about_us_view(request):
    """
    Renders the About Us page.
    """
    return render(request, 'pages/about_us.html', {'title': 'About Us'})

def terms_view(request):
    """
    Renders the Terms and Conditions page.
    """
    return render(request, 'pages/terms.html', {'title': 'Terms and Conditions'})

def contact_view(request):
    """
    Renders the Contact Us page.
    """
    # For a basic static page, you can just render the template.
    # For a functional contact form, you would add form handling logic here.
    return render(request, 'pages/contact.html', {'title': 'Contact Us'})


 
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.conf import settings
from .models import UserRegister
from .forms import ProfileUpdateForm

def profile_view(request):
    if not request.session.get("user_id"):
        return redirect("login")
    
    user = get_object_or_404(UserRegister, pk=request.session["user_id"])
    
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=user)
        if form.is_valid():
            # Update password if provided
            new_password = form.cleaned_data.get("new_password")
            current_password = form.cleaned_data.get("current_password")
            password_changed = False

            if new_password:
                if check_password(current_password, user.password_hash):
                    user.password_hash = make_password(new_password)
                    password_changed = True
                else:
                    messages.error(request, "Current password is incorrect.")
                    return redirect("profile")

            form.save()
            messages.success(request, "Profile updated successfully.")

            # Send email if password changed
            if password_changed and user.email:
                subject = "Your Password Has Been Changed"
                message = f"Hello {user.full_name},\n\nYour account password has been successfully updated.\n\n" \
                          f"If you did not perform this change, please contact support immediately."
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

            return redirect("profile")
    else:
        form = ProfileUpdateForm(instance=user)
    
    return render(request, "profile.html", {"form": form, "user": user})


def delete_account_view(request):
    if not request.session.get("user_id"):
        return redirect("login")
    user = get_object_or_404(UserRegister, pk=request.session["user_id"])
    user.delete()
    request.session.flush()
    messages.success(request, "Account deleted successfully.")
    return redirect("register")


from django.shortcuts import render
from django.db.models import Q, Count
from .models import Recipe, Favorite

def index_view(request):
    user_id = request.session.get("user_id")  # optional, for favorites

    # Only approved recipes
    recipes = Recipe.objects.filter(status='Approved')

    # Search & Filter
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    cooking_time = request.GET.get("cooking_time", "").strip()
    sort_by = request.GET.get("sort_by", "")

    if query:
        recipes = recipes.filter(
            Q(title__icontains=query) | Q(ingredients__icontains=query)
        )

    if category:
        recipes = recipes.filter(category=category)

    if cooking_time:
        try:
            recipes = recipes.filter(cooking_time__lte=int(cooking_time))
        except ValueError:
            pass

    # Sorting
    if sort_by == "popularity":
        recipes = recipes.annotate(num_ratings=Count('rating')).order_by('-num_ratings')
    elif sort_by == "recent":
        recipes = recipes.order_by('-created_at')
    else:
        recipes = recipes.order_by('title')

    # Favorites
    favorite_recipes = []
    if user_id:
        favorite_recipes = Favorite.objects.filter(user_id=user_id).values_list("recipe_id", flat=True)

    return render(request, "index.html", {
        "recipes": recipes,
        "favorite_recipes": favorite_recipes,
        "categories": Recipe.CATEGORY_CHOICES,
        "request_get": request.GET
    })
