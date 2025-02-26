from django.contrib import admin
from .models import User  # Or `User` if using the default Django user model

admin.site.register(User)
