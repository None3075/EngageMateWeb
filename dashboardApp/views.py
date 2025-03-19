from io import StringIO
from django import forms
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import WorkHour, lecture
from .forms import CSVUploadForm, WorkHourForm, lectureForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Avg, Count
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import UserToken, UserDataSource
import csv
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import datetime
from collections import Counter
import plotly.graph_objs as go
import plotly.io as pio
import plotly.express as px
from django.core.cache import cache
from django.utils.timezone import now
import os
import glob


def signup(request):
    if request.method == "POST":
        if request.POST["password1"] == request.POST["password2"]:
            try:
                user = User.objects.create_user(
                    request.POST["username"], password=request.POST["password1"]
                )
                user.save()
                login(request, user)
                return redirect("index")
            except IntegrityError:
                return render(
                    request,
                    "signup.html",
                    {"error": "El usuario ya existe", "form": UserCreationForm()},
                )
        else:
            return render(
                request,
                "signup.html",
                {"error": "Las contraseñas no coinciden", "form": UserCreationForm()},
            )
    elif request.method == "GET":
        return render(request, "signup.html", {"form": UserCreationForm()})

@login_required
def signout(request):
    logout(request)
    return redirect("index")


def signin(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST["username"],
            password=request.POST["password"],
        )
        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            return render(
                request,
                "signin.html",
                {
                    "error": "Usuario o contraseña incorrectos",
                    "form": AuthenticationForm(),
                },
            )
    elif request.method == "GET":
        if request.user.is_authenticated:
            return redirect("lectures")
        else:
            return render(request, "signin.html", {"form": AuthenticationForm()})


def index(request):
    return render(request, "index.html")

@login_required
def dashboard(request):
    user_data_source = UserDataSource.objects.filter(user=request.user).first().data_source
    return render(request, "dashboard.html", {"user_data_source": user_data_source})

@login_required
def settings(request):
    work_hours = WorkHour.objects.filter(user=request.user)
    work_hour_form = WorkHourForm(prefix='workhour')

    if request.method == "GET":
        return render(request, "settings.html", {"work_hours": work_hours, "workHourForm": work_hour_form})
    
    elif request.method == "POST":
        action = request.POST.get('action')
        if 'workhour-submit' in request.POST:
            form = WorkHourForm(request.POST, prefix='workhour')
            if form.is_valid():
                work_hour = form.save(commit=False)
                work_hour.user = request.user
                work_hour.save()
            return render(request, "settings.html", {"work_hours": work_hours, "workHourForm": work_hour_form})
        elif action == 'deleteWorkHour':
            try:
                work_hour_id = request.POST.get('workHourId')
                work_hour = get_object_or_404(WorkHour, id=work_hour_id, user=request.user)
                work_hour.delete()
            except:
                return render(request, "settings.html", {"work_hours": work_hours, "workHourForm": work_hour_form})
            return render(request, "settings.html", {"work_hours": work_hours, "workHourForm": work_hour_form})

    return render(request, "settings.html", {"error": "Invalid action", "form": work_hour_form})


@login_required
def lectures(request):
    lectures = lecture.objects.filter(user=request.user)
    result_avgs = []
    for lecture_instance in lectures:
        work_hour = lecture_instance.horario
        if work_hour:
            max_students = work_hour.max_students if work_hour else 0
        if max_students and max_students != 0:
            # Calculate the ratio of numero_alumnos to max_students
            ratio = int((lecture_instance.numero_alumnos / max_students) * 100)
            result_avgs.append(ratio)
        else:
            result_avgs.append(-1)
    
    lectures_and_averages = zip(lectures, result_avgs)
    return render(request, "lectures.html", {"lectures_and_averages": lectures_and_averages})

@login_required
def selectLecture(request, id):
    lecture_instance = get_object_or_404(lecture, id=id, user=request.user)
    if request.method == "GET":
        form = lectureForm(instance=lecture_instance)
        return render(request, "selectLecture.html", {"lec": lecture_instance, "form": form})
    elif request.method == "POST":
        form = lectureForm(request.POST, instance=lecture_instance)
        if form.is_valid():
            form.save()
            return redirect("lectures")
        else:
            return JsonResponse({"status": "error", "errors": form.errors})

