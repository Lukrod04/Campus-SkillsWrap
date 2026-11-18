from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from skills.models import Skill


SAMPLE_SKILLS = [
    ('Python for beginners', 'Coding',
     'Learn variables, loops, functions, and how to write your first Python program. '
     'Bring a laptop and a small project idea. Suggested session: 45 minutes. No experience needed.'),
    ('Build your first website', 'Web Development',
     'Create a personal webpage with HTML and CSS, then learn how Bootstrap makes layouts responsive. '
     'Bring a laptop. Suggested session: 60 minutes. Great for beginners.'),
    ('Calculus study buddy', 'Tutoring',
     'Practice limits, derivatives, and introductory integrals with worked examples. '
     'Bring your notes and practice questions. Suggested session: 45 minutes. We focus on understanding, not completing graded work for you.'),
    ('Essay planning and proofreading', 'Writing',
     'Organize your argument, strengthen paragraph structure, and learn to spot common grammar mistakes. '
     'Bring an outline or draft. Suggested session: 30 minutes. You remain the author of your work.'),
    ('Guitar chords for beginners', 'Music',
     'Learn basic chords, simple strumming patterns, and how to practice your first song. '
     'Bring a guitar if you have one. Suggested session: 45 minutes. No music theory required.'),
    ('Conversational Spanish practice', 'Languages',
     'Practice introductions, campus conversations, and everyday vocabulary in a relaxed setting. '
     'Suggested session: 30 minutes. Suitable for beginners who want more speaking confidence.'),
    ('Resume and interview practice', 'Career',
     'Make your resume easier to scan and practice answering common internship interview questions. '
     'Bring a draft resume and a role you are interested in. Suggested session: 45 minutes.'),
    ('Excel essentials for students', 'Productivity',
     'Build a budget spreadsheet, use basic formulas, and turn data into a simple chart. '
     'Bring a laptop with Excel or a compatible spreadsheet app. Suggested session: 45 minutes.'),
    ('Phone photography on campus', 'Photography',
     'Explore composition, natural light, and simple editing with your phone camera. '
     'Bring a charged phone. Suggested session: a 45-minute campus photo walk. All experience levels welcome.'),
    ('Design better presentation slides', 'Design',
     'Use clear layouts, readable type, and a consistent color palette to improve a class presentation. '
     'Bring a slide deck or topic. Suggested session: 45 minutes using your preferred presentation app.'),
    ('Public speaking practice', 'Communication',
     'Rehearse a short presentation and get friendly feedback on structure, pace, and delivery. '
     'Bring a topic or a few slides. Suggested session: 30 minutes. Beginners welcome.'),
    ('Sketching everyday objects', 'Art',
     'Practice observation, basic shapes, and shading with a few everyday objects. '
     'Bring paper and a pencil. Suggested session: 45 minutes. No drawing experience needed.'),
]


SAMPLE_NAMES = [
    ('Alex', 'Morgan'), ('Priya', 'Shah'), ('Jordan', 'Lee'),
    ('Emma', 'Brooks'), ('Noah', 'Rivera'), ('Sofia', 'Martinez'),
    ('Maya', 'Patel'), ('Ethan', 'Chen'), ('Olivia', 'Reed'),
    ('Aiden', 'Park'), ('Zoe', 'Bennett'), ('Liam', 'Carter'),
]


class Command(BaseCommand):
    help = 'Add clearly labeled sample skill posts without duplicating them on repeated runs.'

    @transaction.atomic
    def handle(self, *args, **options):
        added = 0
        reassigned = 0
        for (title, category, description), (first, last) in zip(SAMPLE_SKILLS, SAMPLE_NAMES, strict=True):
            username = f'{first[:3]}{last[:5]}1'
            legacy = get_user_model().objects.filter(
                username=f'{first.lower()}_{last.lower()}_demo', is_active=False
            ).first()
            if legacy and not legacy.has_usable_password():
                # Rename the same account so skill ownership and IDs stay intact.
                legacy.username = username
                legacy.save(update_fields=['username'])
            owner, created = get_user_model().objects.get_or_create(
                username=username,
                defaults={'first_name': first, 'last_name': last, 'is_active': False},
            )
            if created:
                owner.set_unusable_password()
                owner.save(update_fields=['password'])
            elif owner.is_active or owner.has_usable_password():
                raise ValueError('A demo username belongs to an active account. No changes were saved.')

            # Move the original sample row, preserving its ID and related records.
            old_skill = Skill.objects.filter(owner__username='campus_sample_catalog', title=title,
                                             description__startswith='SAMPLE POST:').first()
            if old_skill:
                old_skill.owner = owner
                old_skill.save(update_fields=['owner'])
                reassigned += 1
            _, created = Skill.objects.get_or_create(
                owner=owner, title=title,
                defaults={
                    'category': category,
                    'description': 'SAMPLE POST: This is a demonstration skill, not a real student offering. '
                                   'Session requests for sample posts will not be fulfilled.\n\n' + description,
                },
            )
            added += int(created)
        self.stdout.write(self.style.SUCCESS(f'Added {added} sample skills; reassigned {reassigned} to named demo accounts.'))
