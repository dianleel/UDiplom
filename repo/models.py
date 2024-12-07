from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class University(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Universities'


class Faculty(models.Model):
    name = models.CharField(max_length=200)
    university = models.ForeignKey(University, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Faculties'


class Specialty(models.Model):
    name = models.CharField(max_length=200)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Specialties'


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Publication(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes_count = models.IntegerField(default=0)
    views_count = models.IntegerField(default=0)
    type = models.CharField(max_length=10, choices=[('news', 'News'), ('work', 'Work')])

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.type}: {self.title}"


class News(models.Model):
    publication = models.OneToOneField(Publication, on_delete=models.CASCADE, primary_key=True)
    image = models.ImageField(upload_to='news_images/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not hasattr(self, 'publication'):
            self.publication = Publication.objects.create(
                title=getattr(self, '_title', ''),
                content=getattr(self, '_content', ''),
                author=getattr(self, '_author', None),
                type='news'
            )
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'News'

    def __str__(self):
        return self.publication.title


class Work(models.Model):
    publication = models.OneToOneField(Publication, on_delete=models.CASCADE, primary_key=True)
    university = models.ForeignKey(University, on_delete=models.SET_NULL, null=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True)
    specialty = models.ForeignKey(Specialty, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField(Tag)
    dislikes_count = models.IntegerField(default=0)
    file = models.FileField(upload_to='works/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not hasattr(self, 'publication'):
            self.publication = Publication.objects.create(
                title=getattr(self, '_title', ''),
                content=getattr(self, '_content', ''),
                author=getattr(self, '_author', None),
                type='work'
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.publication.title


class Comment(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Comment by {self.author.username} on {self.publication.title}'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    status = models.CharField(max_length=200, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    university = models.ForeignKey(University, on_delete=models.SET_NULL, null=True, blank=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True)
    specialty = models.ForeignKey(Specialty, on_delete=models.SET_NULL, null=True, blank=True)
    linkedin_url = models.URLField(max_length=200, blank=True)

    def __str__(self):
        return f'Profile for {self.user.username}'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()