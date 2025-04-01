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
        
def ejecutar_comando():
    try:
        # Usamos subprocess.run para capturar la salida del comando
        resultado = subprocess.run(
            comando.split, # Divide el comando en lista ["ls", "-l"]
            stdout=subprocess.PIPE,  # Captura la salida estándar
            stderr=subprocess.PIPE,  # Captura errores
            text=True  # Para manejar texto (no bytes)
        )
        
        # Imprime la salida (stdout) o errores (stderr)
        if resultado.returncode == 0:
            print(resultado.stdout, end="")
        else:
            print(resultado.stderr, end="")
            
    except Exception as e:
        print(f"Error: {e}")
        
        
if __name__ == "__main__":
    main()