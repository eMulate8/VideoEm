from django import forms
from django.utils.text import slugify
from django.utils.timezone import now

from .models import Video, Tag


def unique_slugify(instance, slug, max_length=255):
    """
    Generate a unique slug for the given instance.
    If the slug already exists, append a counter to make it unique.
    """
    model_class = instance.__class__
    original_slug = slug[:max_length]
    queryset = model_class.objects.filter(video_slug=original_slug).exclude(pk=instance.pk)
    counter = 1

    while queryset.exists():
        slug = f"{original_slug}-{counter}"
        queryset = model_class.objects.filter(video_slug=slug).exclude(pk=instance.pk)
        counter += 1

    return slug[:max_length]


class EditVideoForm(forms.ModelForm):
    """
    Form for editing uploaded video.
    The title can be edited only once.
    """
    class Meta:
        model = Video

        fields = ['title', 'is_published', 'description', 'tags']

        widgets = {
            'title': forms.TextInput(attrs={'style': 'width: 100%;'}),
            'description': forms.Textarea(attrs={'style': 'width: 100%;'}),
        }

        tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all())

    def __init__(self, *args, **kwargs):

        if kwargs.get('instance'):
            initial = kwargs.setdefault('initial', {})
            initial['tags'] = [t.pk for t in kwargs['instance'].tags.all()]

        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            if self.instance.title:
                self.fields['title'] = forms.CharField(
                    initial=self.instance.title,
                    disabled=True,
                    widget=forms.TextInput(attrs={'readonly': 'readonly'})
                )

        for field in self.fields:
            self.fields[field].required = False

    def save(self, commit=True):

        instance = super().save(commit=False)

        if 'title' in self.fields and self.fields['title'].disabled:
            instance.title = self.instance.title

        if instance.title:
            if not instance.video_slug:
                slug = slugify(instance.title)
                instance.video_slug = unique_slugify(instance, slug)
            if not instance.time_published and instance.is_published:
                instance.time_published = now()
        else:
            instance.is_published = False

        old_save_m2m = self.save_m2m

        def save_m2m():
            old_save_m2m()
            instance.tags.clear()
            instance.tags.add(*self.cleaned_data['tags'])

        self.save_m2m = save_m2m

        if commit:
            instance.save()
            self.save_m2m()

        return instance
