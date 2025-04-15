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
- **Parámetro**: 
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

`split_con_comillas(comando: str) -> List[str]`

- **Objetivo**: Divide una cadena de comando en tokens, respetando los espacios dentro de comillas simples `'` y dobles `"`, mientras separa correctamente los operadores y argumentos. Es fundamental para preservar argumentos que contienen espacios dentro de comillas como una única unidad léxica.
- **Parámetro**: 
    - `comando (str)`: Cadena de texto ya normalizada por `espacio_tokens()`. (ej: `"echo 'hola mundo' > salida.txt"`)
- **Retorna**: Lista de tokens identificados, donde cada token es una palabra o un grupo de palabras entre comillas. (ej: `["echo", "'hola mundo'", ">", "salida.txt"]`)
- **Proceso**: Esta función utiliza una máquina de estados simple para iterar sobre el comando carácter por carácter. Cambia su comportamiento en función del estado actual:
    - Estado NORMAL: Agrega los caracteres a un buffer hasta encontrar una comilla o espacio.
    - Estado ENTRE_COMILLAS: Mantiene los caracteres dentro de una comilla simple o doble como una unidad.
    - Cuando se encuentra una comilla de cierre, el contenido del buffer se agrega como un único token.

- **Ejemplo**:
  ```
  entrada = "echo 'hola mundo' > salida.txt"
  proceso: 
  1. Estado inicial: Normal
  2. 'e','c','h','o' → token_actual = "echo"
  3. Espacio → guarda "echo", reinicia token_actual
  4. "'" → entra en comillas simples
  5. 'h','o','l','a',' ','m','u','n','d','o' → token_actual = "hola mundo"
  6. "'" → sale de comillas simples
  7. Espacio → guarda "'hola mundo'", reinicia token_actual
  8. '>' → token_actual = ">"
  9. Espacio → guarda ">", reinicia token_actual
  10. 's','a','l','i','d','a','.','t','x','t' → token_actual = "salida.txt"
  11. Fin → guarda "salida.txt"
  # Retorna: ['echo', "'hola mundo'", '>', 'salida.txt']
  ```


### Núcleo del Shell

**main()**

- **Objetivo**: Punto de entrada del programa. Ciclo principal que lee y ejecuta comandos.
- **Parámetro**:
- **Retorna**:
- **Funcionamiento**: 
    - Imprime el prompt  `($ )`
    - Lee la línea de entrada.
    - Procesa el comando con `espacio_tokens()` y `split_con_comillas()`
    - Llama a ejecutar_comando(linea).
- **Ejemplo**:
  ```
  Entrada = echo "Prueba técnica" | grep "técnica" > resultado.txt &
  Proceso:
  1. espacio_tokens() normaliza a: echo "Prueba técnica" | grep "técnica" > resultado.txt &
  2. split_con_comillas() produce: ['echo', '"Prueba técnica"', '|', 'grep', '"técnica"', '>', 'resultado.txt', '&']
  3. ejecutar_comando() detecta pipeline + background:
  - Crea 2 subprocesos conectados por pipe
  - Redirige salida final a resultado.txt
  - Registra job en background_jobs con ID incremental
  ```



