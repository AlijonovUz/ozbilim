import requests

from django.contrib.auth import logout, update_session_auth_hash, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext as _
from django.views.generic import DetailView
from django.contrib import messages
from django.views import View

from bot.models import LoginCode
from manager.mixins import LoginNoRequiredMixin
from manager.models import *

from .utils import *
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


class LoginPageView(LoginNoRequiredMixin, View):
    template_name = 'registration/register.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        code = request.POST.get('code')

        if not code.isdigit() or len(code) != 6:
            return redirect('login')

        try:
            login_code = LoginCode.objects.get(code=code)
        except LoginCode.DoesNotExist:
            messages.error(request, _("Kod noto'g'ri yoki eskirgan!"))
            return redirect('login')

        if login_code.is_expired():
            messages.error(request, _("Kirish kodining muddati tugagan!"))
            return redirect('login')

        try:
            user = MyUser.objects.get(telegram_id=login_code.chat_id)
            logout_other_devices(user)
            login(request, user)
            login_code.delete()

            messages.success(request, _("Siz tizimga muvaffaqiyatli kirdingiz!"))
            return redirect('home')

        except MyUser.DoesNotExist:
            response = getChat(login_code.chat_id)['result']

            username = response.get('username', f"user_{login_code.chat_id}")
            first_name = response.get('first_name', '')
            last_name = response.get('last_name', '')
            about = response.get('bio', '')

            if response is None:
                messages.error(request, _("Telegram bilan aloqa o'rnatilmadi."))
                return redirect('login')

            user = MyUser.objects.create(
                username=username,
                first_name=first_name,
                last_name=last_name,
                about=about[:70],
                telegram_id=login_code.chat_id
            )
            user.set_unusable_password()

            if 'photo' in response:
                file_id = response['photo']['big_file_id']
                image = download_telegram_profile_photo(file_id,f"{response['username']}_avatar.jpg")
                user.avatar.save(image.name, image)

            user.save()

            login_code.delete()
            login(request, user)
            messages.success(request, _("Siz ro'yxatdan o'tdingiz va tizimga kirdingiz."))
            return redirect('home')


class LogoutView(LoginRequiredMixin, View):

    def get(self, request):
        logout(request)
        messages.success(self.request, _("Siz tizimdan muvaffaqiyatli chiqdingiz!"))
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
                messages.success(request, _("Ma'lumotlar muvaffaqiyatli saqlandi."))
                return redirect('settings')

        elif 'submit_avatar' in post:
            profile_form = ProfileUpdateForm(instance=user)
            avatar_form = AvatarUpdateForm(data=post, files=request.FILES, instance=user)
            password_form = PasswordForm(user=user)

            if avatar_form.is_valid():
                avatar_form.save()
                messages.success(request, _("Profil rasmi yangilandi."))
                return redirect('settings')

        elif 'remove_avatar' in post:
            if user.avatar:
                user.avatar.delete(save=True)
                messages.success(request, _("Profil rasmi o'chirildi."))
            return redirect('settings')

        elif 'submit_password' in post:
            profile_form = ProfileUpdateForm(instance=user)
            avatar_form = AvatarUpdateForm(instance=user)
            password_form = PasswordForm(user=user, data=post)

            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, _("Parolingiz muvaffaqiyatli yangilandi."))
                return redirect('settings')

        elif 'submit_delete' in post:
            user.delete()
            messages.success(request, _("Hisobingiz muvaffaqiyatli o'chirildi."))
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
