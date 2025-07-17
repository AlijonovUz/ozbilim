from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.views import View

from manager.mixins import LoginNoRequiredMixin
from manager.models import *

from .utils import logout_other_devices
from .forms import *


class ProfileView(DetailView):
    model = MyUser
    template_name = 'profile.html'
    context_object_name = 'profile_user'

    def get_object(self):
        username = self.kwargs.get('username')
        return get_object_or_404(MyUser, username=username)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        articles = Article.objects.filter(author=self.get_object())

        paginator = Paginator(articles, 4)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.page(page_number)
        is_paginated = paginator.num_pages > 1

        context.update({
            'page_obj': page_obj,
            'is_paginated': is_paginated
        })
        return context


class LoginPageView(LoginView):
    form_class = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        messages.success(self.request, "Siz muvaffaqiyatli tizimga kirdingiz!")

        logout_other_devices(user)

        Notification.objects.create(
            user=user,
            title="Xush kelibsiz!",
            message="O‘zBilim saytiga xush kelibsiz. Sizni ko‘rib turganimizdan xursandmiz!",
        )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('home')


class RegisterView(LoginNoRequiredMixin, CreateView):
    model = MyUser
    form_class = RegisterForm
    success_url = reverse_lazy('login')
    template_name = 'registration/register.html'

    def form_valid(self, form):
        messages.success(self.request, "Siz muvaffaqiyatli ro'yxatdan o'tdingiz!")
        return super().form_valid(form)


class LogoutView(LoginRequiredMixin, View):

    def get(self, request):
        logout(request)
        messages.success(self.request, "Siz muvaffaqiyatli tizimdan chiqdingiz!")
        return redirect('login')


class UserSettingsView(LoginRequiredMixin, View):
    template_name = 'settings.html'

    def get(self, request):
        user = request.user

        context = {
            'profile_form': ProfileUpdateForm(instance=user),
            'avatar_form': AvatarUpdateForm(instance=user),
            'password_form': PasswordForm(user=user)
        }

        return render(request, self.template_name, context)

    def post(self, request):
        user = request.user
        post = request.POST

        if 'submit_profile' in post:
            profile_form = ProfileUpdateForm(post, instance=user)
            avatar_form = AvatarUpdateForm(instance=user)
            password_form = PasswordForm(user=user)

            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Ma'lumotlar muvaffaqiyatli saqlandi.")
                return redirect('settings')

        elif 'submit_avatar' in post:
            profile_form = ProfileUpdateForm(instance=user)
            avatar_form = AvatarUpdateForm(data=post, files=request.FILES, instance=user)
            password_form = PasswordForm(user=user)

            if avatar_form.is_valid():
                avatar_form.save()
                messages.success(request, "Profil rasmi yangilandi.")
                return redirect('settings')

        elif 'remove_avatar' in post:
            if user.avatar:
                user.avatar.delete(save=True)
                messages.success(request, "Profil rasmi o'chirildi.")
            return redirect('settings')

        elif 'submit_password' in post:
            profile_form = ProfileUpdateForm(instance=user)
            avatar_form = AvatarUpdateForm(instance=user)
            password_form = PasswordForm(user=user, data=post)

            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Parolingiz muvaffaqiyatli yangilandi.")
                return redirect('settings')

        elif 'submit_delete' in post:
            user.delete()
            messages.success(request, "Hisobingiz muvaffaqiyatli o'chirildi.")
            return redirect('home')

        else:
            profile_form = ProfileUpdateForm(instance=user)
            avatar_form = AvatarUpdateForm(instance=user)
            password_form = PasswordForm(user=user)

        context = {
            'profile_form': profile_form,
            'avatar_form': avatar_form,
            'password_form': password_form,
        }
        return render(request, self.template_name, context)
