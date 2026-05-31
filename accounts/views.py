"""accounts uygulaması view'ları: ana sayfa ve dashboard."""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def home(request):
    """Giriş yapılmamış kullanıcılar için landing page."""
    # Zaten giriş yapılmışsa dashboard'a yönlendir
    if request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect("dashboard")
    return render(request, "home.html")


@login_required
def dashboard(request):
    """Kullanıcı paneli — özet istatistikler."""
    from campaigns.models import Campaign
    from leads.models import Lead
    from emails.models import GeneratedEmail

    # Kullanıcıya ait temel istatistikler
    context = {
        "total_leads": Lead.objects.filter(user=request.user).count(),
        "total_campaigns": Campaign.objects.filter(user=request.user).count(),
        "active_campaigns": Campaign.objects.filter(
            user=request.user, status=Campaign.Status.ACTIVE
        ).count(),
        "emails_sent": GeneratedEmail.objects.filter(
            campaign__user=request.user, status=GeneratedEmail.Status.SENT
        ).count(),
        "emails_opened": GeneratedEmail.objects.filter(
            campaign__user=request.user, status=GeneratedEmail.Status.OPENED
        ).count(),
        "recent_campaigns": Campaign.objects.filter(user=request.user)[:5],
    }
    return render(request, "dashboard.html", context)
