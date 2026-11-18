from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import ReviewForm, SkillForm, SessionForm
from .models import Review, Session, Skill


def skill_list(request):
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    categories = Skill.objects.order_by('category').values_list('category', flat=True).distinct()
    skills = Skill.objects.select_related('owner').annotate(average_rating=Avg('reviews__rating'), review_count=Count('reviews'))
    if query:
        skills = skills.filter(Q(title__icontains=query) | Q(category__icontains=query))
    if category:
        skills = skills.filter(category__iexact=category)
    return render(request, 'skills/list.html', {'skills': skills, 'query': query, 'categories': categories, 'selected_category': category})


def register(request):
    form = UserCreationForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.save())
        return redirect('skill_list')
    return render(request, 'skills/form.html', {'form': form, 'heading': 'Join your campus community', 'submit_label': 'Create account'})


def skill_detail(request, pk):
    skill = get_object_or_404(Skill.objects.select_related('owner'), pk=pk)
    can_review = False
    session = None
    if request.user.is_authenticated:
        session = Session.objects.filter(skill=skill, learner=request.user).first()
        can_review = bool(session and session.completed and skill.owner_id != request.user.pk)
    review = Review.objects.filter(skill=skill, author=request.user).first() if request.user.is_authenticated else None
    form = ReviewForm(request.POST if request.method == 'POST' else None, instance=review)
    if request.method == 'POST':
        if not can_review:
            messages.error(request, 'Complete a session with the provider before reviewing this skill.')
            return redirect('skill_detail', pk=pk)
        if form.is_valid():
            review = form.save(commit=False)
            review.skill = skill
            review.author = request.user
            review.save()
            messages.success(request, 'Your review has been saved.')
            return redirect('skill_detail', pk=pk)
    reviews = skill.reviews.select_related('author')
    return render(request, 'skills/detail.html', {'skill': skill, 'reviews': reviews,
        'average': reviews.aggregate(value=Avg('rating'))['value'], 'form': form,
        'can_review': can_review, 'session': session, 'session_form': SessionForm()})


@login_required
def skill_create(request):
    form = SkillForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        skill = form.save(commit=False)
        skill.owner = request.user
        skill.save()
        return redirect('skill_detail', pk=skill.pk)
    return render(request, 'skills/form.html', {'form': form, 'heading': 'Share your skill', 'submit_label': 'Post skill'})


@login_required
def skill_edit(request, pk):
    skill = get_object_or_404(Skill, pk=pk, owner=request.user)
    form = SkillForm(request.POST if request.method == 'POST' else None, instance=skill)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('skill_detail', pk=pk)
    return render(request, 'skills/form.html', {'form': form, 'heading': 'Edit your skill', 'submit_label': 'Save changes'})


@login_required
def skill_delete(request, pk):
    skill = get_object_or_404(Skill, pk=pk, owner=request.user)
    if request.method == 'POST':
        skill.delete()
        return redirect('dashboard')
    return render(request, 'skills/delete.html', {'skill': skill})


@login_required
def dashboard(request):
    return render(request, 'skills/dashboard.html', {
        'skills': Skill.objects.filter(owner=request.user),
        'incoming': Session.objects.filter(skill__owner=request.user).select_related('skill', 'learner'),
        'sessions': Session.objects.filter(learner=request.user).select_related('skill'),
    })


@login_required
@require_POST
def request_session(request, pk):
    skill = get_object_or_404(Skill, pk=pk)
    if skill.owner_id != request.user.pk:
        form = SessionForm(request.POST)
        if not form.is_valid():
            return render(request, 'skills/form.html', {'form': form, 'heading': 'Request a session', 'submit_label': 'Request session'}, status=400)
        Session.objects.get_or_create(skill=skill, learner=request.user, defaults=form.cleaned_data)
        messages.success(request, 'Session requested! Your provider can confirm your proposed meeting from their dashboard.')
    return redirect('skill_detail', pk=pk)


@login_required
@require_POST
def complete_session(request, pk):
    session = get_object_or_404(Session, pk=pk, skill__owner=request.user)
    session.completed = True
    session.save(update_fields=['completed'])
    messages.success(request, 'Session marked complete. The learner can now leave a review.')
    return redirect('dashboard')


@login_required
@require_POST
def confirm_session(request, pk):
    session = get_object_or_404(Session, pk=pk, skill__owner=request.user)
    if not session.completed:
        session.confirmed = True
        session.save(update_fields=['confirmed'])
        messages.success(request, 'Meeting confirmed. The learner can see the confirmation on their dashboard.')
    return redirect('dashboard')
