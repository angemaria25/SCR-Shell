# Documentación Técnica del Shell

## Introducción

Este proyecto implementa un shell interactivo en Python que soporta:

- Ejecución de comandos del sistema
- Redirecciones de entrada/salida `(>, >>, <)`
- Tuberías `|` entre comandos
- Ejecución en segundo plano `&`
- Comandos internos `(cd, jobs, fg)`

El shell sigue un diseño modular con componentes claramente separados para el parsing, ejecución y gestión de procesos.

## Arquitectura del Sistema

### Componentes Fundamentales

`espacio_tokens(comando: str) -> str`

- **Objetivo**: Normaliza los espacios alrededor de operadores especiales `(>, <, |, >>)` en un comando de shell para facilitar su posterior tokenización y procesamiento.
- **Parámetros**: 
    - `comando`: Cadena de texto ingresada por el usuario (ej: `"ls -l>out.txt"`)
- **Retorna**: Cadena de texto con espacios normalizados alrededor de operadores (ej: `"ls -l > out.txt"`)
- **Proceso**: 
    1. Identificación de operadores:
        - Usa expresión regular para encontrar:
            `>>`: redirección append
            `>, <, |`: operadores simples
        - Añade espacios antes y después de cada operador encontrado.
    2. Normalización de espacios:
        - Divide la cadena en todos los espacios blancos.
        - Vuelve a unir con un solo espacio entre elementos.
        - Elimina espacios al inicio/final.
- **Ejemplo1**:
  ```
  entrada = "ls -l>out.txt"
  proceso: 
  1. Detecta '>' → añade espacios
  "ls -l > out.txt"
  2. Normaliza espacios (ningún cambio)
  3. Retorna: "ls -l > out.txt"
  salida = espacio_tokens(entrada)  # "ls -l > out.txt"
  ```

- **Ejemplo2**:
  ```
  entrada = "cat file.txt|grep \"error\""
  proceso:
  1. Detecta '|' → añade espacios
  "cat file.txt | grep "error""
  2. Normaliza espacios
  3. Retorna: "cat file.txt | grep "error""
  salida = espacio_tokens(entrada)  # "cat file.txt | grep "error""
  ```


### Componentes Principales

**main()**

- **Objetivo**: Controla el bucle principal del shell.
- **Funcionamiento**: 
    - Muestra el prompt `($ )`
    - Lee el comando del usuario
    - Procesa el comando con `espacio_tokens()` y `split_con_comillas()`
    - Determina el tipo de comando y lo ejecuta

