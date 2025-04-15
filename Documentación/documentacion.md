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
- **Retorna**: Cadena de texto con espacios normalizados alrededor de operadores (ej: `"ls -l > out.txt"`)
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

- **Objetivo**: Divide una cadena de comando en tokens, respetando los espacios dentro de comillas simples `'` y dobles `"`, mientras separa correctamente los operadores y argumentos. 
- **Parámetro**: 
    - `comando (str)`: Cadena de texto que representa el comando de entrada del usuario, ya normalizada por `espacio_tokens()` para tener los operadores separados por espacios (ej: `"echo 'hola mundo' > salida.txt"`)
- **Proceso**: 
    1. Utiliza el módulo `shlex` de Python, configurado con `posix=True` de manera predeterminada .
    2. Llama a shlex.split(comando) para dividir la entrada en tokens:
        - Combina palabras entre comillas como un solo token.
        - Maneja correctamente los caracteres escapados.
        - Elimina las comillas externas del resultado.
    3. Retorna la lista de tokens.
- **Retorna**: Lista de cadenas, cada una representando un token individual, con las comillas ya eliminadas por `shlex.split`.
- **Ejemplo1**:
  ```
  entrada = echo "Hola mundo" > archivo.txt
  salida: ['echo', 'Hola mundo', '>', 'archivo.txt']
  ```
- **Ejemplo2**:
  ```
  entrada = "grep 'error critico' < log.txt"
  salida: ['grep', 'error critico', '<', 'log.txt']
  ```


### Flujo de Ejecución General del Shell

**main()**

- **Objetivo**: Punto de entrada del programa. Inicia el ciclo principal del shell, recibe el input del usuario, y delega el procesamiento y ejecución del comando.
- **Proceso**: 
    - Imprime el prompt  `($ )`
    - Lee la línea de entrada.
    - Procesa el comando con `espacio_tokens()` y `split_con_comillas()`
    - Llama a ejecutar_comando(linea).
- **Flujo**:
    main
    └──> espacio_tokens
        └──> split_con_comillas
            └──> ejecutar_comando
                    ├──> ejecutar_cd (si el comando es 'cd')
                    ├──> ejecutar_jobs (si el comando es 'jobs')
                    ├──> ejecutar_fg (si el comando es 'fg')
                    ├──> ejecutar_comando_background (si el comando termina en '&')
                    ├──> ejecutar_con_pipes (si contiene '|')
                    ├──> ejecutar_con_redirecciones (si contiene '<', '>', '>>')
                    └──> ejecutar_simple (para un comando simple sin nada especial)

- **Ejemplo**:
  ```
  entrada = echo "Prueba técnica" | grep "técnica" > resultado.txt &
  Proceso:
  1. espacio_tokens() normaliza entrada
  2. split_con_comillas() produce: ['echo', 'Prueba técnica', '|', 'grep', 'técnica', '>', 'resultado.txt', '&']
  3. ejecutar_comando() detecta pipeline + background:
  - Crea 2 subprocesos conectados por pipe
  - Redirige salida final a resultado.txt
  - Registra job en background_jobs con ID incremental
  ```

`ejecutar_comando(tokens: List[str])`

- **Objetivo**: Gestiona la ejecución de un comando del shell a partir de una lista de tokens, determinando si se trata de un comando interno `(cd, jobs, fg)`, si se ejecuta en segundo plano `&`, si contiene pipes `|` o redirecciones `(>, <, >>)`, y ejecutándolo con la función adecuada en cada caso.
- **Parámetro**: 
    - `tokens (list[str])`: Lista de tokens obtenidos por `split_con_comillas`.
- **Proceso**:
    1. Si `tokens` está vacío, la función retorna sin hacer nada.
    2. Si el primer token es `cd`, se llama a  `ejecutar_cd(tokens)` con todos los tokens (ya que puede incluir el directorio destino).
    3. Si el primer token es `"jobs"`:
        - Si el segundo token es `"-l"`, llama a `listar_jobs(mostrar_detalles=True)`.
        - En cualquier otro caso, llama a `listar_jobs()` sin argumentos.
    4. Si el comando es `"fg"`:
        - Si hay un segundo token, lo pasa como argumento a `ejecutar_fg()` (representa el job id o %job_id).
        - Si no, llama a `ejecutar_fg(None)` para traer el último job en segundo plano al frente.
    5. Si el **último token** es `"&"`:
        - Se marca `is_background = True`.
        - Se elimina `"&"` de la lista de tokens para no interferir con el resto del procesamiento.
    6. Manejo de pipes (`|`):
        - Se reconstruye el comando como string (`comando_str = " ".join(tokens)`).
        - Si hay un pipe (`"|" in comando_str"`), se llama a `manejar_pipes(comando_str, is_background)` y se retorna.
    7. Manejo de redirecciones (`<`, `>`, `>>`) o ejecución normal:
        - Se llama a `parsear_redirecciones(tokens)` que retorna:
            - `comando_base`: lista de tokens del comando base sin redirecciones.
            - `redireccion_salida`: nombre de archivo de salida si existe (None si no).
            - `redireccion_entrada`: archivo de entrada si existe (None si no).
            - `append`: booleano indicando si es `>>` (append) o `>` (sobrescribe).
        - Luego se llama a `ejecutar_comando_redirecciones()` pasando esos elementos junto con `is_background`.
