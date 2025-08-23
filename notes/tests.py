# Create your tests here.
from django.test import TestCase, Client
from django.urls import reverse
from .models import Note, Category
from django.utils import timezone
from datetime import timedelta

class NoteViewsTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category")
        self.note = Note.objects.create(
            title="Test Note",
            description="This is a test note",
            reminder=timezone.now() + timedelta(days=1),
            category=self.category
        )
        self.client = Client()

    def test_note_create_view(self):
        url = reverse('notes:note_create')
        data = {
            'title': 'New Note',
            'description': 'Note description',
            'reminder': (timezone.now() + timedelta(days=2)).isoformat(),
            'category': self.category.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # має бути редирект після створення
        self.assertTrue(Note.objects.filter(title='New Note').exists())

    def test_note_edit_view_get(self):
        url = reverse('notes:note_edit', args=[self.note.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Note")

    def test_note_edit_view_post(self):
        url = reverse('notes:note_edit', args=[self.note.pk])
        new_title = "Updated Note"
        data = {
            'title': new_title,
            'description': self.note.description,
            'reminder': self.note.reminder.isoformat(),
            'category': self.category.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, new_title)

    def test_note_delete_view(self):
        url = reverse('notes:note_delete', args=[self.note.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())