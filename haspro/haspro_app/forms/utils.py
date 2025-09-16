from django import forms


class WidgetClassForm(forms.ModelForm):
    widget_additional_classes = {}

    def __init__(self, *vars, **kwargs):
        super().__init__(*vars, **kwargs)
        for field_name, field in self.fields.items():
            if field_name in self.widget_additional_classes:
                if field.widget.attrs.get('class'):
                    field.widget.attrs['class'] += ' ' + self.widget_additional_classes[field_name]
                else:
                    field.widget.attrs['class'] = self.widget_additional_classes[field_name]
