# 👩‍💻 Shell de Linux en Python

## 📌 Descripción General
Este proyecto implementa un intérprete de comandos (shell) en Python, capaz de ejecutar comandos del sistema, manejar redirecciones de entrada/salida, procesos en background, pipelines, y comandos internos como cd, jobs y fg. Está diseñado para simular el comportamiento de shells como Bash de forma educativa.

## 🧠 Funcionalidades Principales
- ✅ Ejecución de comandos del sistema `(ls, cat, grep, etc.)`
- 🔁 Redirecciones de entrada `(<)`, salida `(>)` y salida con append `(>>)`
- ⛓️ Pipelines `(|)` para conectar múltiples comandos
- 🌙 Procesos en segundo plano `(&)`
- 📂 Comando `cd` con soporte para `.., -, ~` y rutas absolutas/relativas
- 📋 Comando jobs para listar procesos en background `(jobs, jobs -l)`
- 🎯 Comando `fg` para traer procesos al foreground

## 🧰 Instalación y Uso
**🔧 Requisitos**
- Python 3.6 o superior
- Sistema compatible con comandos Unix (Linux/macOS o WSL en Windows)

**📥 Clonación del repositorio**
```
git clone https://github.com/angemaria25/SCR-Shell.git
cd SCR-Shell
```

**🚀 Ejecución del Shell**
```
python3 shell.py
```

**Esto iniciará el shell personalizado. Verás un prompt donde puedes escribir comandos como `ls`, `cd`, `grep`, usar `|`, redirecciones `>`, `<`, y comandos como `jobs`, `fg`, etc.**

**❗Notas:**
- El shell se ejecuta en modo interactivo.
- Si estás usando Windows, se recomienda usar WSL o una máquina virtual con Linux para compatibilidad con los comandos Unix.
- Para salir del shell, puedes usar Ctrl+C o exit.

## 📁 Estructura del Proyecto
```
SCR-Shell/
├── shell.py               # Archivo principal del shell (main loop y ejecución de comandos).
├── README.md              # Documentación del proyecto.
└── Documentación/
    ├── documentacion.md   # Documentación técnica adicional.
```

## 🧪 Ejemplos de Uso

```bash
Comando simple: $ ls

Redirección de salida: $ echo "Hola mundo" > saludo.txt

Redirección de entrada : $ wc < saludo.txt

Append a archivo: $ echo "Otra línea" >> saludo.txt

Comando con pipes: $ cat saludo.txt | grep Hola

Proceso en segundo plano: $ sleep 5 &
                             [1] 12345

Ver trabajos en background: $ jobs
                               [1]+ Running sleep 5 &

Detalles extendidos: $ jobs -l
                        [1]+ 12345 Running sleep 5 &

Traer trabajo al foreground: $ fg %1
                                 sleep 5
                            
```

## 📝 Licencia
Este proyecto está licenciado bajo la **Licencia MIT**.  
Puedes ver el archivo [LICENSE](./LICENSE) para más detalles.
