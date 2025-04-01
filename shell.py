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
    
    id not partes:
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
    
    try:
        resultado = subprocess.run(
            partes, 
            stdout=subprocess.PIPE,  
            stderr=subprocess.PIPE,  
            text=True  
        )
        
        if resultado.returncode == 0:
            print(resultado.stdout, end="")
        else:
            print(resultado.stderr, end="")
            
    except Exception as e:
        print(f"Error: {e}")
        
        
if __name__ == "__main__":
    main()