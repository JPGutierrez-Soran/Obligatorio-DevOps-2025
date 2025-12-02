import time
import os
import zipfile
import boto3
from botocore.exceptions import ClientError

# Configuración de las instancias
region = "us-east-1"

# Configuración de la estancia EC2
ami_id = "ami-0c02fb55956c7d316"
instance_type = "t2.micro"
iam_instance_profile_name = "LabInstanceProfile"
instance_name = "Obligatorio-Boto3"

# Configuración del Security Group EC2
sg_name = "SG-Boto3"
sg_description = "Permitir trafico web desde cualquier IP (HTTP/80)"

# Configuración de la estancia RDS
DB_INSTANCE_ID = "db-empleados"
DB_NAME = "empleados"
DB_USER = "admin"  # requisito del ejercicio
DB_PASS = os.environ.get("RDS_ADMIN_PASSWORD")  # NO hardcodear

if not DB_PASS:
    raise Exception("Debes definir la variable de entorno RDS_ADMIN_PASSWORD con la contraseña del admin.")

# Credenciales de la app
app_user = "admin"
app_pass = "admin123"

# Configuración de S3, nombre del bucket y ZIP de la app
S3_BUCKET_NAME = "bucket-obligatorio-app"
SRC_APP_FOLDER = "obligatorio-main" 
APP_ZIP_PATH = "/tmp/app.zip"
APP_ZIP_KEY = "app.zip"

# Configuración de clientes AWS
ec2 = boto3.client("ec2", region_name=region)
rds = boto3.client("rds", region_name=region)
ssm = boto3.client("ssm", region_name=region)
s3 = boto3.client("s3", region_name=region)

# Creación del zip con los archivos de la aplicación
if not os.path.isdir(SRC_APP_FOLDER):
    raise Exception(f"La carpeta {SRC_APP_FOLDER} no existe en el directorio actual.")

print(f"Creando ZIP de la carpeta {SRC_APP_FOLDER} en {APP_ZIP_PATH}...")
with zipfile.ZipFile(APP_ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk(SRC_APP_FOLDER):
        for file in files:
            full_path = os.path.join(root, file)
            arcname = os.path.relpath(full_path, SRC_APP_FOLDER)
            z.write(full_path, arcname)
print("ZIP creado correctamente.")

# Creación del bucket S3 y subida del zip
try:
    s3.create_bucket(Bucket=S3_BUCKET_NAME)
    print(f"Bucket creado: {S3_BUCKET_NAME}")
except ClientError as e:
    if e.response["Error"]["Code"] == "BucketAlreadyOwnedByYou":
        print(f"El bucket {S3_BUCKET_NAME} ya existe y es tuyo.")
    else:
        print(f"Error creando bucket: {e}")
        exit(1)

try:
    s3.upload_file(APP_ZIP_PATH, S3_BUCKET_NAME, APP_ZIP_KEY)
    print(f"Archivo {APP_ZIP_PATH} subido a s3://{S3_BUCKET_NAME}/{APP_ZIP_KEY}")
except FileNotFoundError:
    print(f"El archivo {APP_ZIP_PATH} no existe")
    exit(1)
except ClientError as e:
    print(f"Error subiendo archivo a S3: {e}")
    exit(1)

# Creación del Security Group EC2
try:
    response = ec2.create_security_group(
        GroupName=sg_name,
        Description=sg_description,
    )
    sg_id = response["GroupId"]
    print(f"Security Group EC2 creado: {sg_id}")

    ec2.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[
            {
                "IpProtocol": "tcp",
                "FromPort": 80,
                "ToPort": 80,
                "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
            }
        ],
    )

except ClientError as e:
    if "InvalidGroup.Duplicate" in str(e):
        sg = ec2.describe_security_groups(GroupNames=[sg_name])["SecurityGroups"][0]
        sg_id = sg["GroupId"]
        print(f"Security Group EC2 ya existe: {sg_id}")
    else:
        raise

# Creación del Security Group RDS
rds_sg_name = "SG-RDS-MySQL"
rds_sg_description = "Permitir acceso MySQL desde EC2"

try:
    response_rds_sg = ec2.create_security_group(
        GroupName=rds_sg_name,
        Description=rds_sg_description,
    )
    rds_sg_id = response_rds_sg["GroupId"]
    print(f"Security Group RDS creado: {rds_sg_id}")

    ec2.authorize_security_group_ingress(
        GroupId=rds_sg_id,
        IpPermissions=[
            {
                "IpProtocol": "tcp",
                "FromPort": 3306,
                "ToPort": 3306,
                "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
            }
        ],
    )

except ClientError as e:
    if "InvalidGroup.Duplicate" in str(e):
        sg_r = ec2.describe_security_groups(GroupNames=[rds_sg_name])["SecurityGroups"][0]
        rds_sg_id = sg_r["GroupId"]
        print(f"Security Group RDS ya existe: {rds_sg_id}")
    else:
        raise

# Creación de la instancia RDS
print("Creando instancia RDS MySQL.")

try:
    rds.create_db_instance(
        DBInstanceIdentifier=DB_INSTANCE_ID,
        AllocatedStorage=20,
        DBInstanceClass="db.t3.micro",
        Engine="mysql",
        EngineVersion="5.7",
        MasterUsername=DB_USER,
        MasterUserPassword=DB_PASS,
        DBName=DB_NAME,
        PubliclyAccessible=True,
        BackupRetentionPeriod=0,
        VpcSecurityGroupIds=[rds_sg_id],
    )
    print(f"Instancia RDS {DB_INSTANCE_ID} creada correctamente.")
