import os 
import subprocess

def main():
    while True:
        try:
            comando = input("$ ")
            if comando.lower == "exit":
                break
            
            ejecutar_comando(comando)
        
        except KeyboardInterrupt:
            print("\nSaliendo del shell...")
            break
        
def ejecutar_comando(comando):
    partes = comando.split()
    
    if not partes:
        return
    
    if partes[0] == "cd":
        try:
            if len(partes) == 1:
                os.chdir(os.path.expanduser("~"))
            else:
                os.chdir(partes[1])
        except Exception as e:
            print(f"Error inesperado: {e}")
        return
    
    if "|" in comando:
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
                stdin = procesos[i-1].stdout #uso la salida del comando anterior.
                
            if i == len(comandos) - 1:
                stdout = None 
            else:
                stdout = subprocess.PIPE
            
            proceso = subprocess.run(
                cmd_actual,
                stdin=stdin,
                stdout=stdout,
                stderr=subprocess.PIPE,
                text=True
            )
            procesos.append(proceso)
        
        #mostrar salida del último comando.
        if procesos[-1].returncode == 0:
            print(procesos[1].stdout or "", end="")
        else:
            print(procesos[-1].stderr or "", end="")
        return
        
    
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
        
    try:
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
                if stadin_file:
                    stadin_file.close()
                return    
            
            
        resultado = subprocess.run(
            comando_base,
            stdin=stdin_file if redireccion_entrada else None,
            stdout=stdout_file if redireccion_salida else subprocess.PIPE,  
            stderr=subprocess.PIPE,  
            text=True  
        )
        
        if not redireccion_salida:
            if resultado.returncode == 0:
                print(resultado.stdout, end="")
            else:
                print(resultado.stderr, end="")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if stdin_file:
            stdin_file.close()
        if stdout_file:
            stdout_file.close()
        
if __name__ == "__main__":
    main()