from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect

from .models import (
    News, Work, Profile, Faculty,
    Specialty, University, Tag, Comment
)
from .forms import CustomUserCreationForm


class NewsListView(ListView):
    model = News
    template_name = 'news.html'
    context_object_name = 'news_list'
    paginate_by = 10

    def get_queryset(self):
        # Используем select_related для оптимизации запросов
        queryset = News.objects.select_related('publication')
        sort_by = self.request.GET.get('sort', 'date')

        if sort_by == 'likes':
            queryset = queryset.order_by('-publication__likes_count')
        elif sort_by == 'views':
            queryset = queryset.order_by('-publication__views_count')
        else:
            queryset = queryset.order_by('-publication__created_at')

        return queryset


class WorksListView(ListView):
    model = Work
    template_name = 'works.html'
    context_object_name = 'works_list'
    paginate_by = 10

    def get_queryset(self):
        # Используем select_related для оптимизации запросов
        queryset = Work.objects.select_related('publication', 'university', 'faculty', 'specialty')

        # Сортировка
        sort_by = self.request.GET.get('sort', 'date')
        if sort_by == 'likes':
            queryset = queryset.order_by('-publication__likes_count')
        elif sort_by == 'views':
            queryset = queryset.order_by('-publication__views_count')
        else:
            queryset = queryset.order_by('-publication__created_at')

        # Фильтрация
        filters = {}
        for field in ['university', 'faculty', 'specialty']:
            value = self.request.GET.get(field)
            if value:
                filters[f'{field}_id'] = value

        if filters:
            queryset = queryset.filter(**filters)

        # Фильтрация по тегу
        tag = self.request.GET.get('tag')
        if tag:
            queryset = queryset.filter(tags__name=tag)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'universities': University.objects.all(),
            'faculties': Faculty.objects.all(),
            'specialties': Specialty.objects.all(),
            'tags': Tag.objects.all(),
        })
        return context


class WorkCreateView(LoginRequiredMixin, CreateView):
    model = Work
    template_name = 'work_form.html'
    fields = ['title', 'description', 'file', 'university', 'faculty', 'specialty', 'tags']
    success_url = reverse_lazy('my_activity')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class WorkUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Work
    template_name = 'work_form.html'
    fields = ['title', 'description', 'file', 'university', 'faculty', 'specialty', 'tags']
    success_url = reverse_lazy('my_activity')

    def test_func(self):
        work = self.get_object()
        return work.author == self.request.user


class WorkDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Work
    success_url = reverse_lazy('my_activity')
    template_name = 'work_confirm_delete.html'

    def test_func(self):
        work = self.get_object()
        return work.author == self.request.user


class NewsCreateView(LoginRequiredMixin, CreateView):
    model = News
    template_name = 'news_form.html'
    fields = ['title', 'description', 'image']
    success_url = reverse_lazy('my_activity')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class NewsUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = News
    template_name = 'news_form.html'
    fields = ['title', 'description', 'image']
    success_url = reverse_lazy('my_activity')

    def test_func(self):
        news = self.get_object()
        return news.author == self.request.user


class NewsDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = News
    success_url = reverse_lazy('my_activity')
    template_name = 'news_confirm_delete.html'

    def test_func(self):
        news = self.get_object()
        return news.author == self.request.user


class MyActivityView(LoginRequiredMixin, TemplateView):
    template_name = 'my_activity.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context.update({
            'news_list': News.objects.filter(author=user).order_by('-created_at')[:5],
            'works_list': Work.objects.filter(author=user).order_by('-created_at')[:5],
            'comments_list': Comment.objects.filter(author=user).order_by('-created_at')[:5],
        })
        return context


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('news')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class ProfileView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'profile.html'
    context_object_name = 'profile'

    def get_object(self):
        return self.request.user.profile


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    template_name = 'profile_edit.html'
    fields = ['photo', 'status', 'birth_date', 'university',
              'faculty', 'specialty', 'linkedin_url']
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user.profile