from flask import Blueprint, render_template, request, jsonify
import pyautogui
import pydirectinput
import time
from app.auth import login_required
from app.models.jobs import Job
from app.models.user import User
from app import db # Asume que 'db' se importa desde la aplicación principal
from math import ceil
from sqlalchemy import or_
import tkinter as tk
from tkinter import messagebox
import threading

bp = Blueprint('jobs', __name__, url_prefix='/jobs')



def pedir_confirmacion_segura(titulo, mensaje):
    root = tk.Tk()
    root.withdraw()
    # Esto fuerza a la ventana a ponerse por encima de TODO (incluso el emulador)
    root.attributes("-topmost", True) 
    respuesta = messagebox.askyesno(titulo, mensaje, parent=root)
    root.destroy()
    return respuesta



############# RUTA PRINCIPAL #############

@bp.route('/')
def index():
    # Valores por defecto para la carga inicial
    total_base = Job.query.count()
    return render_template('jobs/crudjobs.html', 
                           cantidad=0, 
                           total_base=total_base, 
                           encontrados=0, 
                           jobs=[], 
                           total_pages=1, 
                           page=1)





###################################### EJECUTAR JOBS #####################################
def ejecutar_pasos_en_pantalla(datos):
    try:
        # Extraer variables con los IDs del HTML

        ini = int(datos.get('instancia_inicial', 1))
        fin = int(datos.get('instancia_final', 1))
        equipo = datos.get('equipo', '')
        subsistema = datos.get('subsistema', '')
        proceso = datos.get('proceso', '')
        descripcion = datos.get('descripcion', '')
        time.sleep(3) 
        
        # --- TU RUTA DE NAVEGACIÓN (INTACTA) ---
        for _ in range(8): 
            pydirectinput.press('tab')
        
        pyautogui.write('1')
        pydirectinput.press('enter')
        time.sleep(1)
        pydirectinput.press('enter')
        
        pyautogui.write('2')
        pydirectinput.press('enter')
        time.sleep(1)
        pydirectinput.press('enter')

        pydirectinput.press('f6') 
        time.sleep(1)
        pydirectinput.press('f6') 
        time.sleep(1)


        # --- BUCLE DE MATRICULA INSTANCIAS
        for i in range(ini, fin + 1):
            instancia_formateada = str(i).zfill(3)
            

            # 1. Equipo/Maquina
            pyautogui.write(equipo.upper())
            time.sleep(2)
          

            # 2. SubSistema
            pyautogui.write(subsistema.upper())
            pydirectinput.press('tab')
            time.sleep(2)

            # 3. Proceso (Concatenando: PROCESO + SERVIDOR + INSTANCIA)
            # Ej: RPCCO + 01 + 005 = RPCCO01005
            proceso_completo = f"{proceso.upper()}{instancia_formateada}"
            pyautogui.write(proceso_completo)

            time.sleep(2)

            pyautogui.write(descripcion.upper())
            time.sleep(5) 
            pydirectinput.press('enter')
            time.sleep(3) 

        return True, f"Instancias {fin} de {fin} creadas."
    except Exception as e:
        return False, str(e)
            
            


    ##################################### ELIMINAR JOBS #####################################


