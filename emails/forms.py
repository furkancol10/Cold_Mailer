"""Üretilmiş e-mail düzenleme formu."""

from django import forms

from .models import GeneratedEmail


class GeneratedEmailForm(forms.ModelForm):
    """AI tarafından yazılmış maili kullanıcının düzenlemesine izin verir."""

    class Meta:
        model = GeneratedEmail
        fields = ["subject", "body"]
        labels = {
            "subject": "Konu",
            "body": "Mail İçeriği",
        }
        widgets = {
            "subject": forms.TextInput(attrs={
                "class": "w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500",
                "placeholder": "E-mail konusu...",
            }),
            "body": forms.Textarea(attrs={
                "class": "w-full border border-gray-300 rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-indigo-500",
                "rows": 16,
            }),
        }