@login_required
def createLecture(request):
    if request.method == "GET": 
        form = lectureForm()
        return render(request, "createLecture.html", {"form": form})
    
    elif request.method == "POST":
        try:
            form = lectureForm(request.POST)
            if form.is_valid():
                # Instead of splitting a string, get the WorkHour object by its id
                work_hour_id = form.cleaned_data["horario"]
                lecture_instance = lecture(
                    fecha_asignatura=form.cleaned_data["fecha_asignatura"],
                    horario=work_hour_id,
                    numero_alumnos=form.cleaned_data["numero_alumnos"],
                    turno=form.cleaned_data["turno"],
                    startHour=form.cleaned_data["startHour"],
                    endHour=form.cleaned_data["endHour"],
                    startBreak=form.cleaned_data["startBreak"],
                    endBreak=form.cleaned_data["endBreak"],
                    horas_trabajadas_profesor=form.cleaned_data["horas_trabajadas_profesor"],
                    horas_previas_alumnos=form.cleaned_data["horas_previas_alumnos"],
                    tipo_clase_primera_hora=form.cleaned_data["tipo_clase_primera_hora"],
                    notas_primera_hora=form.cleaned_data["notas_primera_hora"],
                    tipo_clase_segunda_hora=form.cleaned_data["tipo_clase_segunda_hora"],
                    notas_segunda_hora=form.cleaned_data["notas_segunda_hora"],
                    energia=form.cleaned_data["energia"],
                    user=request.user,
                )
                lecture_instance.save()
                return redirect("lectures")
            else:
                return JsonResponse({"status": "error", "errors": form.errors})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

@login_required       
def deleteLecture(request, id):
    lecture_instance = get_object_or_404(lecture, id=id, user=request.user)
    lecture_instance.delete()
    return redirect("lectures")