except rds.exceptions.DBInstanceAlreadyExistsFault:
    print(f"La instancia RDS {DB_INSTANCE_ID} ya existe.")

print("Esperando a que la instancia RDS esté disponible.")
rds_waiter = rds.get_waiter("db_instance_available")
rds_waiter.wait(DBInstanceIdentifier=DB_INSTANCE_ID)
print("La instancia RDS está disponible.")

# Obtener el endpoint de la RDS
desc = rds.describe_db_instances(DBInstanceIdentifier=DB_INSTANCE_ID)
db_endpoint = desc["DBInstances"][0]["Endpoint"]["Address"]
print(f"Endpoint de la base de datos: {db_endpoint}")

# Lanzamiento de estancia EC2
print("Lanzando instancia EC2.")

response_instance = ec2.run_instances(
    ImageId=ami_id,
    InstanceType=instance_type,
    MinCount=1,
    MaxCount=1,
    IamInstanceProfile={"Name": iam_instance_profile_name},
    SecurityGroupIds=[sg_id],
    TagSpecifications=[
        {
            "ResourceType": "instance",
            "Tags": [
                {"Key": "Name", "Value": instance_name},
            ],
        }
    ],
)

instance_id = response_instance["Instances"][0]["InstanceId"]
print(f"Instancia EC2 creada con ID: {instance_id}")

print("Esperando a que la instancia EC2 esté disponible.")
waiter = ec2.get_waiter("instance_status_ok")
waiter.wait(InstanceIds=[instance_id])
print("La instancia EC2 está disponible.")

# Obtener IP pública de la EC2
desc_instance = ec2.describe_instances(InstanceIds=[instance_id])
public_ip = desc_instance["Reservations"][0]["Instances"][0]["PublicIpAddress"]

print(f"IP pública de la instancia: {public_ip}")

# Despliegue de la aplicación
print("Desplegando la aplicación en la instancia.")

deploy_script = f"""#!/bin/bash
set -e

# Esperar a que yum deje de estar en uso
while sudo fuser /var/run/yum.pid >/dev/null 2>&1; do
  echo "Esperando a que yum libere el lock"
  sleep 10
done

# Actualizar paquetes
sudo yum clean all
sudo yum makecache
sudo yum -y update

# Instalar Apache, PHP, cliente MariaDB/MySQL, unzip y awscli
sudo yum -y install httpd php php-cli php-fpm php-common php-mysqlnd mariadb unzip awscli

# Habilitar y arrancar servicios httpd y php-fpm
sudo systemctl enable --now httpd
sudo systemctl enable --now php-fpm

# Configurar Apache para usar PHP-FPM si no existe la config
if [ ! -f /etc/httpd/conf.d/php-fpm.conf ]; then
  echo '<FilesMatch \\.php$>
  SetHandler "proxy:unix:/run/php-fpm/www.sock|fcgi://localhost/"
</FilesMatch>' | sudo tee /etc/httpd/conf.d/php-fpm.conf
fi

# Preparar directorio de la app y descargar ZIP desde S3
rm -rf /home/ec2-user/app
mkdir -p /home/ec2-user/app

aws s3 cp s3://{S3_BUCKET_NAME}/{APP_ZIP_KEY} /tmp/app.zip

unzip /tmp/app.zip -d /home/ec2-user/app

# Crear el directorio del webroot
sudo mkdir -p /var/www/html

# Copiar archivos de la app al webroot
sudo cp -r /home/ec2-user/app/* /var/www/html/

# Mover init_db.sql fuera del webroot
if [ -f /var/www/html/init_db.sql ]; then
  sudo mv /var/www/html/init_db.sql /var/www/init_db.sql
fi

# Ejecutar el script SQL contra la RDS para crear tabla y datos
mysql -h {db_endpoint} -u {DB_USER} -p'{DB_PASS}' {DB_NAME} < /var/www/init_db.sql

# Eliminar README.md del webroot
if [ -f /var/www/html/README.md ]; then
  sudo rm -f /var/www/html/README.md
fi

# Crear archivo .env con datos de conexión a la base y credenciales de la app
sudo tee /var/www/.env >/dev/null <<ENV
DB_HOST={db_endpoint}
DB_NAME={DB_NAME}
DB_USER={DB_USER}
DB_PASS={DB_PASS}

APP_USER={app_user}
APP_PASS={app_pass}
ENV

# Ajustar permisos del .env
sudo chown apache:apache /var/www/.env
sudo chmod 600 /var/www/.env

# Ajustar permisos del webroot
sudo chown -R apache:apache /var/www/html

# Reiniciar servicios
sudo systemctl restart httpd
sudo systemctl restart php-fpm
"""

response_cmd = ssm.send_command(
    InstanceIds=[instance_id],
    DocumentName="AWS-RunShellScript",
    Parameters={"commands": [deploy_script]},
)

command_id = response_cmd["Command"]["CommandId"]

print("Esperando a que finalice el despliegue.")
while True:
    output = ssm.get_command_invocation(CommandId=command_id, InstanceId=instance_id)
    if output["Status"] in ["Success", "Failed", "Cancelled", "TimedOut"]:
        break
    time.sleep(2)

print("Estado del despliegue:", output["Status"])
print("Salida estándar del despliegue:")
print(output.get("StandardOutputContent", ""))
print(f"Si el estado es Success, podés acceder a: http://{public_ip}/login.php")
