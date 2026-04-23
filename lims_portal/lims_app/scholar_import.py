import csv
import io
import shutil
from pathlib import Path

from django.conf import settings
from django.contrib.staticfiles import finders

from .models import scholarList

EXPECTED_COLUMNS = [
    "NAME",
    "ABOUT ME (BRIEF DESCRIPTION OF YOURSELF)",
    "FAVORITE PISAY MEMORY",
    "FUTURE PLANS",
    "LIKES",
    "DISLIKES",
    "MBTI",
    "EMAIL",
]


class ScholarImportError(Exception):
    """Raised when a CSV import cannot be completed."""


def normalize_column_name(name):
    return " ".join((name or "").strip().upper().split())


def clean_value(value):
    text = (value or "").strip()
    return text if text else "-"


def ensure_placeholder_image():
    media_dir = Path(settings.MEDIA_ROOT)
    target_dir = media_dir / "student_photos"
    target_path = target_dir / "batcher.jpg"

    if target_path.exists():
        return "student_photos/batcher.jpg"

    source_path = finders.find("batcher.jpg")
    if not source_path:
        raise ScholarImportError(
            "Could not find static placeholder image 'batcher.jpg'. "
            "Place it inside a static directory first."
        )

    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_path, target_path)
    return "student_photos/batcher.jpg"


def _read_csv_rows(csv_source, encoding):
    if isinstance(csv_source, (str, Path)):
        csv_path = Path(csv_source).expanduser()
        if not csv_path.exists() or not csv_path.is_file():
            raise ScholarImportError(f"CSV file not found: {csv_path}")

        with csv_path.open("r", encoding=encoding, newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            return reader.fieldnames or [], list(reader)

    if not hasattr(csv_source, "read"):
        raise ScholarImportError("Invalid CSV source. Provide a path or file upload.")

    raw_content = csv_source.read()
    if isinstance(raw_content, bytes):
        try:
            text_content = raw_content.decode(encoding)
        except UnicodeDecodeError as exc:
            raise ScholarImportError(
                f"Could not decode uploaded CSV with encoding '{encoding}'."
            ) from exc
    else:
        text_content = str(raw_content)

    reader = csv.DictReader(io.StringIO(text_content))
    return reader.fieldnames or [], list(reader)


def import_scholars(csv_source, section, encoding="utf-8-sig", dry_run=False):
    valid_sections = {choice[0] for choice in scholarList._meta.get_field("section").choices}
    if section not in valid_sections:
        raise ScholarImportError(
            f"Invalid section '{section}'. Choose one of: {sorted(valid_sections)}"
        )

    actual_columns, rows = _read_csv_rows(csv_source, encoding=encoding)

    normalized_actual = [normalize_column_name(c) for c in actual_columns]
    normalized_expected = [normalize_column_name(c) for c in EXPECTED_COLUMNS]
    if normalized_actual != normalized_expected:
        raise ScholarImportError(
            "Invalid CSV columns/order.\n"
            f"Expected: {EXPECTED_COLUMNS}\n"
            f"Found: {actual_columns}"
        )

    placeholder_image_relpath = "student_photos/batcher.jpg"
    if not dry_run:
        placeholder_image_relpath = ensure_placeholder_image()

    created = 0
    updated = 0
    skipped_blank = 0

    for row in rows:
        if not any((value or "").strip() for value in row.values()):
            skipped_blank += 1
            continue

        name = clean_value(row.get(EXPECTED_COLUMNS[0]))
        description = clean_value(row.get(EXPECTED_COLUMNS[1]))
        favorite_memory = clean_value(row.get(EXPECTED_COLUMNS[2]))
        future_plans = clean_value(row.get(EXPECTED_COLUMNS[3]))
        likes = clean_value(row.get(EXPECTED_COLUMNS[4]))
        dislikes = clean_value(row.get(EXPECTED_COLUMNS[5]))
        mbti = clean_value(row.get(EXPECTED_COLUMNS[6]))
        email = clean_value(row.get(EXPECTED_COLUMNS[7]))

        if dry_run:
            exists = scholarList.objects.filter(name=name, section=section).exists()
            if exists:
                updated += 1
            else:
                created += 1
            continue

        defaults = {
            "description": description,
            "favorite_memory": favorite_memory,
            "future_plans": future_plans,
            "likes": likes,
            "dislikes": dislikes,
            "mbti": mbti,
            "email": email,
            "image": placeholder_image_relpath,
        }

        existing = scholarList.objects.filter(name=name, section=section).order_by("id").first()
        if existing:
            for key, value in defaults.items():
                setattr(existing, key, value)
            existing.save()
            updated += 1
        else:
            scholarList.objects.create(name=name, section=section, **defaults)
            created += 1

    return {
        "created": created,
        "updated": updated,
        "skipped_blank": skipped_blank,
    }
