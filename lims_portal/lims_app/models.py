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
    image = models.ImageField(upload_to='student_photos', help_text="Student's photo")
    graduation_year = models.IntegerField(default=2026)
    favorite_memory = models.TextField(max_length=500, blank=True, help_text="Favorite school memory")
    future_plans = models.CharField(max_length=200, blank=True, help_text="Plans after graduation")
    
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