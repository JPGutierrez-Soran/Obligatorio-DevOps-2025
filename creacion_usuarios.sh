#!/bin/bash

# Función para registrar errores con fecha y hora
LOG_ERRORES="errores.log"

registrar_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_ERRORES"
}

# Opciones con getopts
INFO=false
PASSWORD=""

while getopts ":ic:" opt; do
    case "$opt" in
        i) INFO=true ;;
        c) PASSWORD="$OPTARG" ;;
        :) echo "Error: Falta argumento para -$OPTARG" >&2; exit 2 ;;
        \?) echo "Opción inválida: -$OPTARG" >&2; exit 2 ;;
    esac
done
shift $((OPTIND-1))

# Validación de archivo pasado
if [[ $# -ne 1 ]]; then
    echo "Uso: $0 [-i] [-c <contraseña>] <archivo_usuarios>"
    registrar_error "Error: número incorrecto de parámetros."
    exit 1
fi

archivo="$1"

if [[ ! -f "$archivo" ]]; then
    echo "Error: '$archivo' no es un archivo regular o no existe."
    registrar_error "Error: archivo inexistente o inválido: $archivo"
    exit 1
fi

# Validación de contraseña
#Si no se pasó una contraseña como parámetro, se asigna una por defecto
if [[ -z "$PASSWORD" ]]; then
    PASSWORD="BancoRiendo!2025"
fi

# Validación de contraseña ingresada
if [[ ${#PASSWORD} -lt 8 ]] || \
   ! [[ "$PASSWORD" =~ [a-z] ]] || \
   ! [[ "$PASSWORD" =~ [A-Z] ]] || \
   ! [[ "$PASSWORD" =~ [0-9] ]] || \
   ! [[ "$PASSWORD" =~ [^[:alnum:]] ]]; then
    echo "Error: la contraseña no cumple los requisitos de seguridad."
    registrar_error "Contraseña no cumple con los requisitos."
    exit 1
fi

# Lectura y procesamiento del archivo
echo "Iniciando creación de usuarios según el archivo: $archivo"
CREADOS=0


while IFS=':' read -r usuario shell home crear_home comentario; do
    # Saltar líneas vacías o comentarios
    [[ -z "$usuario" || "$usuario" =~ ^# ]] && continue

    # Contar cantidad de campos válidos
    campos=0
    for campo in "$usuario" "$shell" "$home" "$crear_home" "$comentario"; do
if [[ -n "$campo" ]]; then
((campos = campos + 1))
fi
    done

    if (( campos < 4 || campos > 5 )); then
        registrar_error "Error: línea con formato incorrecto: '$usuario:$shell:$home:$crear_home:$comentario'"
        $INFO && echo "Línea inválida: se esperaban entre 4 y 5 campos."
        continue
    fi

    # Construir comando useradd
    cmd=( useradd -s "$shell" -d "$home" )
    [[ -n "$comentario" ]] && cmd+=( -c "$comentario" )
    [[ "$crear_home" =~ ^[Ss][Ii]$ ]] && cmd+=( -m )
    cmd+=( "$usuario" )

    # Ejecutar comando y gestionar resultado
    if "${cmd[@]}" &>/dev/null; then
        if [[ -n "$PASSWORD" ]]; then
            echo "$usuario:$PASSWORD" | chpasswd &>/dev/null
        fi
        ((CREADOS = CREADOS + 1))
        if $INFO; then 
       ASEGURADO_HOME="NO" 
       [[ "$crear_home" =~ ^[Ss][Ii]$ ]] && ASEGURADO_HOME="SI"
       echo "Usuario $usuario creado con éxito con datos indicados:"
        [[ -n "$comentario" ]] && echo "Comentario: $comentario"
        echo "Dir home: $home"
        echo "Asegurado existencia de directorio home: $ASEGURADO_HOME"
        echo "Shell por defecto: $shell"
        echo
    fi

    else
        registrar_error "Error al crear usuario '$usuario'."
        $INFO && echo "Error al crear usuario '$usuario'."
    fi
done < "$archivo"

echo
echo "Proceso finalizado. Usuarios creados: $CREADOS"
echo "Errores registrados en: $LOG_ERRORES"

