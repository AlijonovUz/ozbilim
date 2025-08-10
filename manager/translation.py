from modeltranslation.translator import register, TranslationOptions

from .models import Article


@register(Article)
class ArticleTranslation(TranslationOptions):
    fields = ('title', 'content')