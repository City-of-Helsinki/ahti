import logging
import sys

from django.core.management.base import BaseCommand

from features.importers.registry import importers

logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Import features using the configured importers"

    def add_arguments(self, parser):
        parser.add_argument(
            "-s", "--single", help="Run a single importer with identifier"
        )
        parser.add_argument(
            "-l",
            "--list",
            action="store_true",
            help="List all the configured importer identifiers",
        )

    def handle(self, *args, **options):
        single_importer = options["single"]
        list_importers = options["list"]
        enabled_importers = importers.registry.items()

        if list_importers:
            self.stdout.write(self.style.SUCCESS("Enabled importers are:"))
            for identifier, _ in enabled_importers:
                self.stdout.write(f"- {identifier}")
            return
        if single_importer:
            if single_importer not in importers.registry:
                self.stderr.write(
                    self.style.ERROR(f"{single_importer} is not a configured importer.")
                )
                sys.exit(1)

            enabled_importers = filter(
                lambda values: values[0] == single_importer, enabled_importers,
            )

        for identifier, importer_class in enabled_importers:
            self.stdout.write(self.style.SUCCESS(f"Importing {identifier}"))
            try:
                importer_class().import_features()
            except Exception:
                message = f"Importer {importer_class} failed to import data"
                logging.exception(message)
                self.stderr.write(self.style.ERROR(message))

        self.stdout.write(self.style.SUCCESS("Feature importers completed"))
