import os 
import re
import subprocess
from collections import OrderedDict

ultimo_directorio = None
background_jobs = OrderedDict()
job_id_counter = 1


def espacio_tokens(comando):
    comando = re.sub(r"\s*(>>|[<>|])\s*", r" \1 ", comando)
    comando = " ".join(comando.split())
    return comando.strip()

def main():
    while True:
        try:
            comando = input("$ ")
            comando = espacio_tokens(comando)
            if comando == "exit":
                break
            
            ejecutar_comando(comando)
        
        except KeyboardInterrupt:
            print("\nSaliendo del shell...")
            break
        except Exception as e:
            print(f"Error: {e}")
            
        
    
def ejecutar_cd(partes):
    global ultimo_directorio
    try:
        directorio_actual = os.getcwd()
        if len(partes) == 1 or partes[1] == "~":
            os.chdir(os.path.expanduser("~"))
        elif partes[1] == "..":
            os.chdir("..")
        elif partes[1] == "-":
            if ultimo_directorio:
                os.chdir(ultimo_directorio)
                print(f"Volviendo al último directorio: {ultimo_directorio}.")
            else:
                print("No hay un directorio anterior al que regresar.")
        elif partes[1].startswith("~/"):
            ruta = os.path.expanduser(partes[1])
            os.chdir(ruta)
        else:
            os.chdir(partes[1])
        ultimo_directorio = directorio_actual
    except FileNotFoundError:
        print(f"Error: No existe el directorio '{partes[1]}'.")
    except Exception as e:
        print(f"Error inesperado: {e}")
            
            
        
