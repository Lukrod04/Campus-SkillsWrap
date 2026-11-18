from django import forms
from .models import Review, Skill, Session


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['title', 'category', 'description']
        widgets = {'description': forms.Textarea(attrs={'rows': 5})}
        help_texts = {'title': 'For example: Python tutoring for beginners.',
                      'category': 'For example: Coding, Music, Tutoring, or Art.',
                      'description': 'Explain what students will learn, what to bring, and the session length.'}


class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['preferred_time', 'meeting_place']
        help_texts = {'preferred_time': 'Suggest a day and time, including your time zone. Optional.',
                      'meeting_place': 'Suggest a public campus location or online meeting. Optional.'}


class ReviewForm(forms.ModelForm):
    rating = forms.TypedChoiceField(choices=[(n, f'{n} / 5') for n in range(1, 6)], coerce=int)

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {'comment': forms.Textarea(attrs={'rows': 4})}
