from django import forms
from django.contrib.auth.models import User
from .models import Profile, Message, Post, Comment
from django.core.exceptions import ValidationError

# 1. Register Form (Account အသစ်ဖွင့်ရန်)
class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email (Optional)'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

# 2. User Update Form (Username နှင့် Email ပြင်ရန်)
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

# 3. Profile Update Form (Photo, Bio နှင့် Talk ID ပြင်ရန်)
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_pic', 'bio', 'talk_id']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Write something about yourself...'}),
            'profile_pic': forms.FileInput(attrs={'class': 'form-control'}),
            'talk_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Unique ID'}),
        }

# 4. Post Form (Post တင်ရန်)
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': "What's on your mind?"}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

# 5. Comment Form (Comment ရေးရန်)
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Write a comment...'}),
        }

# 6. Message Form (Chat အတွက်)
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content', 'image', 'voice_note']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 1,
                'placeholder': 'Type a message...',
                'id': 'chat-message-input'
            }),
            'image': forms.FileInput(attrs={'class': 'form-control', 'id': 'chat-image-input'}),
            'voice_note': forms.FileInput(attrs={'class': 'hidden', 'id': 'chat-voice-input'}),
        }

    # ပုံ သို့မဟုတ် စာ သို့မဟုတ် voice note တစ်ခုခုပါမှ ပို့လို့ရအောင် စစ်ဆေးခြင်း
    def clean(self):
        cleaned_data = super().clean()
        content = cleaned_data.get('content')
        image = cleaned_data.get('image')
        voice_note = cleaned_data.get('voice_note')

        if not content and not image and not voice_note:
            raise ValidationError("You cannot send an empty message.")
        return cleaned_data