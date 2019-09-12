from django import forms


class CreateTaskForm(forms.Form):
    caption = forms.CharField(max_length=200)
    due_date = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M'])