def manejar_pipes(comando, background=False):
    global background_jobs, job_id_counter
    
    partes_del_comando = comando.split("|")
    comandos = []
    for cmd in partes_del_comando:
        cmd_limpio = cmd.strip()
        comandos.append(cmd_limpio)

    procesos = []
        
    for i in range(len(comandos)):
        cmd_actual = comandos[i].split()
        if i == 0:
            stdin = None #el primer comando no recibe entrada de otro.
        else:
            stdin = procesos[i-1].stdout #el siguiente comando recibe la salida del comando anterior.

        # El último comando dirige su salida al stdout, no al pipe.
        stdout = subprocess.PIPE if i < len(comandos) - 1 else None
            
        proceso = subprocess.Popen(
            cmd_actual,
            stdin=stdin,
            stdout=stdout,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if i > 0:
            procesos[i-1].stdout.close()
            
        procesos.append(proceso)
    
    if background:
        job_id = job_id_counter
        job_id_counter += 1
        background_jobs[job_id] = {
            "process": procesos,
            "command": comando
        }
        print(f"[{job_id}] {procesos[-1].pid}")
        return 
        
    salida, error = procesos[-1].communicate()
        
    #mostrar salida del último comando.
    if procesos[-1].returncode == 0:
        print(salida or "", end="")
    else:
        print(error or "", end="")
        
def parsear_redirecciones(partes):
    redireccion_salida = None
    redireccion_entrada = None
    append = False 
    comando_base = partes.copy()
    
    i = 0
    while i < len(comando_base):
        if comando_base[i] == ">":
            if i+1 < len(comando_base):
                redireccion_salida = comando_base[i+1]
                comando_base = comando_base[:i]
                break
        elif comando_base[i] == ">>":
            if i+1 < len(comando_base):
                redireccion_salida = comando_base[i+1]
                append = True
                comando_base = comando_base[:i]
                break
        elif comando_base[i] == '<':
            if i+1 < len(comando_base):
                redireccion_entrada = comando_base[i+1]
                comando_base = comando_base[:i]
                break
        i+=1
    
    return comando_base, redireccion_salida, redireccion_entrada, append
        
def ejecutar_comando_redirecciones(comando_base, redireccion_salida, redireccion_entrada, append, background=False):
    global background_jobs, job_id_counter
    
    stdin_file = None
    if redireccion_entrada:
        try:
            stdin_file = open(redireccion_entrada, "r")
        except IOError as e:
            print(f"Error al abrir {redireccion_entrada}: {e}")
            return
            
    stdout_file = None
    if redireccion_salida:
        try:
            mode = "a" if append else "w"
            stdout_file = open(redireccion_salida, mode)
        except IOError as e:
            print(f"Error al abrir {redireccion_salida}: {e}")
            if stdin_file:
                stdin_file.close()
            return    
    
    try:
        proceso = subprocess.Popen(
            comando_base,
            stdin=stdin_file if redireccion_entrada else None,
            stdout=stdout_file if redireccion_salida else subprocess.PIPE,  
            stderr=subprocess.PIPE,  
            text=True  
        )
        
        if background:
            job_id = job_id_counter
            background_jobs[job_id] = {
                "pid": proceso.pid,
                "command": " ".join(comando_base),
                "process": [proceso]
            }
            print(f"[{job_id}] {proceso.pid}")
            job_id_counter += 1
        else:
            salida, error = proceso.communicate()
            
            if not redireccion_salida:
                if proceso.returncode == 0:
                    print(salida or "", end="")
                else:
                    print(error or "", end="")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if stdin_file:
            stdin_file.close()
        if stdout_file:
            stdout_file.close()
            
def listar_jobs(mostrar_detalles=False):
    global background_jobs
    limpiar_jobs_terminados()
    
    if not background_jobs:
        print("No hay procesos en el background.")
        return
    
    max_job_id = 0
    for job_id in background_jobs.keys():
        if job_id > max_job_id:
            max_job_id = job_id
    
    for job_id, job_info in background_jobs.items():
        job_en_ejecucion = False
        for proceso in job_info["process"]:
            if proceso.poll() is None:
                job_en_ejecucion = True
                break
            
        estado = "Running" if job_en_ejecucion else "Done"
        simbolo = "+" if job_id == max_job_id else "-"
        
        #Quitar & si el proceso terminó
        comando = job_info["command"]
        if not job_en_ejecucion:
            comando = comando.rstrip(" &")
            
        if mostrar_detalles: #jobs -l
            if len(job_info["process"]) > 1:
                partes_comando = job_info["command"].split('|')
                for i, proceso in enumerate(job_info["process"]):
                    if i == 0:
                        print(f"[{job_id}]{simbolo} {proceso.pid:>6} {estado:<7} {partes_comando[i].strip()}")
                    else:
                        es_ultimo = i == len(job_info["process"])-1
                        terminator = " &" if (job_en_ejecucion and es_ultimo) else ""
                        print(f"    {proceso.pid:>6}       | {partes_comando[i].strip()}{terminator}")
            else:
                #jobs -l sin pipes
                terminator = " &" if job_en_ejecucion else ""
                print(f"[{job_id}]{simbolo} {job_info['process'][0].pid:>6} {estado:<7} {job_info['command']}{terminator}")
        else:
            #jobs
            terminator = " &" if job_en_ejecucion else ""
            print(f"[{job_id}]{simbolo} {estado:<7} {job_info['command']}{terminator}")
            
def limpiar_jobs_terminados():
    global background_jobs
    jobs_a_eliminar = []
    
    for job_id, job_info in backgorund_jobs.items():
        todos_terminados = True 
        
        for proceso in job_info["process"]:
            if proceso.poll() is None:
                todos_terminados = False
                break 
            
        if todos_terminados:
            jobs_a_eliminar.append(job_id)
            
    for job_id in jobs_a_eliminar:
        del background_jobs[job_id]
        
def ejecutar_comando(comando):
    global background_jobs, job_id_counter
    
    if not comando:
        return
    
    if comando.strip().startswith("jobs"):
        partes = comando.split()
        if len(partes) > 1 and partes[1] == "-l":
            listar_jobs(mostrar_detalles=True)
        else:
            listar_jobs()
        return
        
    is_background = comando.strip().endswith("&")
    if is_background:
        comando = comando[:-1].strip()
    
    partes = comando.split()
    
    if not partes:
        return
    
    if partes[0] == "cd":
        ejecutar_cd(partes)
        return
    
    if "|" in comando:
        manejar_pipes(comando, is_background)
        return
        
    comando_base, redireccion_salida, redireccion_entrada, append = parsear_redirecciones(partes)
    ejecutar_comando_redirecciones(comando_base, redireccion_salida, redireccion_entrada, append, is_background)


if __name__ == "__main__":
    main()