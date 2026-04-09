from flask import Blueprint, render_template, request, jsonify
import pyautogui
import pydirectinput
import time

bp = Blueprint('jobs', __name__, url_prefix='/jobs')

def ejecutar_pasos_en_pantalla(datos):
    try:
        # Extraer variables con los IDs del HTML
        user = datos.get('user')
        password = datos.get('password')
        servidor = datos.get('instancia_servidor', '01') 
        ini = int(datos.get('instancia_inicial', 1))
        fin = int(datos.get('instancia_final', 1))
        equipo = datos.get('equipo', '')
        subsistema = datos.get('subsistema', '')
        proceso = datos.get('proceso', '')
        descripcion = datos.get('descripcion', '')

        time.sleep(3) 
        
        # --- TU RUTA DE NAVEGACIÓN (INTACTA) ---
        pyautogui.write(user.upper(), interval=0.1)
        pyautogui.write(password, interval=0.1)
        pydirectinput.press('enter') 
        time.sleep(1)
        pydirectinput.press('enter') 
        time.sleep(3)
        
        pyautogui.write('1')
        pydirectinput.press('enter')
        pyautogui.write('1')
        pydirectinput.press('enter')

        for _ in range(8): 
            pydirectinput.press('tab')
        
        pyautogui.write('1')
        pydirectinput.press('enter')
        pydirectinput.press('enter')
        
        pyautogui.write('2')
        pydirectinput.press('enter')
        pydirectinput.press('enter')

        # --- BUCLE DE MATRICULACIÓN CORREGIDO ---
        for i in range(ini, fin + 1):
            instancia_formateada = str(i).zfill(3)
            
            pydirectinput.press('f6') 
            time.sleep(1)

            # 1. Equipo/Maquina
            pyautogui.write(equipo.upper())
            pydirectinput.press('tab')

            # 2. SubSistema
            pyautogui.write(subsistema.upper())
            pydirectinput.press('tab')

            # 3. Proceso (Concatenando: PROCESO + SERVIDOR + INSTANCIA)
            # Ej: RPCCO + 01 + 005 = RPCCO01005
            proceso_completo = f"{proceso.upper()}{servidor}{instancia_formateada}"
            pyautogui.write(proceso_completo)
            
            # 4. Los campos intermedios (Servidor, Inicial, Final)
            # Si el cursor cae en ellos tras el TAB del proceso, los llenamos:
            pydirectinput.press('tab')
            pyautogui.write(servidor)
            pyautogui.write(instancia_formateada)
            pyautogui.write(instancia_formateada)
            
            # 5. Salto a Descripción (Ajusta los TAB si es necesario)
            pydirectinput.press('tab')
            pyautogui.write(descripcion.upper())
            
            pydirectinput.press('enter')
            time.sleep(1.5) 

        return True, f"Instancias {ini} a {fin} creadas."
    except Exception as e:
        return False, str(e)


@bp.route('/test-pasos', methods=['POST'])
def test_pasos():
    data = request.json
    # Pasamos todo el diccionario 'data' para tener acceso a todos los campos
    exito, mensaje = ejecutar_pasos_en_pantalla(data)
    return jsonify({"ok": exito, "message": mensaje})

@bp.route('/')
def index():
    return render_template('jobs/crudjobs.html')



