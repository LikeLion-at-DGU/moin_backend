from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Suggestion)
admin.site.register(SuggestionComment)
admin.site.register(SuggestionImage)