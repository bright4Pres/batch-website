from django import forms
from django.contrib import admin, messages
from django.shortcuts import redirect, render
from django.urls import path, reverse
from .models import scholarList, commenter, PrivateMessage
from .scholar_import import EXPECTED_COLUMNS, ScholarImportError, import_scholars


class ScholarCsvImportForm(forms.Form):
    section = forms.ChoiceField(choices=scholarList._meta.get_field("section").choices)
    csv_file = forms.FileField(help_text="Upload a CSV file with the exact required column order.")
    dry_run = forms.BooleanField(
        required=False,
        initial=False,
        help_text="Validate the file and preview counts without saving data.",
    )

# Register your models here.
@admin.register(scholarList)
class scholarListAdmin(admin.ModelAdmin):
    list_display = ('name', 'section', 'mbti', 'email', 'image')
    search_fields = ('name', 'section', 'mbti', 'email')
    change_list_template = 'admin/lims_app/scholarlist/change_list.html'

    def get_urls(self):
        urls = super().get_urls()
        opts = self.model._meta
        custom_urls = [
            path(
                'import-csv/',
                self.admin_site.admin_view(self.import_csv_view),
                name=f'{opts.app_label}_{opts.model_name}_import_csv',
            )
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        opts = self.model._meta
        extra_context['import_csv_url'] = reverse(
            f'admin:{opts.app_label}_{opts.model_name}_import_csv'
        )
        return super().changelist_view(request, extra_context=extra_context)

    def import_csv_view(self, request):
        if not self.has_change_permission(request):
            self.message_user(
                request,
                'You do not have permission to import CSV data.',
                level=messages.ERROR,
            )
            return redirect('..')

        if request.method == 'POST':
            form = ScholarCsvImportForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    result = import_scholars(
                        csv_source=form.cleaned_data['csv_file'],
                        section=form.cleaned_data['section'],
                        dry_run=form.cleaned_data['dry_run'],
                    )
                except ScholarImportError as exc:
                    self.message_user(request, str(exc), level=messages.ERROR)
                except Exception as exc:
                    self.message_user(request, f'Import failed: {exc}', level=messages.ERROR)
                else:
                    mode = 'DRY RUN' if form.cleaned_data['dry_run'] else 'IMPORTED'
                    self.message_user(
                        request,
                        (
                            f"{mode}: created={result['created']}, updated={result['updated']}, "
                            f"skipped_blank={result['skipped_blank']}"
                        ),
                        level=messages.SUCCESS,
                    )
                    if not form.cleaned_data['dry_run']:
                        return redirect('..')
        else:
            form = ScholarCsvImportForm()

        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'form': form,
            'title': 'Import scholars from CSV',
            'expected_columns': EXPECTED_COLUMNS,
        }
        return render(request, 'admin/lims_app/scholarlist/import_csv.html', context)

@admin.register(commenter)
class commenterAdmin(admin.ModelAdmin):
    list_display = ('username', 'comment', 'targetScholar', 'created_at')

@admin.register(PrivateMessage)
class PrivateMessageAdmin(admin.ModelAdmin):
    list_display = ('sender_name', 'targetScholar', 'message', 'created_at', 'is_read')
    list_filter = ('is_read', 'targetScholar')
    search_fields = ('sender_name', 'targetScholar', 'message')