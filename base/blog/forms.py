from django import forms
from .models import Comment, Subscriber

class SearchForm(forms.Form):
    query = forms.CharField(label='Поиск', 
                            max_length=100, 
                            widget=forms.TextInput(
                                attrs={'placeholder': 'Поиск...'}))


class ContactForm(forms.Form):
    name = forms.CharField(label='Имя', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    subject = forms.CharField(label='Тема', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    message = forms.CharField(label='Сообщение', widget=forms.Textarea(attrs={'class': 'form-control'}))

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваше имя'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ваш email'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Введите ваш комментарий здесь'}),
        }


class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ваш email'})
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if Subscriber.objects.filter(email=email).exists():
            raise forms.ValidationError("Этот email уже подписан на рассылку.")
        return email
