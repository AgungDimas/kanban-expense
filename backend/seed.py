import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from expenses.management.commands.seed_data import run_seed

if __name__ == "__main__":
    run_seed()
