from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Ai)
admin.site.register(AiComment)
admin.site.register(Keyword)
admin.site.register(AiRating)
admin.site.register(AiLike)
admin.site.register(AiInfo)