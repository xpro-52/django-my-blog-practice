from django.shortcuts import render, Http404, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView, TemplateView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.template import RequestContext

from .models import Post, Profile
from .forms import PostForm, ProfileForm


"""
Only superuser is this blog app administrator.
Other users are anonymous.
"""

def top(request):
    superuser = User.objects.filter(is_superuser=True)
    context = {
        'published_num': Post.objects.exclude(published_date=None).count(),
        'draft_num': 0,
        'profile': None,
    }
    if (profile := Profile.objects.first()):
        context['profile'] = profile
    if request.user.is_authenticated:
        context['draft_num'] = Post.objects.all().count() - context['published_num']

    return render(request, 'top.html', context=context)


class ProfileUpdate(LoginRequiredMixin, UpdateView):
    model = Profile
    template_name = 'profile/update.html'
    form_class = ProfileForm
    success_url = reverse_lazy('blog:top')

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)


class PostListView(ListView):
    model = Post
    template_name = 'Post/list.html'
    context_object = 'Post_list'

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            queryset = queryset.exclude(published_date=None)
        return queryset


class PostDetailView(DetailView):
    model = Post
    template_name = 'Post/detail.html'
    context_object = 'Post'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.request.user.is_authenticated and self.object.published_date is None:
            self.object = None
            raise Http404("this is not public")
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'Post/form.html'
    form_class = PostForm
    success_url = reverse_lazy('blog:post-list')

    def get_form(self, form_class=None):
        return self.form_class(user=self.request.user, **self.get_form_kwargs())

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if self.request.POST.get('publish_flg') == 'on':
            self.object.publish()
        self.object.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = 'Post/form.html'
    form_class = PostForm

    def get_form(self, form_class=None):
        return self.form_class(user=self.request.user, **self.get_form_kwargs())

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if self.request.POST.get('publish_flg'):
            self.object.publish()
        else:
            self.object.private()
        self.object.save()
        return super().form_valid(form)
    
    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)

    def get_success_url(self):
        self.success_url = reverse('blog:post-detail', kwargs={'pk': self.kwargs['pk']})
        return super().get_success_url()


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'Post/delete.html'
    success_url = reverse_lazy('blog:post-list')
