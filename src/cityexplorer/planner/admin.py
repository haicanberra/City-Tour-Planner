from django.contrib import admin
from .models import Search, Address, Marker, Path

# Register your models here.
admin.site.register(Search)
admin.site.register(Address)
admin.site.register(Marker)
admin.site.register(Path)
