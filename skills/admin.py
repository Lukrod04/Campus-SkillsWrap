from django.contrib import admin
from .models import Review, Session, Skill

admin.site.register([Skill, Session, Review])
