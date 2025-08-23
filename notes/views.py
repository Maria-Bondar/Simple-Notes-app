from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden

from .models import Note, Category
from .forms import NoteForm, RegisterForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import GroupForm

# Create your views here.

from django.utils import timezone
from datetime import timedelta

def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  
            login(request, user)
            return redirect('notes:notes')
    else:
        form = RegisterForm()
    return render(request, 'registration/sign_up.html', {'form': form})

@login_required(login_url="/login")
def notes(request):
    notes = Note.objects.select_related('category').filter(user=request.user)
    categories = Category.objects.all()
    
    category_id = request.GET.get("category")
    reminder_filter = request.GET.get("reminder")
    
    if category_id and category_id.isdigit():
        notes = notes.filter(category_id=int(category_id))
    
    now = timezone.now()

    if reminder_filter:
        notes = notes.exclude(reminder__isnull=True)
        if reminder_filter == "future":
            notes = notes.filter(reminder__gt=now)
        elif reminder_filter == "past":
            notes = notes.filter(reminder__lt=now)
        elif reminder_filter == "today":
            notes = notes.filter(reminder__date=now.date())
        elif reminder_filter == "week":
            week_later = now + timedelta(days=7)
            notes = notes.filter(reminder__range=(now, week_later))
        
    search_query = request.GET.get("search")
    if search_query:
        notes = notes.filter(title__icontains=search_query)

    return render(request, "notes/notes.html", {
        "notes": notes,
        "categories": categories,
        "search_query": search_query,
    })

@login_required(login_url="/login")
def note_create(request):
    if request.method == 'POST':
        form = NoteForm(request.POST, user=request.user)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            return redirect('notes:notes')
    else:
        form = NoteForm()
    return render(request, 'notes/note_create.html', {'form': form})

@login_required(login_url="/login")
def note_delete(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    if note.user != request.user:
        return HttpResponseForbidden("You cannot delete this note.")

    note.delete()
    return redirect('notes:notes')

@login_required(login_url="/login")
def note_detail(request, pk):
    note = get_object_or_404(Note, pk=pk)
    if note.group:  
        if request.user not in note.group.members.all():
            print("don't have access")
            return HttpResponseForbidden("You do not have access to this note.")
    else: 
        if note.user != request.user:
            return HttpResponseForbidden("You do not have access to this note.")
    return render(request, "notes/note_detail.html", {"note": note})

@login_required(login_url="/login")
def note_edit(request, pk):
    note = get_object_or_404(Note, pk=pk)
    
    if note.group:
        if note.user != request.user:
            return HttpResponseForbidden("You cannot edit this note.")
    else:
        if note.user != request.user:
            return HttpResponseForbidden("You cannot edit this note.")
        
    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('notes:note_detail', pk=pk)
    else:
        form = NoteForm(instance=note, user=request.user)
    return render(request, 'notes/note_edit.html', {'form': form, 'note': note})

@login_required
def group_notes(request):
    user_groups = request.user.custom_groups.all()
    notes = Note.objects.filter(group__in=user_groups)
    return render(request, 'notes/group_notes.html', {'notes': notes})

@login_required(login_url="/login")
def create_group(request):
    if request.method == "POST":
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            group.members.add(request.user)
            return redirect('notes:note_create') 
    else:
        form = GroupForm()
    return render(request, 'notes/create_group.html', {'form': form})
        