def eliminar_jobs(datos):

    try:
        # Extraer variables con los IDs del HTML

        ini = int(datos.get('instancia_inicial', 1))
        fin = int(datos.get('instancia_final', 1))
        equipo = datos.get('equipo', '')
        subsistema = datos.get('subsistema', '')
        proceso = datos.get('proceso', '')
        descripcion = datos.get('descripcion', '')

                # --- 1. MENSAJE DE ALERTA (CONFIRMACIÓN) ---
        # El código se detendrá aquí hasta que el usuario responda
        msg1 = f"¿Está seguro de ELIMINAR las instancias de la {ini} a la {fin}?"
        if not pedir_confirmacion_segura("Confirmación de Eliminación", msg1):
            return False, "Eliminación cancelada por el usuario."
        
        time.sleep(3) 
        
        # --- TU RUTA DE NAVEGACIÓN (INTACTA) ---
        for _ in range(8): 
            pydirectinput.press('tab')
        
        pyautogui.write('1')
        pydirectinput.press('enter')
        time.sleep(1)
        pydirectinput.press('enter')
        
        pyautogui.write('2')
        pydirectinput.press('enter')
        time.sleep(1)
        pydirectinput.press('enter')

        # 1. Presionar F6 UNA SOLA VEZ antes de empezar el bucle
        pydirectinput.press('f6') 
        time.sleep(1)
            # 1. Subir una posición

        # --- BUCLE DE MATRICULA INSTANCIAS
        for i in range(ini, fin + 1):
            instancia_formateada = str(i).zfill(3)
            proceso_completo = f"{proceso.upper()}{instancia_formateada}"
            
            # 1. Subir una posición (Esto se repite en cada vuelta)
            pydirectinput.press('up')
            time.sleep(0.3) 

            # 2. Moverse 26 veces a la derecha (AHORA ESTÁ DENTRO DEL FOR)

            for _ in range(26):
                pydirectinput.press('right', _pause=0)
            
            # 3. Escribir el proceso (AHORA ESTÁ DENTRO DEL FOR)
            pyautogui.write(proceso_completo)
            time.sleep(1.5)
            pydirectinput.press('enter')
            time.sleep(1)
            
            # 4. Opción 4 y eliminar (AHORA ESTÁ DENTRO DEL FOR)
            pyautogui.write('4')
            time.sleep(1)       
            pydirectinput.press('enter')
            time.sleep(1) #

            msg1 = f"¿Está seguro de ELIMINAR las instancias de la {ini} a la {fin}?"
            if not pedir_confirmacion_segura("Confirmación de Eliminación", msg1):
                return False, "Eliminación cancelada por el usuario."

        # Si eligió SÍ, el código continúa aquí abajo...
            time.sleep(2) 

            pyautogui.hotkey('shift', 'f11')
            time.sleep(1)       



        return True, f"Instancias {fin} de {fin} Eliminadas."
        
    except Exception as e:
        return False, str(e)
            
    



    ##################################### Editar JOBS #####################################

