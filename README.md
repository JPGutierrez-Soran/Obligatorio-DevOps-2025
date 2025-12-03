# Obligatorio Programación para DevOps

Este es el README para el Obligatorio final para la materia Programación para DevOps de la carrera AII en la Universidad ORT 2025


## Contenido

Este repositorio cuenta con los dos ejercicios requeridos, el creacion_usuarios.sh , que es el primer ejercicio y el despliegue_aplicacion.py, que es el segundo. 

A su vez, cuenta con el archivo archivo_usuarios.txt, el cual contiene algunos ejemplos para poder pasar como parámetro al correr el ejercicio de Bash.

Por otra parte, se encuenta la carpeta obligatorio-main, que almacena todos los archivos de la aplicación que vamos a desplegar.


## Requisitos generales

Nosotros trabajamos con una VM CentOS Stream 9 gestionada por VirtualBox para poder cumplir la consigna.

Para poder clonar nuestro repo a la VM, es necesario instalar git con el comando:

```bash
$ sudo dnf install -y git
```

Una vez instalado, se puede verificar que todo esté correctamente con el comando:

```bash
$ git --version
```

Para poder clonar el repositorio de Github, se tiene que colorcar el comando:

```bash
$ git clone https://github.com/JPGutierrez-Soran/Obligatorio-DevOps-2025
```

Una vez clonado el repositorio, se accede a él con el comando:

```bash
$ cd Obligatorio-DevOps-2025/
```


### Requisitos para el Ejercicio 1

Para poder correr el script de Bash, es necesario darle permisos de ejecución. Esto se hace con el comando:

```bash
$ chmod +x creacion_usuarios.sh
```

### Requisitos para el Ejercicio 2

Para poder correr el segundo ejercicio, es necesario comprobar los servicios instalados y en caso de ser necesario, instalar determinados paquetes en determinadas versiones.

Como CentOS Stream 9 viene con Python3.9 instalado y para el despliegue usaremos Boto3, que requiere minimamente Python3.10, deberemos de instalar una versión más actualizada de Python. A su vez, necesitaremos instalar PIP por lo que se necesita correr el comando:

```bash
$ sudo dnf install python3.11 python3.11-pip
```

Una vez terminada la instalación de Python y PIP, se puede instalar Boto3 con el comando:

```bash
$ sudo pip3.11 install boto3[crt]
```

Una vez instalado Boto3, hay que verificar si se tiene instalado el paquete de unzip, para ello se necesita correr el comando:

```bash
$ unzip -v
```

En caso de que no esté instalado, se debe de instalar con el comando:

```bash
$ sudo dnf install -y unzip
```

Una vez se instalaron dichos paquetes, se instalará AWS CLI.

Primero se necesita descargar el paquete de instalación con el comando:

```bash
$ curl https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -o awscliv2.zip
```

Luego se descomprime el paquete con el comando:

```bash
$ unzip awscliv2.zip
```

Una vez descomprimido, se ejecuta el insalador con el comando:

```bash
$ sudo ./aws/install
```

Una vez instalado, se puede verificar que todo esté correctamente con el comando:

```bash
$ aws --version
```

Con todo esto instalado, ya se puede configurar las keys de AWS en ~/.aws/credentials para poder acceder sin problemas.
De otra forma puede configurarlo utilizando:

```bash
$ aws configure
```

El último paso para poder correr el script es configurar la contraseña del administrador RDS mediante la variable de entorno con el siguiente comando:

```bash
export RDS_ADMIN_PASSWORD='contraseña'
```


## Modo de uso

### Modo de uso del Ejercicio 1

El ejercicio 1 de Bash está pensado para correr de la siguiente forma.

```bash
$ sdo ./creacion_usuarios.sh -i -c 'contraseña' archivo_usuarios.txt
```

La contraseña que se pase como parámetro, debe cumplir con estándares de seguridad, siendo que debe de tener una longitud mayor a 8 caracteres, tener una mayúscula, una minúscula y un símbolo.

Por otro lado, dentro del archivo archivo_usuarios.txt, se encuentran los ejemplos brindados en la letra del obligatorio para poder resolver.

#### Otros modos de uso del Ejercicio 1

El script está pensado para solo recibir un archivo regular como parámetro, por lo que pasarle el directorio obligatorio-main daría un error.

En adición, en caso de que la contraseña pasada como parámetro no cumpla con los parámetros mencionados anteriormente, también dará error.

### Modo de uso del Ejercicio 2

El script del despliegue se corre simplemente con el comando:

```bash
$ python3.11 despliegue_aplicacion.py
```
