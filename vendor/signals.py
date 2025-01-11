# vendor/signals.py

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from .models import GiftCard

@receiver(pre_save, sender=GiftCard)
def generate_unique_slug(sender, instance, *args, **kwargs):
    if not instance.slug:
        slug = slugify(instance.name)
        unique_slug = slug
        num = 1
        while GiftCard.objects.filter(slug=unique_slug).exists():
            unique_slug = f'{slug}-{num}'
            num += 1
        instance.slug = unique_slug

