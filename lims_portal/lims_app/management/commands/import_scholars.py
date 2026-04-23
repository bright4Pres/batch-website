from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from lims_app.scholar_import import ScholarImportError, import_scholars


class Command(BaseCommand):
    help = "Import scholars from a CSV file using the required batch column order."

    def add_arguments(self, parser):
        parser.add_argument("csv_file", help="Path to the CSV file to import")
        parser.add_argument(
            "--section",
            required=True,
            choices=["Einstein", "Tesla", "Curie"],
            help="Section to assign to every imported row",
        )
        parser.add_argument(
            "--encoding",
            default="utf-8-sig",
            help="CSV file encoding (default: utf-8-sig)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate and preview import without writing to the database",
        )

    def handle(self, *args, **options):
        csv_path = Path(options["csv_file"]).expanduser()
        if not csv_path.is_absolute():
            csv_path = Path.cwd() / csv_path

        if not csv_path.exists() or not csv_path.is_file():
            raise CommandError(f"CSV file not found: {csv_path}")

        section = options["section"]
        encoding = options["encoding"]
        dry_run = options["dry_run"]

        try:
            result = import_scholars(
                csv_source=csv_path,
                section=section,
                encoding=encoding,
                dry_run=dry_run,
            )
        except ScholarImportError as exc:
            raise CommandError(str(exc)) from exc

        if result["skipped_blank"]:
            self.stdout.write(
                self.style.WARNING(f"Skipped blank rows: {result['skipped_blank']}")
            )

        mode = "DRY RUN" if dry_run else "IMPORTED"
        self.stdout.write(
            self.style.SUCCESS(
                f"{mode}: created={result['created']}, updated={result['updated']}"
            )
        )
