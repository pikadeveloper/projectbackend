Se necesita realizar la configuración inicial
Se utilizo mariadb 11.6.2 como base de datos para este proyecto
a traves de la shell se realizaron configuraciones de inicializacion
Pasos a seguir

#Acceder Mysql SHELL
(configuracion defecto)
mysql -u root -p

##Nuestra base de datos se llama conectait

Crear una base de datos
CREATE DATABASE conectait CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

Eliminar una base de datos
drop database conectait;

#Dentro del directorio del proyecto

##Crear entorno virtual
python -m venv entorno

ejecutar script de entorno virtual (Dentro de la carpeta del proyecto)
entorno\Scripts\activate
ejecutar el comando: pip install -r requirements.txt

##Comprobar si existen carpetas de pycache y migrations, eliminarlas para no tener conflictos entre archivos

#Ejecutar comandos

python manage.py makemigrations base    

python manage.py migrate

Para realizar pruebas crear el super usuario
python manage.py createsuperuser

seguir pasos de la consola
python manage.py runserver

Cambiar credenciales utilizadas en AWS al momento de crear la RDS