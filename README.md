# Obligatorio Programación para DevOps

Este es el README para el obligatorio final para la materia Programación para DevOps de la carrera AII en la Universidad ORT 2025

## Contenido

Este repositorio cuenta con los dos ejercicios requeridos, el creacion_usuarios.sh , que es el primer ejercicio y el implementacion_aplicacion.py, que es el segundo. 

A su vez, cuenta con el archivo archivo_usuarios.txt, el cual contiene algunos ejemplos para poder pasar como parámetro al correr el ejercicio de Bash.

Por otra parte, se encuenta la carpeta obligatorio-main, que almacena todos los archivos de la aplicación que vamos a desplegar.


## Requisitos generales

Nosotros trabajamos con una VM CentOS Stream 9 gestionada por VirtualBox para poder cumplir la consigna.

Para poder clonar nuestro repo a la VM, es necesario instalar git con el siguiente comando:

```bash
sudo dnf install -y git
```

## Requisitos Ejercicio 2

Para poder correr el segundo ejercicio, es necesario comprobar y en caso necesario instalar determinados servicios.

Como CentOS Stream 9 viene con Python

Instalar Python 3.11 y PIP con sudo dnf install pytohn3.11 python3.11-pip
Instalar Boto3 con pip3.11 install boto3crt
Verificar si unzip está instalado con unzip -v
Instalar unzip co sudo dnf install -y uzip
Instalar AWS CLI con 
	Descarga el paquete de instalación con curl https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -o awscliv2.zip
	Descomprime el paquete con unzip awscliv2.zip
	Ejecuta el instalador con sudo ./aws/install
	Verifica la instalación con aws --version
Configurar las keys en home/.aws/credentials
