from django import forms
from django.utils.translation import gettext_lazy as _

from mentors.models import Mentor
from tarot.spreads import SPREADS


class ReadingJourneyForm(forms.Form):
    mentor = forms.ModelChoiceField(label=_("Mentor"), queryset=Mentor.objects.none())
    question = forms.CharField(label=_("Your question"), max_length=1000, widget=forms.Textarea(attrs={"rows": 4}))
    reading_type = forms.ChoiceField(label=_("Spread"), choices=[])
    locale = forms.ChoiceField(label=_("Language"), choices=[("en", "English"), ("uk", "Українська")])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["reading_type"].choices = [
            (key.value, spread.name) for key, spread in SPREADS.items() if spread.is_active
        ]
        self.fields["mentor"].queryset = Mentor.objects.filter(is_active=True).order_by("name")

    def clean_question(self):
        question = self.cleaned_data["question"].strip()
        if not question:
            raise forms.ValidationError(_("Please enter a question."))
        return question
