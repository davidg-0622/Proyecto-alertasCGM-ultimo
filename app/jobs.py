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

bp = Blueprint('jobs', __name__, url_prefix='/jobs')

# --- VARIABLE GLOBAL DE CONTROL ---
PROCESO_ACTIVO = True

############# RUTA PRINCIPAL #############

@bp.route('/')
def index():
    return render_template(
    'jobs/crudjobs.html', 
    cantidad=0, 
    jobs=[],          # Lista de trabajos vacía
    total_pages=1,    # Valor mínimo para que el IF del HTML funcione
    page=1,           # Página actual inicial
    filtro=None       # Sin búsqueda activa
)
##########################  detener proceso global ##########################


@bp.route('/detener', methods=['POST'])
def detener_proceso():
    global PROCESO_ACTIVO
    PROCESO_ACTIVO = False
    print("!!! SEÑAL DE PARADA RECIBIDA !!!")
    return jsonify({"ok": True, "message": "Deteniendo..."})



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
            time.sleep(10) 
            pydirectinput.press('enter')
            time.sleep(3) 

        return True, f"Instancias {fin} de {fin} creadas."
    except Exception as e:
        return False, str(e)
            
            


    ##################################### ELIMINAR JOBS #####################################


def eliminar_jobs(datos):
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
        # El código se detendrá aquí hasta que el usuario responda
        respuesta = pyautogui.confirm(
            text=f'¿Está seguro de ELIMINAR las instancias de la {ini} a la {fin}?',
            title='Confirmación de Eliminación',
            buttons=['SÍ, ELIMINAR', 'CANCELAR']
        )
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
                pydirectinput.press('right')
            
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

        ## mensaje de alerta de confirmación de eliminación


                # Esta ventana aparecerá en el centro de tu pantalla
        respuesta = pyautogui.confirm(
            text=f'¿Deseas proceder con la eliminación de {fin - ini + 1} instancias?',
            title='Confirmación de Seguridad iSeries',
            buttons=['SÍ, ELIMINAR', 'CANCELAR']
        )

        if respuesta == 'CANCELAR':
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
        # El código se detendrá aquí hasta que el usuario responda
        respuesta = pyautogui.confirm(
            text=f'¿Está seguro de Editar las instancias de la {ini} a la {fin}?',
            title='Confirmación de Edición',
            buttons=['SÍ, EDITAR', 'CANCELAR']
        )
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
                pydirectinput.press('right')
            
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
        respuesta = pyautogui.confirm(
            text=f'¿Deseas proceder con la edición de {fin - ini + 1} instancias?',
            title='Confirmación de Seguridad iSeries',
            buttons=['SÍ, EDITAR', 'CANCELAR']
        )

        if respuesta == 'CANCELAR':
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
        time.sleep(10) 
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




#################### listar jobs ####################


from math import ceil

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
            Job.Subsistema.ilike(f'%{filtro}%'),
            Job.Nombre_trabajo.ilike(f'%{filtro}%'),
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
