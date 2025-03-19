from datetime import timezone
from django.db import models
from django.contrib.auth.models import User
from django.db.models import TextChoices
from django.conf import settings
import uuid

class TipoClase(TextChoices):
        MAGISTRAL = 'magistral', 'Magistral'
        PRACTICA = 'practica', 'Práctica'
        MIXTA = 'mixta', 'Mixta'
        
class EstadoDeAnimo(TextChoices):
    MUY_MAL = 'muy_mal', 'Muy mal'
    MAL = 'mal', 'Mal'
    REGULAR = 'regular', 'Regular'
    BIEN = 'bien', 'Bien'
    MUY_BIEN = 'muy_bien', 'Muy bien'
    

class WorkHour(models.Model):
    name = models.CharField(max_length=100, default="No seleccionado")
    dayOfWeek = models.CharField(max_length=100)
    startHour = models.TimeField(default="00:00")
    endHour = models.TimeField(default="00:00")
    max_students = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.name} ({self.dayOfWeek} - {self.startHour} - {self.endHour})"
class lecture(models.Model):
    fecha_asignatura = models.DateField()
    horario = models.ForeignKey(WorkHour, on_delete=models.DO_NOTHING, null=True, blank=True)
    estadoDeAnimo = models.CharField(
        max_length=10,
        choices=EstadoDeAnimo.choices,
        default=EstadoDeAnimo.BIEN,
    )
    numero_alumnos = models.IntegerField(default=0)
    turno = models.CharField(max_length=50, default="")
    startHour = models.TimeField(default="00:00")
    endHour = models.TimeField(default="00:00")
    startBreak = models.TimeField(default="00:00")
    endBreak = models.TimeField(default="00:00")
    energia = models.IntegerField(default=0)
    horas_trabajadas_profesor = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    horas_previas_alumnos = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    tipo_clase_primera_hora = models.CharField(
        max_length=10,
        choices=TipoClase.choices,
        default=TipoClase.MAGISTRAL,
    )
    notas_primera_hora = models.TextField(default="")
    tipo_clase_segunda_hora = models.CharField(
        max_length=10,
        choices=TipoClase.choices,
        default=TipoClase.PRACTICA,
    )
    notas_segunda_hora = models.TextField(default="")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    


class UserDataSource(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    data_source = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.user.username}: {self.data_source}"
    
class UploadedCSV(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="uploaded_csvs")
    file = models.FileField(upload_to="Data/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.file.name}"

class UserToken(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, default=uuid.uuid4)
                             
    def __str__(self):
        
        return f"{self.user.username} - {self.token}"