def editar_jobs(datos):
    global PROCESO_ACTIVO
    PROCESO_ACTIVO = True # Resetear al iniciar
    try:
        # Extraer variables con los IDs del HTML

        ini = int(datos.get('instancia_inicial', 1))
        fin = int(datos.get('instancia_final', 1))
        equipo = datos.get('equipo', '')
        subsistema = datos.get('subsistema', '')
        proceso = datos.get('proceso', '')
        descripcion = datos.get('descripcion', '')

                # --- 1. MENSAJE DE ALERTA (CONFIRMACIÓN) ---

        msg1 = f"¿Está seguro de EDITAR las instancias de la {ini} a la {fin}?"
        if not pedir_confirmacion_segura("Confirmación de Edición", msg1):
            return False, "Edición cancelada por el usuario."
        time.sleep(3) 
        
        # --- TU RUTA DE NAVEGACIÓN (INTACTA) ---
        for _ in range(8): 
            pydirectinput.press('tab')
        
        pyautogui.write('1')
        pydirectinput.press('enter')
        time.sleep(1)
        pydirectinput.press('enter')
        
        pyautogui.write('2')
        pydirectinput.press('enter')
        time.sleep(1)
        pydirectinput.press('enter')

        # 1. Presionar F6 UNA SOLA VEZ antes de empezar el bucle
        pydirectinput.press('f6') 
        time.sleep(1)
           
        # --- BUCLE DE MATRICULA INSTANCIAS
        for i in range(ini, fin + 1):

            instancia_formateada = str(i).zfill(3)
            proceso_completo = f"{proceso.upper()}{instancia_formateada}"
            
            # 1. Subir una posición (Esto se repite en cada vuelta)
            pydirectinput.press('up')
            time.sleep(0.3) 

            # 2. Moverse 26 veces a la derecha (AHORA ESTÁ DENTRO DEL FOR)
            for _ in range(26):
                pydirectinput.press('right', _pause=0)
            
            # 3. Escribir el proceso (AHORA ESTÁ DENTRO DEL FOR)
            pyautogui.write(proceso_completo)
            time.sleep(1.5)
            pydirectinput.press('enter')
            time.sleep(1)
            
            # 4. Opción 4 y eliminar (AHORA ESTÁ DENTRO DEL FOR)
            pyautogui.write('2')
            time.sleep(1)
            pydirectinput.press('enter')
            time.sleep(1) #

        ## mensaje de alerta de confirmación de eliminación


                # Esta ventana aparecerá en el centro de tu pantalla
            msg1 = f"¿Está seguro de EDITAR las instancias de la {ini} a la {fin}?"
            if not pedir_confirmacion_segura("Confirmación de Edición", msg1):
                return False, "Edición cancelada por el usuario."
        
        # Si eligió SÍ, el código continúa aquí abajo...
            time.sleep(2) 

            pyautogui.press('delete', presses=3)
            time.sleep(1)
            pydirectinput.press('tab')
        
            pyautogui.press('delete', presses=10)
            time.sleep(1)
            pydirectinput.press('tab')

            pyautogui.press('delete', presses=10)
            time.sleep(1)
            pydirectinput.press('tab')

            pyautogui.press('delete', presses=30)
            time.sleep(1)
            time.sleep(2)
            
            pydirectinput.press('up', presses=6)
            time.sleep(1)
        
            # 1. Equipo/Maquina
            pyautogui.write(equipo.upper())
            time.sleep(2)
        

            # 2. SubSistema
            pyautogui.write(subsistema.upper())
            pydirectinput.press('tab')
            time.sleep(2)

            # 3. Proceso (Concatenando: PROCESO + SERVIDOR + INSTANCIA)
            # Ej: RPCCO + 01 + 005 = RPCCO01005
            proceso_completo = f"{proceso.upper()}{instancia_formateada}"
            pyautogui.write(proceso_completo)

            time.sleep(2)

            pyautogui.write(descripcion.upper())
            time.sleep(3) 
            pydirectinput.press('enter')
        
        
        return True, f"Instancias {ini} a {fin} Editadas."
    except Exception as e:
        return False, str(e)
            
    




###################################################################################3





# RUTAS DE EJECUCIÓN DE JOBS

@bp.route('/test-pasos', methods=['POST'])
def test_pasos():
    data = request.json
    exito, mensaje = ejecutar_pasos_en_pantalla(data)
    return jsonify({"ok": exito, "message": mensaje})


# RUTA DE ELIMINACIÓN DE JOBS

@bp.route('/eliminar-pasos', methods=['POST'])
def eliminar_pasos_ruta():
    data = request.json
    exito, mensaje = eliminar_jobs(data)
    return jsonify({"ok": exito, "message": mensaje})



@bp.route('/editar-pasos', methods=['POST'])
def editar_pasos_ruta():
    data = request.json
    exito, mensaje = editar_jobs(data)
    return jsonify({"ok": exito, "message": mensaje})




#################### listar jobs tabla####################

@bp.route('/listar')
@login_required
def listar():
    filtro = request.args.get('filtro')
    page = request.args.get('page', 1, type=int)

    # 1. Obtenemos el total real de toda la tabla (sin filtros)
    total_base = Job.query.count()

    query = Job.query
    perfil = User.query.all()

    if filtro:
        query = query.filter(or_(
            Job.Subsistema.like(f'%{filtro}%'),
            Job.Nombre_trabajo.like(f'%{filtro}%'),
        ))
        # 2. Obtenemos cuántos coinciden con la búsqueda
        encontrados = query.count()
        per_page = encontrados or 1
    else:
        encontrados = 0 # O puedes poner total_base si prefieres
        per_page = 10

    paginacion = query.paginate(page=page, per_page=per_page, error_out=False)
    
    total = query.count()
    total_pages = ceil(total / per_page) if per_page > 0 else 1

    return render_template(
        'jobs/crudjobs.html',
        jobs=paginacion.items,
        page=page,
        total_pages=total_pages,
        filtro=filtro,
        perfil=perfil,
        total_base=total_base,  # Enviamos el total general
        encontrados=encontrados, # Enviamos el total del filtro
        cantidad=0
    )
