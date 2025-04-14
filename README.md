## 🐚 Proyecto: Shell de Linux en Python

### 📌 Descripción General
Este proyecto implementa un intérprete de comandos (shell) en Python, capaz de ejecutar comandos del sistema, manejar redirecciones de entrada/salida, procesos en background, pipelines, y comandos internos como cd, jobs y fg. Está diseñado para simular el comportamiento de shells como Bash de forma educativa.


### 🧠 Funcionalidades Principales
✅ Ejecución de comandos del sistema (ls, cat, grep, etc.)

🔁 Redirecciones de entrada (<), salida (>) y salida con append (>>)

⛓️ Pipelines (|) para conectar múltiples comandos

🌙 Procesos en segundo plano (&)

📂 Comando cd con soporte para .., -, ~ y rutas absolutas/relativas

📋 Comando jobs para listar procesos en background (jobs, jobs -l)

🎯 Comando fg para traer procesos al foreground

📦 Soporte de comillas simples y dobles para argumentos con espacios


### 🛠️ Estructura del Código

# shell.py
- main()                         # Bucle principal de lectura de comandos
- ejecutar_comando()            # Lógica general para ejecutar cualquier comando
- manejar_pipes()               # Ejecutar comandos con pipes
- ejecutar_comando_redirecciones()  # Ejecutar con redirecciones
- ejecutar_cd()                 # Implementación del comando 'cd'
- ejecutar_fg()                 # Implementación de 'fg'
- listar_jobs()                 # Mostrar procesos en segundo plano
- limpiar_jobs_terminados()    # Gestión de procesos terminados


### 🧪 Ejemplos de Uso

🔸 Comando simple: $ ls
🔸 Redirección de salida: $ echo "Hola mundo" > saludo.txt
🔸 Redirección de entrada : $ wc < saludo.txt
🔸 Append a archivo: $ echo "Otra línea" >> saludo.txt
🔸 Comando con pipes: $ cat saludo.txt | grep Hola
🔸 Proceso en segundo plano: $ sleep 5 &
                             [1] 12345
🔸 Ver trabajos en background: $ jobs
                               [1]+ Running sleep 5 &
🔸 Detalles extendidos: $ jobs -l
                        [1]+ 12345 Running sleep 5 &
🔸 Traer trabajo al foreground: $ fg %1
                                 sleep 5
                            

### ⚙️ Comportamientos Especiales

cd - → cambia al último directorio
Manejo de comillas simples ' ' y dobles " " para que los argumentos no se separen por espacios
Pipes con múltiples comandos encadenados
Limpieza automática de jobs terminados


### 💻 Requisitos
Python 3.6 o superior
Sistema compatible con comandos Unix (Linux/macOS o WSL en Windows)

