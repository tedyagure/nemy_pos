from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.cache import cache_page
from .views import custom_404, custom_500, custom_403

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),

    # Core app URLs
    path('', include('dashboard.urls')),  # Main dashboard as homepage
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('inventory/', include('inventory.urls', namespace='inventory')),
    path('sales/', include('sales.urls', namespace='sales')),
    path('payments/', include('payments.urls', namespace='payments')),
    path('rentals/', include('rentals.urls', namespace='rentals')),
    
    # POS and Customer Management
    path('pos/', include('pos.urls', namespace='pos')),
    path('customers/', include('customers.urls', namespace='customers')),
    path('quotations/', include('quotations.urls', namespace='quotations')),

    # API endpoints (if needed)
    path('api/v1/', include('api.urls', namespace='api')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar for development
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]

# Custom error handlers
handler404 = 'nemy_pos.views.custom_404'
handler500 = 'nemy_pos.views.custom_500'
handler403 = 'nemy_pos.views.custom_403' 