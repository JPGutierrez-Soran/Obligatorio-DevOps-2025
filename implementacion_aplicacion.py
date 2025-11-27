import boto3
from botocore.exceptions import ClientError
 
# Configuración para las estancias
# Configuración de estancia EC2
region = "us-east-1"
ami_id = "ami-0c02fb55956c7d316" 
instance_type = "t2.micro" 
iam_instance_profile_name = "LabInstanceProfile" 
instance_name = "Obligatorio-Boto3"

# Configuración de Security Group EC2
sg_name = "SG-Boto3" 
sg_description = "Permitir trafico web desde cualquier IP (HTTP/80)"

# Configuración de la estancia RDS
DB_INSTANCE_ID = "db-empleados"
DB_NAME = "empleados"
DB_USER = "admin"  # requisito del ejercicio
DB_PASS = os.environ.get("RDS_ADMIN_PASSWORD")  # NO hardcodear

if not DB_PASS:
    raise Exception("Debes definir la variable de entorno RDS_ADMIN_PASSWORD con la contraseña del admin.")

# Credenciales de la app (para login en la web)
app_user = "admin"
app_pass = "admin123"

# Configuración del S3, nombre del bucket y ZIP de la app
S3_BUCKET_NAME = "bucket-contenido-aplicacion”
SRC_APP_FOLDER = "obligatorio-main" 
APP_ZIP_PATH = "/tmp/app.zip"
APP_ZIP_KEY = "app.zip"

# Creación de clientes de AWS
s3 = boto3.client("s3", region_name=region)
ec2 = boto3.client("ec2", region_name=region)
rds = boto3.client("rds", region_name=region)
ssm = boto3.client("ssm", region_name=region)

# Crear o reutilizar Security Group
try: 
    response = ec2.create_security_group(
        GroupName=sg_name,
        Description=sg_description,
    )
    sg_id = response["GroupId"]
    print(f"Security Group creado: {sg_id}")

    # Reglas de ingreso: puerto 80 desde cualquier IP
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
        print(f"Security Group ya existe: {sg_id}")
    else:
        raise

# Lanzar instancia EC2
print("Lanzando instancia EC2...")
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
print(f"Instancia creada con ID: {instance_id}")

# Esperar a que la instancia esté en estado running
print("Esperando a que la instancia esté en estado running")
waiter = ec2.get_waiter("instance_status_ok").wait(InstanceIds=[instance_id])
print("La instancia está en estado running.")
