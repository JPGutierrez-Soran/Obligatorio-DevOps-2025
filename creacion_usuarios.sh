# Función para registrar errores con el timestamp de fecha y hora
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

# Validación del archivo pasado
if [[ $# -ne 1 ]]; then
    echo "Uso: $0 [-i] [-c <contraseña>] <archivo_usuarios>"
    registrar_error "Error: número incorrecto de parámetros."
    exit 1
fi

archivo="$1"

if [[ ! -f "$archivo" ]]; then
    echo "Error: '$archivo' no es un archivo regular o no existe."
    registrar_error "Error: archivo inexistente o inválido → $archivo"
    exit 1
fi

# Comprobanción de contraseña
if "$PASSWORD" -ne "" then
  if [[ ${#PASSWORD} -lt 8 ]] || \
    ! [[ "$PASSWORD" =~ [a-z] ]] || \
    ! [[ "$PASSWORD" =~ [A-Z] ]] || \
    ! [[ "$PASSWORD" =~ [0-9] ]] || \
    ! [[ "$PASSWORD" =~ [^[:alnum:]] ]]; then
    echo "Error: la contraseña no cumple los requisitos de seguridad."
    registrar_error "Contraseña no cumple con los requisitos."
    exit 1
  fi
else $PASSWORD="BancoRiendo!2025"
fi

echo "Iniciando creación de usuarios según archivo: $archivo"
CREADOS=0

# Lectura y procesamiento del archivo
while IFS=':' read -r usuario shell home crear_home comentario; do
    # Saltar líneas vacías o comentarios
    [[ -z "$usuario" || "$usuario" =~ ^# ]] && continue

    # Contar cantidad de campos válidos
    campos=0
    for campo in "$usuario" "$shell" "$home" "$crear_home" "$comentario"; do
        [[ -n "$campo" ]] && ((campos++))
    done

    if (( campos < 4 || campos > 5 )); then
        registrar_error "Error: línea con formato incorrecto → '$usuario:$shell:$home:$crear_home:$comentario'"
        $INFO && echo "Línea inválida: se esperaban entre 4 y 5 campos."
        continue
    fi

    # Construir comando useradd
    cmd=( useradd -s "$shell" -d "$home" )
    [[ -n "$comentario" ]] && cmd+=( -c "$comentario" )
    [[ "$crear_home" =~ ^[Ss]i$ ]] && cmd+=( -m )
    cmd+=( "$usuario" )

    # Ejecutar comando y gestionar resultado
    if "${cmd[@]}" &>/dev/null; then
        if [[ -n "$PASSWORD" ]]; then
            echo "$usuario:$PASSWORD" | chpasswd &>/dev/null
        fi
        ((CREADOS++))
        $INFO && echo "Usuario '$usuario' creado correctamente."
    else
        registrar_error "Error al crear usuario '$usuario'."
        $INFO && echo "Error al crear usuario '$usuario'."
    fi
done < "$archivo"

echo
echo "Proceso finalizado. Usuarios creados: $CREADOS"
echo "Errores registrados en: $LOG_ERRORES"
