from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "Battlegrounds Admin"
admin.site.site_title = "Battlegrounds Admin Panel"
admin.site.index_title = "Welcome to Battlegrounds Admin Panel"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('djrichtextfield/', include('djrichtextfield.urls')),

    path('', include('tournament.urls')),
    path('', include('accounts.urls')),
    path('profile/', include('userprofile.urls')),
    path('accounts/', include('allauth.urls')),
    path('tournament/scrims/', include("scrims.urls")),
]

handler404 = 'battleground.views.error_404_view'
handler500 = 'battleground.views.error_500_view'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)