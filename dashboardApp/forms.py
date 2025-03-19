from django import forms
from django.utils.safestring import mark_safe
from .models import UploadedCSV, lecture, WorkHour

class RangeWithPercentageWidget(forms.NumberInput):
    def render(self, name, value, attrs=None, renderer=None):
        base_html = super().render(name, value, attrs, renderer)
        # Use the id from attrs (or fallback to name) so it can be targeted by JS
        slider_id = attrs.get('id', name)
        extra_html = f'<span id="{slider_id}-val">0%</span>'
        return mark_safe(f'{base_html} {extra_html}')

class lectureForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(lectureForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['horario'].queryset = WorkHour.objects.filter(user=user)
            self.fields['horario'].widget.attrs.update({'class': 'form-control'})
            self.fields['startHour'].widget.attrs.update({'class': 'clockpicker'})
            self.fields['endHour'].widget.attrs.update({'class': 'clockpicker'})
            self.fields['startBreak'].widget.attrs.update({'class': 'clockpicker'})
            self.fields['endBreak'].widget.attrs.update({'class': 'clockpicker'})

    class Meta:
        model = lecture
        fields = [
            'fecha_asignatura', 'horario', 'estadoDeAnimo', 'numero_alumnos', 'turno',
            'startHour', 'endHour','startBreak', 'endBreak', 'horas_trabajadas_profesor', 'horas_previas_alumnos',
            'tipo_clase_primera_hora', 'notas_primera_hora', 'tipo_clase_segunda_hora',
            'notas_segunda_hora', 'energia'
        ]
        labels = {
            'startHour': 'Hora de Inicio',
            'endHour': 'Hora de Fin',
            'startBreak': 'Inicio del Recreo',
            'endBreak': 'Fin del Recreo',
            'energia': 'Energía'
        }
        widgets = {
            'fecha_asignatura': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'horario': forms.Select(attrs={'class': 'form-control'}),
            'estadoDeAnimo': forms.Select(attrs={'class': 'form-control'}),
            'numero_alumnos': forms.NumberInput(attrs={'class': 'form-control'}),
            'turno': forms.Select(choices=[('mañana', 'Mañana'), ('tarde', 'Tarde')], attrs={'class': 'form-control'}),
            'startHour': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'endHour': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'startBreak': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'endBreak': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'horas_trabajadas_profesor': forms.NumberInput(attrs={'class': 'form-control'}),
            'horas_previas_alumnos': forms.NumberInput(attrs={'class': 'form-control'}),
            'tipo_clase_primera_hora': forms.Select(attrs={'class': 'form-control'}),
            'notas_primera_hora': forms.Textarea(attrs={'class': 'form-control'}),
            'tipo_clase_segunda_hora': forms.Select(attrs={'class': 'form-control'}),
            'notas_segunda_hora': forms.Textarea(attrs={'class': 'form-control'}),
            'energia': RangeWithPercentageWidget(attrs={
                'class': 'form-control',
                'type': 'range',
                'min': '0',
                'max': '100'
            })
        }

class CSVUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedCSV
        fields = ['file']
        
class WorkHourForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(WorkHourForm, self).__init__(*args, **kwargs)
        self.fields['startHour'].widget.attrs.update({'class': 'clockpicker'})
        self.fields['endHour'].widget.attrs.update({'class': 'clockpicker'})

    class Meta:
        model = WorkHour
        fields = ['name', 'startHour', 'endHour', 'dayOfWeek', 'max_students']
        labels = {
            'name': 'Nombre',
            'startHour': 'Hora de Inicio',
            'endHour': 'Hora de Fin',
            'dayOfWeek': 'Día de la Semana',
            'max_students': 'Número de Alumnos matriculados'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'startHour': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'endHour': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'dayOfWeek': forms.Select(choices=[
                ('Lunes', 'Lunes'),
                ('Martes', 'Martes'),
                ('Miércoles', 'Miércoles'),
                ('Jueves', 'Jueves'),
                ('Viernes', 'Viernes'),
                ('Sábado', 'Sábado'),
                ('Domingo', 'Domingo')
            ], attrs={'class': 'form-control'}),
            'max_students': forms.NumberInput(attrs={'class': 'form-control'})
        }
