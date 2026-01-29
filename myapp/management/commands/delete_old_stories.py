from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from myapp.models import Story # myapp နေရာတွင် သင့် app အမည်ကို ပြောင်းပါ

class Command(BaseCommand):
    help = 'Deletes stories older than 6 hours'

    def handle(self, *args, **options):
        expiry_time = timezone.now() - timedelta(hours=6)
        old_stories = Story.objects.filter(created_at__lt=expiry_time)
        count = old_stories.count()
        old_stories.delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} old stories.'))