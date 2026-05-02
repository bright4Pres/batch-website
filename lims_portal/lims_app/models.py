from django.db import models
from django.utils import timezone

# Create your models here.
sectionChoice = (
    ("Einstein", "Einstein"),
    ("Tesla", "Tesla"),
    ("Curie", "Curie")
)

class scholarList(models.Model):
    name = models.CharField(max_length=100, help_text="Student's full name")
    description = models.TextField(max_length=1000, help_text="Personal message, achievements, or memories")
    section = models.CharField(max_length=50, choices=sectionChoice, help_text="Student's section")
    image = models.ImageField(upload_to='student_photos', default='student_photos/batcher.jpg', help_text="Student's photo")
    email = models.EmailField(blank=True, help_text="Student's email (for receiving private messages)")
    graduation_year = models.IntegerField(default=2026)
    favorite_memory = models.TextField(max_length=1000, blank=True, help_text="Favorite school memory")
    future_plans = models.CharField(max_length=1000, blank=True, help_text="Plans after graduation")
    likes = models.TextField(max_length=1000, blank=True, default='-', help_text="Things the student likes")
    dislikes = models.TextField(max_length=1000, blank=True, default='-', help_text="Things the student dislikes")
    mbti = models.CharField(max_length=10, blank=True, default='-', help_text="Student's MBTI")
    
    def __str__(self):
        return f"{self.name} - {self.section}"
    
    class Meta:
        verbose_name = "Batch 2026 Student"
        verbose_name_plural = "Batch 2026 Students"
        ordering = ['section', 'name']

class commenter(models.Model):
    username = models.CharField(max_length=50)
    comment = models.TextField(max_length=500, help_text="Share your thoughts or memories")
    targetScholar = models.CharField(max_length=100, help_text="Student this comment is for")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.username} -> {self.targetScholar}"
    
    class Meta:
        verbose_name = "Student Comment"
        verbose_name_plural = "Student Comments"
        ordering = ['-created_at']

class PrivateMessage(models.Model):
    sender_name = models.CharField(max_length=100, help_text="Your name")
    sender_email = models.EmailField(blank=True, help_text="Your email (optional, for replies)")
    message = models.TextField(max_length=2000, help_text="Your private message")
    targetScholar = models.CharField(max_length=100, help_text="Student this message is for")
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"[Private] {self.sender_name} -> {self.targetScholar}"

    class Meta:
        verbose_name = "Private Message"
        verbose_name_plural = "Private Messages"
        ordering = ['-created_at']