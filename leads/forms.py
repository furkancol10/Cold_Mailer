"""Lead ekleme/düzenleme formu ve CSV yükleme formu."""

from django import forms
from .models import Lead


class LeadForm(forms.ModelForm):
    """Tek bir lead eklemek veya düzenlemek için form."""

    class Meta:
        model = Lead
        fields = ["first_name", "last_name", "email", "company", "position", "notes"]
        labels = {
            "first_name": "Ad",
            "last_name": "Soyad",
            "email": "E-posta",
            "company": "Şirket",
            "position": "Pozisyon",
            "notes": "Notlar",
        }
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "input-field", "placeholder": "Ahmet"}),
            "last_name": forms.TextInput(attrs={"class": "input-field", "placeholder": "Yılmaz"}),
            "email": forms.EmailInput(attrs={"class": "input-field", "placeholder": "ahmet@sirket.com"}),
            "company": forms.TextInput(attrs={"class": "input-field", "placeholder": "Şirket Adı"}),
            "position": forms.TextInput(attrs={"class": "input-field", "placeholder": "CEO, Pazarlama Müdürü..."}),
            "notes": forms.Textarea(attrs={"class": "input-field", "rows": 3, "placeholder": "AI'a iletilecek ek bilgiler..."}),
        }


class CSVUploadForm(forms.Form):
    """CSV dosyası yükleme formu."""

    csv_file = forms.FileField(
        label="CSV Dosyası",
        help_text="Sütunlar: first_name, last_name, email, company, position, notes",
    )

    def clean_csv_file(self):
        dosya = self.cleaned_data["csv_file"]

        # Sadece .csv uzantısı kabul et
        if not dosya.name.endswith(".csv"):
            raise forms.ValidationError("Lütfen .csv uzantılı bir dosya yükleyin.")

        # 5MB boyut sınırı
        if dosya.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Dosya boyutu 5MB'ı aşamaz.")

        return dosya