- **Retorna**: No retorna explícitamente nada. Su propósito es controlar el flujo de ejecución de comandos dependiendo de su tipo y estructura.
- **Ejemplo1**:
  ```
  entrada = ["sort", "<", "nombres.txt", ">", "ordenados.txt"]
  Proceso:
  1. Verifica si tokens esta vacío. ---- ❌ → Hay tokens → sigue.
  2. Verifica si es un comando interno como jobs, fg, cd. ---- ❌ → El primer token es "sort".
  3. Verifica si es en segundo plano (&). ---- ❌ → El último token no es "&". 
    - is_background = False
  4. Verifica si contiene pipes (|). ---- ❌ →  porque "|" in comando_str es False.
    - Entonces llama a :
        comando_base, redireccion_salida, redireccion_entrada, append = parsear_redirecciones(tokens)
        - Y luego llama a ejecutar_comando_redirecciones() con el resultado de parsear_redirecciones().
  ```
- **Ejemplo2**:
  ```
  entrada = ["cat", "entrada.txt", "|", "grep", "error", ">", "salida.txt", "&"]
  Proceso:
  1. Verifica si tokens esta vacío. ---- ❌ → Hay tokens → sigue.
  2. Verifica si es un comando interno como jobs, fg, cd. ---- ❌ → El primer token es "cat".
  3. Verifica si es en segundo plano (&). ---- ✅ → El último token es "&". 
    - Se elimina el "&":
        tokens = ["cat", "entrada.txt", "|", "grep", "error", ">", "salida.txt"]
        is_background = True
  4. Verifica si contiene pipes (|). ---- ✅ →  porque "|" in comando_str es True.
    - Entonces llama a :
        manejar_pipes("cat entrada.txt | grep error > salida.txt", is_background=True)
  ```


`manejar_pipes(comando, background=False)`

- **Objetivo**: Ejecuta comandos que incluyen tuberías (`|`) y, opcionalmente, redirecciones de entrada (`<`) y salida (`>`, `>>`), respetando las restricciones: 
    - `<` solo está permitido en el primer comando.
    - `>` o `>>` solo están permitidos en el último comando.
    - También soporta la ejecución en segundo plano (`&`) si se indica en el parámetro `background=True`.
- **Parámetros**: 
    - `comando (str)`: El comando completo como cadena con pipes y posibles redirecciones (ej: "cat archivo.txt | grep hola | sort > salida.txt").
    - `background (bool)`: Indica si el comando debe ejecutarse en segundo plano.
- **Proceso**:
    1. Separar los comandos por `|` y limpiar los espacios.
    2. Iterar sobre cada comando:
        - Detectar redirecciones usando `parsear_redirecciones()`.
        - Validar reglas de uso de redirecciones.
        - Configurar correctamente `stdin` y `stdout` dependiendo de si está al inicio, al medio o al final.
    3. Crear los procesos conectados mediante `subprocess.PIPE` entre ellos.
    4. Si es en segundo plano, se guarda en `background_jobs`, si no, espera a que termine y muestra el resultado del último comando.
- **Retorna**: 
    - No retorna explícitamente, pero imprime salidas y errores del último proceso si no hay redirección.
    - Si es en background, imprime el job ID y PID del proceso final.
- **Ejemplo**:
  ```
  entrada = cat entrada.txt | grep "error" | sort > errores.txt
  Proceso:
  1. Separación del comando por pipes.
  2. Limpieza de comandos y creación de lista comandos → salida: ["cat entrada.txt", 'grep "error"', "sort > errores.txt"] 
  3. Iteración 1: Primer comando - cat entrada.txt
        - Se llama a parsear_redirecciones(['cat', 'entrada.txt'])
            
  ```

