from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, RedirectView, TemplateView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.utils import timezone
from django.views import View

from .mixins import ThrottlingMixin
from .models import *
from .forms import *


class HomeView(ListView):
    model = Article
    template_name = 'index.html'
    context_object_name = 'articles'
    paginate_by = 6


class SearchView(ListView):
    template_name = 'index.html'
    context_object_name = 'articles'
    paginate_by = 6

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        return (
            Article.objects.filter(
                models.Q(title__icontains=query) |
                models.Q(content__icontains=query)
            ).distinct()
        )


class ArticleDetail(DetailView):
    model = Article
    template_name = 'detail.html'
    context_object_name = 'article'

    def get(self, request, *args, **kwargs):
        article = self.get_object()
        response = super().get(request, *args, **kwargs)

        cookie_key = f"viewed_article_{article.id}"
        if not request.COOKIES.get(cookie_key):
            article.views += 1
            article.save(update_fields=['views'])

            now = timezone.now()
            response.set_cookie(
                key=cookie_key,
                value=now.isoformat(),
                max_age=3600,
                samesite='Lax',
            )

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'form': CommentForm(),
            'comments': self.object.comments.select_related('user').order_by('-created_at')
        })

        return context


class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm

    def get_success_url(self):
        return reverse_lazy('detail', args=[self.object.pk])

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)

        image_form = ArticleImageForm(data=self.request.POST, files=self.request.FILES)
        if image_form.is_valid():
            for img in self.request.FILES.getlist('images'):
                ArticleImage.objects.create(article=self.object, image=img)

        messages.success(self.request, f"Maqola muvaffaqiyatli qo'shildi.")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['image_form'] = ArticleImageForm()
        return context


class ArticleUpdateView(LoginRequiredMixin, UpdateView):
    model = Article
    form_class = ArticleForm

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        user = request.user
        if obj.author != user and not user.is_superuser:
            return redirect('detail', obj.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('detail', args=[self.object.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['image_form'] = ArticleImageForm(article=self.object)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)

        image_form = ArticleImageForm(
            data=self.request.POST,
            files=self.request.FILES,
            article=self.object
        )

        if image_form.is_valid():
            for img in self.request.FILES.getlist('images'):
                ArticleImage.objects.create(article=self.object, image=img)

            image_ids_to_delete = image_form.cleaned_data.get('delete_images', [])
            if image_ids_to_delete:
                ArticleImage.objects.filter(id__in=image_ids_to_delete, article=self.object).delete()

        messages.success(self.request, "Maqola yangilandi.")
        return response


class ArticleDeleteView(View):

    def get(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        user = request.user

        if article.author == user or user.is_superuser:
            article.delete()
            messages.success(request, "Maqola muvaffaqiyatli o'chirildi.")

            if article.author != user:
                Notification.objects.create(
                    user=article.author,
                    title="Maqola o'chirildi.",
                    message="Siz yozgan maqola administrator tomonidan o‘chirildi.",
                    link=reverse('profile', args=[user.username])
                )

            return redirect('profile', article.author.username)
        return redirect('detail', article.pk)


class CommentView(LoginRequiredMixin, ThrottlingMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'detail.html'

    throttle_timeout = 60

    def dispatch(self, request, *args, **kwargs):
        self.article = get_object_or_404(Article, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.article = self.article

        if self.article.author != self.request.user:
            Notification.objects.create(
                user=self.article.author,
                title="Yangi izoh",
                message="Sizning maqolangizga izoh yozildi.",
                link=reverse('detail', args=[self.article.pk])
            )

        messages.success(self.request, "Izohingiz muvaffaqiyatli qo'shildi!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Izoh yuborishda xatolik yuz berdi.")
        return redirect('detail', pk=self.article.pk)

    def get_success_url(self):
        return redirect('detail', pk=self.article.pk).url


class CommentDeleteView(LoginRequiredMixin, View):

    def get(self, request, article_pk, comment_pk):
        comment = get_object_or_404(Comment, pk=comment_pk)
        author = comment.article.author
        recipient = comment.user
        user = request.user

        if user in [recipient, author] or user.is_superuser:
            comment.delete()
            messages.success(request, "Izoh muvaffaqiyatli o'chirildi.")

            if recipient != user:
                Notification.objects.create(
                    user=recipient,
                    title="Izoh o‘chirildi",
                    message="Siz yozgan izoh muallif tomonidan o‘chirildi.",
                    link=reverse('detail', args=[article_pk])
                )

        return redirect('detail', article_pk)


class NotificationReadRedirectView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        notification = get_object_or_404(Notification, pk=kwargs['pk'], user=self.request.user)

        if not notification.is_read:
            notification.is_read = True
            notification.save()

        return notification.link or '/'


class ReadAllNotificationsView(View):

    def get(self, request):
        if request.user.is_authenticated:
            Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return redirect(request.META.get('HTTP_REFERER'), 'home')


class Custom404(TemplateView):
    template_name = '404.html'