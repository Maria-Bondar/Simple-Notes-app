from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Group(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='custom_groups')
    
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name

class Note(models.Model):
    """
    This class represents a Book.
    """
    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    reminder = models.DateTimeField(null=True, blank=True)
    
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    group = models.ForeignKey(Group, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} ({self.category})"

    @staticmethod
    def get_by_id(book_id):
        try:
            return Note.objects.get(id=book_id)
        except Note.DoesNotExist:
            return None

    @staticmethod
    def delete_by_id(note_id):
        note = Note.get_by_id(note_id)
        if note:
            note.delete()
            return True
        return False

    @staticmethod
    def create(title, description, reminder, category_name):
        if len(title) > 128:
            return None
        category, created = Category.objects.get_or_create(name=category_name)
        note = Note(title=title, description=description, reminder=reminder, category=category)
        note.save()
        return note
    
    def update(self, title=None, description=None):
        if title is not None:
            if len(title) <= 128:
                self.title = title
        if description is not None:
            self.description = description
        self.save()

    @staticmethod
    def get_all():
        return list(Note.objects.all())