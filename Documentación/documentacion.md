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

**`espacio_tokens(comando: str) -> str`**

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

**`split_con_comillas(comando: str) -> List[str]`**

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
```
main
└──> espacio_tokens
    └──> split_con_comillas
        └──> ejecutar_comando
                ├──> ejecutar_cd (si el comando es "cd")
                ├──> listar_jobs (si el comando es "jobs")
                ├──> ejecutar_fg (si el comando es "fg")
                ├──> manejar_pipes (si contiene "|")
                ├──> parsear_redirecciones (si contiene "<", ">", ">>")
                └──> ejecutar_comando_redirecciones (si contiene redirecciones o es un comando simple)
```

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

**`ejecutar_comando(tokens: List[str])`**

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

**`ejecutar_cd(tokens: List[str])`**

- **Objetivo**: 
    - Cambiar el directorio actual del shell al especificado por el usuario, con soporte para rutas relativas, absolutas, directorio home (`~`), directorio padre (`..`), cambio al último directorio (`-`) y rutas relativas al home (`~/ruta`).
    - Además, mantiene un seguimiento del último directorio visitado mediante la **variable global** `ultimo_directorio`.
- **Parámetro**: 
    - `partes (List[str])`: Lista de cadenas que representan los elementos del comando cd.
        - partes[0] debería ser 'cd'.
        - partes[1] puede ser una ruta o una bandera especial `(~, .., -, ~/ruta)`.
- **Variables globales**:
    - `ultimo_directorio (str)`: Ruta del último directorio visitado, utilizada cuando el usuario quiere volver al anterior con `cd -`.
- **Proceso**:
    1. Se guarda el directorio actual con `os.getcwd()` antes de hacer cualquier cambio.
    2. Se analizan los argumentos para determinar el comportamiento del comando:
        - Sin argumentos o con `~`: se cambia al directorio home del usuario usando `os.path.expanduser("~")`.
        - Con `..`: se cambia al directorio padre.
        - Con `-`: se intenta volver al directorio anterior almacenado en `ultimo_directorio`.
            - Si `ultimo_directorio` está definido, se cambia a ese directorio e imprime un mensaje indicando el cambio.
            - Si no está definido, informa que no hay un directorio anterior.
        - Con ruta que empieza por `~/`: se expande la ruta relativa al home con `os.path.expanduser`.
        - Cualquier otra ruta: se interpreta literalmente y se intenta acceder a esa ubicación.
    3. Si el cambio de directorio fue exitoso, se actualiza `ultimo_directorio` con la ruta anterior (`directorio_actual`).
    4. Si ocurre un error (como que el directorio no exista o sea inaccesible), se muestra un mensaje informativo.

