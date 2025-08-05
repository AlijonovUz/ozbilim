import asyncio
from django.core.management.base import BaseCommand
from bot.bot import run_bot


class Command(BaseCommand):
    help = 'Aiogram telegram botni ishga tushuradi'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('✅ Bot ishga tushmoqda...'))
        asyncio.run(run_bot())