"""Kampanya oluşturma/düzenleme formu."""

from django import forms

from leads.models import Lead

from .models import Campaign


class CampaignForm(forms.ModelForm):
    """Yeni kampanya veya mevcut kampanyayı düzenlemek için form."""

    # Lead seçimi: sadece bu kullanıcının lead'leri gösterilir
    leads = forms.ModelMultipleChoiceField(
        queryset=Lead.objects.none(),
        widget=forms.CheckboxSelectMultiple(),
        label="Lead'ler",
        required=False,
        help_text="Kampanyaya dahil edilecek lead'leri seçin.",
    )

    class Meta:
        model = Campaign
        fields = [
            "name",
            "description",
            "service_description",
            "prompt_template",
            "leads",
            "scheduled_at",
            "daily_limit",
        ]
        labels = {
            "name": "Kampanya Adı",
            "description": "Açıklama",
            "service_description": "Hizmet Açıklaması",
            "prompt_template": "AI Prompt Şablonu",
            "scheduled_at": "Zamanlanmış Gönderim (opsiyonel)",
            "daily_limit": "Günlük Gönderim Limiti",
        }
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500",
                "placeholder": "Örn: Kasım 2024 SaaS Kampanyası",
            }),
            "description": forms.Textarea(attrs={
                "class": "w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500",
                "rows": 2,
                "placeholder": "Kampanya hakkında kısa açıklama (opsiyonel)...",
            }),
            "service_description": forms.Textarea(attrs={
                "class": "w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500",
                "rows": 4,
                "placeholder": "Sunduğunuz hizmet veya ürünü açıklayın. AI bu bilgiyi kullanarak kişiselleştirilmiş mail yazar.",
            }),
            "prompt_template": forms.Textarea(attrs={
                "class": "w-full border border-gray-300 rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-indigo-500",
                "rows": 10,
            }),
            "scheduled_at": forms.DateTimeInput(attrs={
                "class": "w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500",
                "type": "datetime-local",
            }),
            "daily_limit": forms.NumberInput(attrs={
                "class": "w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500",
                "min": 1,
                "max": 200,
            }),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Sadece bu kullanıcının abonelikten çıkmamış lead'lerini göster
        self.fields["leads"].queryset = Lead.objects.filter(
            user=user, is_unsubscribed=False
        ).order_by("first_name", "last_name")
