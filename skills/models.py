from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Skill(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=120)
    category = models.CharField(max_length=60)
    description = models.TextField(max_length=3000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Session(models.Model):
    preferred_time = models.CharField(max_length=120, blank=True)
    meeting_place = models.CharField(max_length=160, blank=True)
    confirmed = models.BooleanField(default=False)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='sessions')
    learner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['skill', 'learner'], name='one_session_per_learner')]


class Review(models.Model):
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(max_length=1500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['skill', 'author'], name='one_review_per_student'),
            models.CheckConstraint(condition=models.Q(rating__gte=1, rating__lte=5), name='rating_between_1_and_5'),
        ]
