from django import forms
from .models import UserRegister
from django.contrib.auth.hashers import make_password

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = UserRegister
        fields = ['full_name', 'username', 'email', 'phone', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        cleaned_data["password_hash"] = make_password(password)
        return cleaned_data


from django import forms
from .models import Recipe

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'ingredients', 'preparation_steps', 'category', 'cooking_time', 'image']

from django import forms
from .models import Rating

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating', 'review']  # Include review
        widgets = {
            'review': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your review here...'}),
        }


from django import forms
from .models import UserRegister
from django.contrib.auth.hashers import make_password, check_password

class ProfileUpdateForm(forms.ModelForm):
    current_password = forms.CharField(
        widget=forms.PasswordInput, required=False, label="Current Password"
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput, required=False, label="New Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput, required=False, label="Confirm New Password"
    )

    class Meta:
        model = UserRegister
        fields = ['full_name', 'username', 'email', 'phone']

    def clean(self):
        cleaned_data = super().clean()
        current = cleaned_data.get("current_password")
        new = cleaned_data.get("new_password")
        confirm = cleaned_data.get("confirm_password")

        if new or confirm:
            if not current:
                raise forms.ValidationError("Current password is required to change password.")
            if new != confirm:
                raise forms.ValidationError("New passwords do not match.")
        return cleaned_data