@login_required
def statisticsLecture(request, id):
    lecture_instance = get_object_or_404(lecture, id=id, user=request.user)
    
    # Build file path for the logged-in user's CSV file
    csv_path = f"dashboardApp/Data/{request.user.username}_lectures.csv"
    
    try:
        file_content = default_storage.open(csv_path, "r").read()
    except Exception as e:
        return render(request, "statisticsLecture.html", {
            "lec": lecture_instance,
            "error": f"Error reading CSV: {e}"
        })
    
    csv_reader = csv.DictReader(StringIO(file_content))
    
    # Get the lecture date and start/end times
    lecture_date_str = lecture_instance.fecha_asignatura.strftime("%Y-%m-%d")
    start_hour = lecture_instance.startHour  # assuming datetime.time
    end_hour = lecture_instance.endHour

    # Filter rows that match the lecture date and fall within the start and end hours
    filtered_rows = []
    for row in csv_reader:
        ts = row['fechayhora']  # e.g., "2024-05-07T23:02:34"
        try:
            date_part, time_part = ts.split("T")
            time_obj = datetime.datetime.strptime(time_part, "%H:%M:%S").time()
        except Exception:
            continue
        if date_part == lecture_date_str and start_hour <= time_obj <= end_hour:
            filtered_rows.append(row)
    
    # Prepare data for Plotly from the filtered CSV rows
    times = []
    temperatures = []
    humedads = []
    luminosidades = []
    calidades = []
    for row in filtered_rows:
        try:
            t = datetime.datetime.strptime(row['fechayhora'], "%Y-%m-%dT%H:%M:%S")
            temp = float(row['Media Temperatura'])
            media_humedad = float(row['Media Humedad'])
            media_luminosidad = float(row['Media Luminosidad'])
            media_calidad = float(row['Media CalidadAire'])
            times.append(t)
            temperatures.append(temp)
            humedads.append(media_humedad)
            luminosidades.append(media_luminosidad)
            calidades.append(media_calidad)
        except Exception:
            continue

    # Graph for Media Temperatura
    trace_temp = go.Scatter(
        x=times,
        y=temperatures,
        mode='lines+markers',
        name='Media Temperatura',
        line=dict(color='royalblue', width=2)
    )
    layout_temp = go.Layout(
        title={
            'text': 'Temperatura Media durante la Clase',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': 'darkblue'}
        },
        xaxis=dict(title='Tiempo', showgrid=True, gridwidth=1, gridcolor='lightgray'),
        yaxis=dict(title='Temperatura (°C)', showgrid=True, gridwidth=1, gridcolor='lightgray'),
        template='plotly_white',
        font=dict(family='Arial, sans-serif', size=12, color='black')
    )
    fig_temp = go.Figure(data=[trace_temp], layout=layout_temp)
    chart_div_temp = pio.to_html(fig_temp, full_html=False)

    # Graph for Media Humedad
    trace_humedad = go.Scatter(
        x=times,
        y=humedads,
        mode='lines+markers',
        name='Media Humedad',
        line=dict(color='seagreen', width=2)
    )
    layout_humedad = go.Layout(
        title={
            'text': 'Humedad Media durante la Clase',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': 'darkblue'}
        },
        xaxis=dict(title='Tiempo', showgrid=True, gridwidth=1, gridcolor='lightgray'),
        yaxis=dict(title='Humedad (%)', showgrid=True, gridwidth=1, gridcolor='lightgray'),
        template='plotly_white',
        font=dict(family='Arial, sans-serif', size=12, color='black')
    )
    fig_humedad = go.Figure(data=[trace_humedad], layout=layout_humedad)
    chart_div_humedad = pio.to_html(fig_humedad, full_html=False)

    # Graph for Media Luminosidad
    trace_luminosidad = go.Scatter(
        x=times,
        y=luminosidades,
        mode='lines+markers',
        name='Media Luminosidad',
        line=dict(color='goldenrod', width=2)
    )
    layout_luminosidad = go.Layout(
        title={
            'text': 'Luminosidad Media durante la Clase',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': 'darkblue'}
        },
        xaxis=dict(title='Tiempo', showgrid=True, gridwidth=1, gridcolor='lightgray'),
        yaxis=dict(title='Luminosidad', showgrid=True, gridwidth=1, gridcolor='lightgray'),
        template='plotly_white',
        font=dict(family='Arial, sans-serif', size=12, color='black')
    )
    fig_luminosidad = go.Figure(data=[trace_luminosidad], layout=layout_luminosidad)
    chart_div_luminosidad = pio.to_html(fig_luminosidad, full_html=False)

    # Graph for Media CalidadAire
    trace_calidad = go.Scatter(
        x=times,
        y=calidades,
        mode='lines+markers',
        name='Media Calidad de Aire',
        line=dict(color='indianred', width=2)
    )
    layout_calidad = go.Layout(
        title={
            'text': 'Calidad de Aire Media durante la Clase',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': 'darkblue'}
        },
        xaxis=dict(title='Tiempo', showgrid=True, gridwidth=1, gridcolor='lightgray'),
        yaxis=dict(title='Calidad de Aire', showgrid=True, gridwidth=1, gridcolor='lightgray'),
        template='plotly_white',
        font=dict(family='Arial, sans-serif', size=12, color='black')
    )
    fig_calidad = go.Figure(data=[trace_calidad], layout=layout_calidad)
    chart_div_calidad = pio.to_html(fig_calidad, full_html=False)


    date_str = lecture_instance.fecha_asignatura.strftime("%Y%m%d")
    hour_str = lecture_instance.endHour.strftime("%H")
    #date_str = "20250210"
    #end_time_str = "185247"
    # Create pattern to match files with only the hour part
    #base_path = f"C:\\Users\\marti\\Desktop\\DeustoTech\\integracion\\version2\\logs"
    #pattern = f"{base_path}\\metrics_{date_str}_{hour_str}*_clean\\ENQUA.csv"
    pattern = f"Data/metrics_{date_str}_{hour_str}*_clean/ENQUA.csv"
    
    # Find matching files
    matching_files = glob.glob(pattern)

    if matching_files:
        hotsup_csv_path = matching_files[0]
        data = []

        # Read the CSV file with a semicolon delimiter
        try:
            with open(hotsup_csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    try:
                        # Convert "ts" field from epoch seconds (string) to datetime
                        ts = int(row['ts'])
                        dt = datetime.datetime.fromtimestamp(ts)

                        # Convert the "result" field to a float (handle comma as decimal separator)
                        result_str = row['result'].replace(',', '.')
                        result = float(result_str)

                        data.append({'datetime': dt, 'result': result})
                    except Exception:
                        continue
        except Exception as e:
            context = {
            'lec': lecture_instance,
            'chart_div_temp': chart_div_temp,
            'chart_div_humedad': chart_div_humedad,
            'chart_div_luminosidad': chart_div_luminosidad,
            'chart_div_calidad': chart_div_calidad,
            'chart_div_hotsup': "CSV file not found"
        }
            return render(request, "statisticsLecture.html", context)
    else:
        # No matching file found
        chart_div_hotsup = "<h3>No HOTSUP data file found for this lecture.</h3>"
        context = {
            'lec': lecture_instance,
            'chart_div_temp': chart_div_temp,
            'chart_div_humedad': chart_div_humedad,
            'chart_div_luminosidad': chart_div_luminosidad,
            'chart_div_calidad': chart_div_calidad,
            'chart_div_hotsup': chart_div_hotsup
        }
        return render(request, "statisticsLecture.html", context)

    # Define the time interval as the start and end time of the lecture
    start_time = datetime.datetime.combine(lecture_instance.fecha_asignatura, lecture_instance.startHour)
    end_time = datetime.datetime.combine(lecture_instance.fecha_asignatura, lecture_instance.endHour)
    
    # Filter data using the specified time range
    filtered_data = [d for d in data if start_time <= d['datetime'] <= end_time]

    if filtered_data:
        times = [d['datetime'] for d in filtered_data]
        results = [d['result'] for d in filtered_data]
        trace_hotsup = go.Scatter(
            x=times,
            y=results,
            mode='lines+markers',
            name='Result',
            line=dict(color='indianred', width=2)
        )
        trace_hotsup.mode = 'lines'
        layout_hotsup = go.Layout(
            title={
                'text': 'Evolución del Engagement',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': 'darkblue'}
            },
            xaxis=dict(title='Time', showgrid=True, gridwidth=1, gridcolor='lightgray'),
            yaxis=dict(title='Result', showgrid=True, gridwidth=1, gridcolor='lightgray'),
            template='plotly_white',
            font=dict(family='Arial, sans-serif', size=12, color='black')
        )
        fig = go.Figure(data=[trace_hotsup], layout=layout_hotsup)
        chart_div_hotsup = pio.to_html(fig, full_html=False)
    else:
        chart_div_hotsup = "<h3>No data found in the specified time range.</h3>"
    
    context = {
        'lec': lecture_instance,
        'chart_div_temp': chart_div_temp,
        'chart_div_humedad': chart_div_humedad,
        'chart_div_luminosidad': chart_div_luminosidad,
        'chart_div_calidad': chart_div_calidad,
        'chart_div_hotsup': chart_div_hotsup
    }
    return render(request, "statisticsLecture.html", context)

@login_required
def statistics(request):
    
    pattern = f"Data/metrics_*_*_clean/ENQUA.csv"
        
    # Find matching files
    matching_files = glob.glob(pattern)
    file_averages = []

    if matching_files:
        for file in matching_files:
            hotsup_csv_path = file
            file_data = []
            
            # Read the CSV file with a semicolon delimiter
            try:
                with open(hotsup_csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f, delimiter=';')
                    for row in reader:
                        try:
                            # Convert "ts" field from epoch seconds (string) to datetime
                            ts = int(row['ts'])
                            dt = datetime.datetime.fromtimestamp(ts)

                            # Convert the "result" field to a float (handle comma as decimal separator)
                            result_str = row['result'].replace(',', '.')
                            result = float(result_str)

                            file_data.append({'datetime': dt, 'result': result})
                        except Exception:
                            continue
            except Exception as e:
                print(e)
                continue
            
            # Calculate averages if there are data points
            if file_data:
                avg_ts = sum(d['datetime'].timestamp() for d in file_data) / len(file_data)
                avg_dt = datetime.datetime.fromtimestamp(avg_ts)
                avg_result = sum(d['result'] for d in file_data) / len(file_data)
                
                file_averages.append({'datetime': avg_dt, 'result': avg_result})

        # Sort by datetime to ensure correct line connections
        file_averages.sort(key=lambda x: x['datetime'])

    if file_averages:
        times = [d['datetime'] for d in file_averages]
        results = [d['result'] for d in file_averages]
        
        trace_hotsup = go.Scatter(
            x=times,
            y=results,
            mode='lines+markers',
            name='Average Result',
            line=dict(color='indianred', width=2),
            marker=dict(size=10, symbol='circle')
        )
        
        layout_hotsup = go.Layout(
            title={
                'text': 'Promedio de Engagemate por Sesión',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': 'darkblue'}
            },
            xaxis=dict(title='Tiempo', showgrid=True, gridwidth=1, gridcolor='lightgray'),
            yaxis=dict(title='Resultado Promedio', showgrid=True, gridwidth=1, gridcolor='lightgray'),
            template='plotly_white',
            font=dict(family='Arial, sans-serif', size=12, color='black')
        )
        fig = go.Figure(data=[trace_hotsup], layout=layout_hotsup)
        chart_div5 = pio.to_html(fig, full_html=False)
    else:
        chart_div5 = "<h3>No data found in the specified files.</h3>"
        
    
    # Get total students per fecha_asignatura and workHour
    lectures_by_date_and_workhour = (
        lecture.objects
        .values('fecha_asignatura', 'horario')
        .annotate(total_students=Sum('numero_alumnos'))
        .order_by('fecha_asignatura')
    )

    # Organize data by workHour
    data_dict = {}
    for entry in lectures_by_date_and_workhour:
        workhour = WorkHour.objects.filter(id=entry['horario']).first()
        if workhour is None:
            workhour = "No definido"
        date_ = entry['fecha_asignatura']
        student_count = entry['total_students']
        if workhour not in data_dict:
            data_dict[workhour] = {'fechas': [], 'total_alumnos': []}
        data_dict[workhour]['fechas'].append(date_)
        data_dict[workhour]['total_alumnos'].append(student_count)

    # Define a list of colors for the traces
    colors = ['royalblue', 'seagreen', 'indianred', 'goldenrod', 'darkorange', 'navy', 'purple']

    # Create a trace for each workHour
    traces = []
    for i, (workhour, values) in enumerate(data_dict.items()):
        color = colors[i % len(colors)]
        trace = go.Scatter(
            x=values['fechas'],
            y=values['total_alumnos'],
            mode='lines+markers',
            name=f'{workhour}',
            line=dict(color=color, width=2),
            marker=dict(
                size=8,
                symbol='diamond',
                color=color,
                line=dict(width=2, color='black')
            )
        )
        traces.append(trace)

    layout1 = go.Layout(
        title={
            'text': 'Total de Alumnos por Fecha',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': 'darkblue'}
        },
        xaxis=dict(
            title='Fecha',
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray'
        ),
        yaxis=dict(
            title='Número de Alumnos',
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray'
        ),
        template='plotly_white',
        font=dict(
            family='Arial, sans-serif',
            size=12,
            color='black'
        )
    )
    fig1 = go.Figure(data=traces, layout=layout1)
    chart_div1 = pio.to_html(fig1, full_html=False)

    lectures_by_date_hours = (
        lecture.objects
        .values('fecha_asignatura')
        .annotate(avg_hours=Avg('horas_trabajadas_profesor'))
        .order_by('fecha_asignatura')
    )
    fechas2 = [entry['fecha_asignatura'] for entry in lectures_by_date_hours]
    avg_hours = [entry['avg_hours'] for entry in lectures_by_date_hours]

    trace2 = go.Bar(
        x=fechas2,
        y=avg_hours,
        name='Horas Promedio',
        marker=dict(
            color='royalblue',
            line=dict(color='navy', width=1)
        )
    )
    layout2 = go.Layout(
        title={
            'text': 'Promedio de Horas Trabajadas por Fecha',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': 'darkblue'}
        },
        xaxis=dict(
            title='Fecha',
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray'
        ),
        yaxis=dict(
            title='Horas Trabajadas',
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray'
        ),
        template='plotly_white',
        font=dict(
            family='Arial, sans-serif',
            size=12,
            color='black'
        )
    )
    fig2 = go.Figure(data=[trace2], layout=layout2)
    chart_div2 = pio.to_html(fig2, full_html=True)

    promedio_alumnos = lecture.objects.aggregate(avg_alumnos=Avg('numero_alumnos'))['avg_alumnos']

    mood_data = (
        lecture.objects
        .values('estadoDeAnimo')
        .annotate(count=Count('id'))
    )
    estados = [entry['estadoDeAnimo'] for entry in mood_data]
    mood_counts = [entry['count'] for entry in mood_data]

    trace3 = go.Pie(
        labels=estados,
        values=mood_counts,
        name='Frecuencia de Estados de Ánimo',
        hole=0.4,
        marker=dict(
            colors=['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692'],
            line=dict(color='#000000', width=2)
        ),
        textinfo='label+percent',
        insidetextorientation='radial'
    )
    layout3 = go.Layout(
        title={
            'text': 'Frecuencia de cada Estado de Ánimo',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': 'darkblue'}
        },
        template='plotly_white',
        legend=dict(
            orientation='h',
            x=0.5,
            xanchor='center'
        ),
        margin=dict(l=20, r=20, t=50, b=20),
        font=dict(
            family='Arial, sans-serif',
            size=12,
            color='black'
        )
    )
    fig3 = go.Figure(data=[trace3], layout=layout3)
    chart_div3 = pio.to_html(fig3, full_html=False)

    teaching_types = list(lecture.objects.values_list('tipo_clase_primera_hora', flat=True)) + \
                     list(lecture.objects.values_list('tipo_clase_segunda_hora', flat=True))
    type_counts = Counter(teaching_types)
    tipos = list(type_counts.keys())
    clases_por_tipo = list(type_counts.values())

    trace4 = go.Pie(
        labels=tipos,
        values=clases_por_tipo,
        name='Clases por Tipo de Docencia',
        hole=0.4,
        marker=dict(
            colors=['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692'][:len(tipos)],
            line=dict(color='#000000', width=2)
        ),
        textinfo='label+percent',
        insidetextorientation='radial'
    )
    layout4 = go.Layout(
        title={
            'text': 'Número de Clases por Tipo de Docencia',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': 'darkblue'}
        },
        template='plotly_white',
        legend=dict(
            orientation='h',
            x=0.5,
            xanchor='center'
        ),
        margin=dict(l=40, r=40, t=60, b=40),
        font=dict(
            family='Arial, sans-serif',
            size=12,
            color='black'
        )
    )
    fig4 = go.Figure(data=[trace4], layout=layout4)
    chart_div4 = pio.to_html(fig4, full_html=False)

    context = {
        'chart_div1': chart_div1,
        'chart_div2': chart_div2,
        'chart_div3': chart_div3,
        'chart_div4': chart_div4,
        'chart_div5': chart_div5,
        
    }
    return render(request, 'statistics.html', context)



def csvs(request):
    user_token = request.headers.get('userToken')
    if not user_token:
        return JsonResponse({"error": "User token is missing"}, status=400)

    try:
        user = UserToken.objects.get(token=user_token).user
    except UserToken.DoesNotExist:
        return JsonResponse({"error": "Invalid user token"}, status=400)

    if user.username == "Morelab":
        with open('dashboardApp/data/measured_data3.csv', 'r') as file:
            response = HttpResponse(file, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=lectures.csv'
            return response

@login_required
def status(request):
    if cache.get(f"class_status_{request.user.id}") == "ongoing":
        return JsonResponse({"status": "ongoing"})
    elif cache.get(f"class_status_{request.user.id}") == "break":
        return JsonResponse({"status": "break"})
    return JsonResponse({"status": "ok", "user": request.user.username})

@csrf_exempt
def uploadCsv(request):
    user_token = request.headers.get('userToken')
    endCSV = request.headers.get('end')  # Expected: "start" or "end"
    
    if not user_token:
        return JsonResponse({"error": "User token is missing"}, status=400)

    try:
        user = UserToken.objects.get(token=user_token).user
    except UserToken.DoesNotExist:
        return JsonResponse({"error": "Invalid user token"}, status=400)
    
    print(f"endCSV: {endCSV}")
    
    cache_key_status = f"class_status_{user.id}"
    
    if endCSV == "break":
        cache_key_break_start = f"break_start_{user.id}"
        cache_key_break_end = f"break_end_{user.id}"
        if cache.get(cache_key_status) == "ongoing":
            cache.set(cache_key_status, "break", timeout=8500)
            cache.set(cache_key_break_start, now(), timeout=8500)
        elif cache.get(cache_key_status) == "break":
            cache.set(cache_key_status, "ongoing", timeout=8500)
            cache.set(cache_key_break_end, now(), timeout=8500)
        return JsonResponse({"status": "break"})
    
    elif cache.get(cache_key_status) == "break":
        return JsonResponse({"status": "break"})

    if request.method == "POST":
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_csv = form.save(commit=False)
            uploaded_csv.user = user
            timestamp = now().strftime("%Y%m%d%H%M%S")
            filename = f"{user.username}_{timestamp}.csv"
            uploaded_csv.file.name = filename
            uploaded_csv.save()

            uploaded_file = request.FILES['file']
            uploaded_file.seek(0) 
            uploaded_file_data = uploaded_file.read().decode('utf-8').splitlines()
            uploaded_csv_reader = csv.DictReader(uploaded_file_data)
            for row in uploaded_csv_reader:
                date_str = row.get("fechayhora")
                try:
                    date = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
                except Exception as e:
                    print(e)
                    continue
                break
            
            if endCSV == "start":
                # Store the start time in cache for one hour (or adjust as needed)
                cache_key = f"lecture_start_{user.id}"
                cache.set(cache_key, date, timeout=8500)
                cache_key_status = f"class_status_{user.id}"
                cache.set(cache_key_status, "ongoing", timeout=8500)
            elif endCSV == "end":
                # Retrieve the stored start time from cache
                cache_key = f"lecture_start_{user.id}"
                cache_key_status = f"class_status_{user.id}"
                cache_key_break_start = f"break_start_{user.id}"
                cache_key_break_end = f"break_end_{user.id}"
                
                start_time = cache.get(cache_key)
                break_start = cache.get(cache_key_break_start)
                break_end = cache.get(cache_key_break_end)
                if not break_start:
                    break_start = now()
                if not break_end:
                    break_end = now()
                print(f"start_time: {start_time}")
                print(f"break_start: {break_start}")
                print(f"break_end: {break_end}")
                    
                if start_time:
                    current_time = date
                    # Create a lecture using the retrieved start time and current time as end time.
                    lecture_instance = lecture(
                        fecha_asignatura=current_time.date(),
                        startHour=start_time.time(),
                        endHour=current_time.time(),
                        startBreak=break_start.time(),
                        endBreak=break_end.time(),
                        user=user,
                    )
                    lecture_instance.save()
                    # Remove the cached start time.
                    cache.delete(cache_key)
                    cache.delete(cache_key_status)
                    cache.delete(cache_key_break_start)
                    cache.delete(cache_key_break_end)
                    message = "Lecture created with recorded start and end timestamps."
                else:
                    message = "No start timestamp found. Cannot create lecture."
            else:
                message = "CSV uploaded successfully."
            # Define the path for the user's CSV file
            user_csv_path = f'dashboardApp/Data/{user.username}_lectures.csv'
            # reset reader
            uploaded_file.seek(0)
            uploaded_file_data = uploaded_file.read().decode('utf-8').splitlines()
            uploaded_csv_reader = csv.DictReader(uploaded_file_data)
            # Check if the user's CSV file already exists
            if default_storage.exists(user_csv_path):
                uploaded_csv_rows = [list(next(uploaded_csv_reader).values())]
                with default_storage.open(user_csv_path, 'a') as user_csv_file:
                    writer = csv.writer(user_csv_file, lineterminator='\n')
                    writer.writerows(uploaded_csv_rows)
            else:
                uploaded_csv_rows = [uploaded_csv_reader.fieldnames, list(next(uploaded_csv_reader).values())]
                with default_storage.open(user_csv_path, 'w') as user_csv_file:
                    writer = csv.writer(user_csv_file, lineterminator='\n')
                    writer.writerows(uploaded_csv_rows)
            return render(request, "uploadCsv.html", {"form": form})
    else:
        form = CSVUploadForm()
    return render(request, "uploadCsv.html", {"form": form})

def hotsup(request):
    return render(request, "hotsup.html")