**`manejar_pipes(comando, background=False)`**

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
        1. Se llama a parsear_redirecciones(['cat', 'entrada.txt'])
            - No hay redirecciones aquí.
            - Retorna: 
                comando_base = ['cat', 'entrada.txt']
                redireccion_entrada = None
                redireccion_salida = None
                append = False
        2. Como es el primer comando y no hay <, stdin_actual = None.
        3. Como no es el último comando, stdout_actual = subprocess.PIPE (para encadenar con el siguiente comando).
        4. Se ejecuta:
            proceso = subprocess.Popen(['cat', 'entrada.txt'], stdout=subprocess.PIPE)
        5. stdin_previo se actualiza con proceso.stdout.
  4.  Iteración 2: Segundo comando - grep "error"
        1. Se llama a parsear_redirecciones(['grep', 'error'])
            - No hay redirecciones aquí.
            - Retorna: 
                comando_base = ['grep', 'error']
        2. stdin_actual = stdin_previo (la salida de cat).
        3. Como no es el último, stdout_actual = subprocess.PIPE.
        4. Se ejecuta:
            proceso = subprocess.Popen(['grep', 'error'], stdin=stdin_previo, stdout=subprocess.PIPE)
        5. stdin_previo se actualiza con proceso.stdout.
   5. Iteración 3: Último comando - sort > errores.txt
        1. Se llama a parsear_redirecciones(['sort', '>', 'errores.txt'])
            - Hay redirección de salida: redireccion_salida = "errores.txt" , append = False
        2. Como es el último, stdout_actual = open("errores.txt", "w")
        3. stdin_actual = stdin_previo (salida de grep).
        4. Se ejecuta:
            proceso = subprocess.Popen(['sort'], stdin=stdin_previo, stdout=archivo)
   6. Se espera al último proceso con communicate(), pero no imprime nada porque hubo redirección a archivo.
  ```

**`parsear_redirecciones(partes)`**

- **Objetivo**: Extrae las redirecciones `<`, `>`, `>>` desde una lista de tokens.
- **Parámetro**: 
    - `partes`: Lista de tokens del comando, por (ej: ["cat", "archivo.txt", ">", "salida.txt"]).
- **Proceso**: 
- **Retorna**: 
    - El comando limpio sin redirecciones.
    - El archivo de entrada (si hay `<`).
    - El archivo de salida (si hay `>` o `>>`).
    - Un booleano append para saber si es `>>` (añadir) o `>` (sobrescribir).
- **Ejemplo1**:
  ```
  entrada = ["cat", "archivo.txt", ">", "salida.txt"]
  Proceso:
  1. i = 0 → "cat" → nada
  2. i = 1 → "archivo.txt" → nada
  3. i = 2 → ">" → detecta redirección de salida
  4. Guarda:
        redireccion_salida = "salida.txt"
        comando_base = ["cat", "archivo.txt"]
        append = False
  ```
- **Ejemplo2**:
  ```
  entrada = ["grep", "error", "<", "entrada.txt"]
  Proceso:
  1. i = 0 → "grep" → nada
  2. i = 1 → "error" → nada
  3. i = 2 → "<" → detecta redirección de entrada
  4. Guarda:
        redireccion_entrada = "entrada.txt"
        comando_base = ["grep", "error"]
  ```
- **Ejemplo3**:
  ```
  entrada = ["sort", "archivo.txt", ">>", "ordenado.txt"]
  Proceso:
  1. i = 0 → "sort" → nada
  2. i = 1 → "archivo.txt" → nada
  3. i = 2 → ">>" → redirección de salida en modo append
  4. Guarda:
        redireccion_salida = "ordenado.txt"
        append = True
        comando_base = ["sort", "archivo.txt"]
  ```
            
**`ejecutar_comando_redirecciones(comando_base, redireccion_salida, redireccion_entrada, append, background=False)`**

- **Objetivo**: 
    - Ejecuta un comando individual que ya fue preprocesado para detectar si tiene redirecciones o si se ejecuta en background.
    - Este comando ya no incluye los tokens `>`, `>>`, `<`, `&`, etc. Es decir, todo eso ya lo extrajo `parsear_redirecciones()` y lo pasó limpio a esta función.
- **Parámetros**: 
    - `comando_base	list[str]`:	Comando sin redirecciones (ej. [`"ls", "-l"`])
    - `redireccion_salida (str o None)`: Nombre del archivo si se redirige salida (`>` o `>>`)
    - `redireccion_entrada (str o None)`: Nombre del archivo si se redirige entrada (`<`)
    - `append (bool)`: True si la salida se agrega (`>>`), False si sobrescribe (`>`)
    - `background (bool)`: True si el proceso debe ejecutarse en segundo plano
- **Proceso**:
    1. Verifica si hay archivo de entrada (`redirección de entrada <`):
        - Si lo hay, abre el archivo en modo lectura ("r") y lo asigna como stdin.
        - Si ocurre un error al abrirlo (por ejemplo, no existe), se muestra un mensaje y se cancela la ejecución.
    2. Verifica si hay archivo de salida (`redireccion_salida: > o >>`):
        - Si lo hay, abre el archivo en modo:
            - Si es `>`, lo abre en modo de sobreescritura ("w").
            - Si es `>>`, lo abre en modo de agregar al final del archivo ("a").
        - Se usa como stdout.
        - Si ocurre un error al abrirlo, también se cancela la ejecución y se cierran recursos si es necesario.
    3. Lanza el proceso con `subprocess.Popen()`:
        - Si hay redirección de entrada, el archivo se pasa como stdin.
        - Si hay redirección de salida, el archivo se pasa como stdout.
        - Si no hay redirección de salida, captura stdout internamente para imprimirlo después.
        - Se ejecuta `comando_base`, que es una lista de strings (ej: `["ls", "-l"]`).
    4. Comprueba si se ejecuta en background (`&`):
        - Si el comando se debe ejecutar en segundo plano:
            - Guarda el proceso en el diccionario de trabajos en segundo plano (background_jobs) con un ID único.
            - Muestra por pantalla el PID del proceso.
            - La función finaliza sin esperar a que el proceso termine.
    5. Si no es background (foreground):
        - Si el comando se ejecuta en primer plano:
            - La función espera a que el proceso finalice con `.communicate()`
            - Si no hubo redirección de salida, muestra la salida estándar en la terminal.
            - Si hubo errores, también los muestra en pantalla.
    6. Cierre de archivos:
        - Una vez terminado todo, se cierran los archivos abiertos para entrada o salida.
- **Ejemplo de Proceso Completo**:
  ```
  1. Input original del usuario: echo hola > saludo.txt &
  2. Tokenización: → ["echo", "hola", ">", "saludo.txt", "&"]
  3. Se detecta & → background = True  → Tokens quedan: ["echo", "hola", ">", "saludo.txt"]
  4. parsear_redirecciones() extrae:
        - comando_base = ["echo", "hola"]
        - redireccion_salida = "saludo.txt"
        - redireccion_entrada = None
        - append = False
  5. Se llama a:
            ejecutar_comando_redirecciones(
                comando_base=["echo", "hola"],
                redireccion_salida="saludo.txt",
                redireccion_entrada=None,
                append=False,
                background=True)
  6. La función:
        - Abre "saludo.txt" en modo "w".
        - Ejecuta echo hola redirigiendo la salida al archivo.
        - Guarda el proceso como job en background.
        - Muestra: [1] 12345 (por ejemplo)
  ```


**`listar_jobs(mostrar_detalles=False)`**

- **Objetivo**: 
    - Muestra en la terminal la lista de trabajos que el usuario ha puesto en segundo plano utilizando `&`. Informa sobre su **estado actual** (`Running` o `Done`), su **identificador** (`job_id`), **PIDs asociados** (si es una pipeline) y el **comando original ejecutado**.
    - Imita el comportamiento del comando `jobs` y `jobs -l`del shell de Unix.
- **Parámetros**: 
    - `mostrar_detalles (bool)`:
        - `True`: muestra información detallada: los PIDs individuales y las partes del comando si hay pipelines.
        - `False (por defecto)`: se muestra información resumida con el ID del trabajo, estado y comando original.
- **Variable globale**: 
    - `background_jobs (dict)`: Diccionario que almacena los trabajos en segundo plano.
```
background_jobs = {
    job_id: {
        "command": str,
        "process": list[subprocess.Popen]
    },
    ...
}
```
- **Proceso**: 
    1. Limpieza de trabajos terminados:
        - Llama a `limpiar_jobs_terminados()` para remover de `background_jobs` los trabajos cuyos procesos ya finalizaron.
    2. Verificación de existencia de trabajos:
        - Si no hay trabajos activos (`background_jobs está vacío`), se imprime `"No hay procesos en el background."` y retorna.
    3. Cálculo del ID más alto:
        - Se identifica el `max_job_id` para marcar el trabajo más reciente con `+` y el penúltimo con `-`, replicando el comportamiento estándar del shell.
    4. Para cada trabajo:
        - Se verifica si algún proceso del trabajo sigue activo (`poll() is None`).
        - Se define el **estado** del trabajo: `"Running"` o `"Done"`.
        - Se elimina el carácter `&` del final del comando si el trabajo ha terminado.
        - Se muestra el resultado en función del valor de `mostrar_detalles`.
    5. Visualización del comando:
        - Según el valor de `mostrar_detalles`, se imprime:
            - Una línea por proceso (si es un pipeline), con PID, símbolo de pipe (`|`) y el fragmento del comando correspondiente.
            - Una línea simple si el trabajo tiene un solo proceso.
- **Retorna**: No retorna nada, imprime la información de los trabajos activos directamente a la salida estándar.
- **Ejemplo1**:
```
entrada = sleep 60 &
comando: jobs
salida: [1]+ Running  sleep 60 &
```
- **Ejemplo2**:
```
entrada = ls -l &  #El proceso termina casi inmediatamente.
comando: jobs
salida: [2]- Done    ls -l
```
- **Ejemplo3**:
```
entrada = comando1 | comando2 | comando3 &
comando: jobs -l
salida: [1]+ 12350 Running comando1
             12351       | comando2
             12352       | comando3 & 
```




