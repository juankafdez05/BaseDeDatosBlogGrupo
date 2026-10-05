# Instalación de Oracle Database 26ai Enterprise en Debian 13

Esta guía detalla el procedimiento para preparar el sistema operativo e instalar Oracle Database 26ai Enterprise Edition (instalación mediante *gold image* y creación de una base de datos contenedora CDB con PDB) en un entorno Debian 13 (Trixie).

> **Atención**: Debian no es una distribución oficialmente certificada por Oracle. La instalación requiere deshabilitar la validación estricta del instalador mediante la variable `CV_ASSUME_DISTID=OL8` y la opción `-ignorePrereqFailure`.

## 1. Requisitos Mínimos y Preparación del Sistema Operativo

Antes de comenzar el despliegue, el servidor debe cumplir con los siguientes recursos mínimos exigidos por Oracle Database:

* **Memoria RAM**: Mínimo 2 GB (recomendado 8 GB o superior).

* **Memoria de Intercambio (SWAP)**:

  * Igual a la RAM si está entre 2 GB y 16 GB.

  * 16 GB fijos si la RAM es superior a 16 GB.

* **Espacio en Disco**: Al menos 10 GB de espacio libre para el software (`ORACLE_HOME`), espacio adicional para la base de datos (`/u01/oradata`) y mínimo 1 GB libre en `/tmp`.

* **Resolución de nombres**: FQDN asignado correctamente en `/etc/hosts`.

### Instalación de paquetes y adaptación de librerías en Debian

En primer lugar, se instalan todas las herramientas de compilación, enlazado, shells y bibliotecas del sistema necesarias para que el instalador de Oracle pueda reconstruir los binarios adecuadamente.

```
sudo apt update
sudo apt install -y \
  binutils gcc g++ make libc6-dev \
  libaio-dev libaio1t64 libnsl2 libstdc++6 \
  libelf-dev elfutils ksh bc unzip \
  net-tools sysstat psmisc lsof \
  libxi6 libxtst6 libxrender1 \
  rlwrap

```

En Debian 13 el paquete de la biblioteca `libaio1` se empaqueta como `libaio1t64` (`libaio.so.1t64`), pero el instalador de Oracle busca explícitamente el nombre tradicional `libaio.so.1`. Creamos el enlace simbólico y actualizamos la caché de bibliotecas.

```
sudo ln -s /usr/lib/x86_64-linux-gnu/libaio.so.1t64 /usr/lib/x86_64-linux-gnu/libaio.so.1
sudo ldconfig

```

Comprobamos que las bibliotecas críticas quedan bien resueltas:

```
sudo ldconfig -p | grep -E 'libaio|libnsl'

```

```
[INSERTA AQUÍ LA SALIDA DEL COMANDO EN TU TERMINAL]

```

### Resolución de nombres de red

Configuramos el FQDN del servidor y aseguramos que apunte a la IP estática en el archivo `/etc/hosts` para evitar fallos de red durante la configuración del Listener.

```
sudo hostnamectl set-hostname ora26ai.example.com
echo "TU_IP   ora26ai.example.com   ora26ai" | sudo tee -a /etc/hosts

```

Verificamos la resolución:

```
hostname -f
getent hosts ora26ai.example.com

```

```
[INSERTA AQUÍ LA SALIDA DEL COMANDO EN TU TERMINAL]

```

## 2. Configuración de Usuarios, Kernel y Directorios Estándar (OFA)

### Grupos y usuario de sistema

De acuerdo con las recomendaciones de la guía oficial de instalación de Oracle, creamos el grupo primario para la instalación (`oinstall`), el grupo de administración (`dba`) y el usuario de sistema `oracle` asignado a ambos.

```
sudo groupadd -g 54321 oinstall
sudo groupadd -g 54322 dba
sudo useradd -m -u 54321 -g oinstall -G dba -s /bin/bash oracle
sudo passwd oracle

```

Verificamos la creación del usuario:

```
id oracle

```

```
[INSERTA AQUÍ LA SALIDA DEL COMANDO EN TU TERMINAL]

```

### Parámetros del kernel y límites del sistema

Añadimos los parámetros de memoria compartida, semáforos, descriptores de archivos y rangos de puertos efímeros en `/etc/sysctl.conf` para cumplir con las especificaciones del motor de Oracle.

```
sudo tee -a /etc/sysctl.conf <<'EOF'

# Oracle Database 26ai
fs.file-max = 6815744
fs.aio-max-nr = 1048576
kernel.sem = 250 32000 100 128
kernel.shmmni = 4096
kernel.shmall = 1073741824
kernel.shmmax = 4398046511104
kernel.panic_on_oops = 1
net.core.rmem_default = 262144
net.core.rmem_max = 4194304
net.core.wmem_default = 262144
net.core.wmem_max = 1048576
net.ipv4.ip_local_port_range = 9000 65500
EOF
sudo sysctl -p

```

```
[INSERTA AQUÍ LA SALIDA DEL COMANDO EN TU TERMINAL]

```

A continuación, definimos los límites de recursos de procesos, archivos abiertos y pila para el usuario `oracle` en `/etc/security/limits.conf`.

```
sudo tee -a /etc/security/limits.conf <<'EOF'

# Oracle Database 26ai
oracle   soft   nofile    1024
oracle   hard   nofile    65536
oracle   soft   nproc     16384
oracle   hard   nproc     16384
oracle   soft   stack     10240
oracle   hard   stack     32768
oracle   soft   memlock   134217728
oracle   hard   memlock   134217728
EOF

```

Aseguramos que el módulo `pam_limits` se aplique en sesiones de cambio de usuario e inspeccionamos los límites efectivos:

```
sudo sed -i 's/^#\s*\(session\s\+required\s\+pam_limits.so\)/\1/' /etc/pam.d/su
sudo su - oracle -c 'ulimit -n -u -s'

```

```
[INSERTA AQUÍ LA SALIDA DEL COMANDO EN TU TERMINAL]

```

### Directorios OFA y variables de entorno

Creamos los directorios de instalación según la arquitectura OFA (Oracle Flexible Architecture) asignándoles el propietario y permisos correspondientes.

```
sudo mkdir -p /u01/app/oracle/product/26.0.0/dbhome_1
sudo mkdir -p /u01/app/oraInventory
sudo mkdir -p /u01/oradata
sudo mkdir -p /u01/fast_recovery_area
sudo chown -R oracle:oinstall /u01
sudo chmod -R 775 /u01

```

Configuramos las variables de entorno del usuario `oracle` en su archivo `~/.bashrc`. Destaca la variable `CV_ASSUME_DISTID=OL8`, indispensable para omitir la comprobación de distribución no soportada en Debian.

```
sudo tee -a /home/oracle/.bashrc <<'EOF'

# Oracle Database 26ai
export TMP=/tmp
export TMPDIR=$TMP
export ORACLE_HOSTNAME=ora26ai.example.com
export ORACLE_BASE=/u01/app/oracle
export ORACLE_HOME=$ORACLE_BASE/product/26.0.0/dbhome_1
export ORACLE_SID=ORCL
export ORACLE_UNQNAME=ORCL
export DATA_DIR=/u01/oradata
export PATH=$ORACLE_HOME/bin:$ORACLE_HOME/OPatch:$PATH
export LD_LIBRARY_PATH=$ORACLE_HOME/lib:/lib:/usr/lib
export CLASSPATH=$ORACLE_HOME/jlib:$ORACLE_HOME/rdbms/jlib
export NLS_LANG=AMERICAN_AMERICA.AL32UTF8
export CV_ASSUME_DISTID=OL8
alias sqlp='rlwrap sqlplus / as sysdba'
EOF
sudo chown oracle:oinstall /home/oracle/.bashrc

```

Tras esto, es necesario ejecutar el sed a continuación ya que Debian mete por defecto en todos los .bashrc un bloque que bloquea la ejecución del contenido de estos en shell no interactivas, asi que es sed elimina dicho bloque para que no nos estorbe en comandos que expanden sub shells que ejecutaremos durante la instalación.

```
sudo sed -i '/# If not running interactively/,/esac/d' /home/oracle/.bashrc
```

Verificamos las variables de entorno cargadas:

```
sudo su - oracle -c 'env | grep -E "ORACLE|CV_ASSUME"'

```

```
[INSERTA AQUÍ LA SALIDA DEL COMANDO EN TU TERMINAL]

```

## 3. Instalación del Software y Creación de la Base de Datos

### Descompresión de la imagen de oracle e instalación silenciosa

Descomprimimos el paquete de instalación directamente en la ruta del `$ORACLE_HOME` usando el usuario `oracle`.

```
sudo su - oracle -c 'unzip -q /TU_DIRECTORIO/LINUX.X64_2326100_db_home.zip -d /u01/app/oracle/product/26.0.0/dbhome_1'

```

Tras esto es comveniente eliminar el fichero original de la imagen.

```
rm -f /TU_DIRECTORIO/LINUX.X64_2326100_db_home.zip
```

Iniciamos la instalación silenciosa indicando únicamente la instalación del motor de software (`INSTALL_DB_SWONLY`). Omitimos las advertencias de prerequisitos con `-ignorePrereqFailure`.

```
sudo su - oracle -c 'cd /u01/app/oracle/product/26.0.0/dbhome_1 && ./runInstaller -silent -ignorePrereqFailure \
  oracle.install.option=INSTALL_DB_SWONLY \
  UNIX_GROUP_NAME=oinstall \
  INVENTORY_LOCATION=/u01/app/oraInventory \
  ORACLE_BASE=/u01/app/oracle \
  oracle.install.db.InstallEdition=EE \
  oracle.install.db.OSDBA_GROUP=dba \
  oracle.install.db.OSOPER_GROUP=dba \
  oracle.install.db.OSBACKUPDBA_GROUP=dba \
  oracle.install.db.OSDGDBA_GROUP=dba \
  oracle.install.db.OSKMDBA_GROUP=dba \
  oracle.install.db.OSRACDBA_GROUP=dba \
  SECURITY_UPDATES_VIA_MYORACLESUPPORT=false \
  DECLINE_SECURITY_UPDATES=true'

```

```
[INSERTA AQUÍ LA SALIDA DEL COMANDO EN TU TERMINAL]

```

Finalizada la instalación del software, ejecutamos los scripts de registro y permisos con privilegios elevados (`sudo`).

```
sudo /u01/app/oraInventory/orainstRoot.sh
sudo /u01/app/oracle/product/26.0.0/dbhome_1/root.sh

```

```
[INSERTA AQUÍ LA SALIDA DEL COMANDO EN TU TERMINAL]

```

Comprobamos que el software se registró correctamente en el inventario:

```
sudo su - oracle -c 'sqlplus -V'
sudo cat /u01/app/oraInventory/ContentsXML/inventory.xml

```

```
[INSERTA AQUÍ LA SALIDA DEL COMANDO EN TU TERMINAL]

```

### Configuración del Listener y Despliegue de la Base de Datos (CDB/PDB)

Con el usuario `oracle`, creamos el Listener predeterminado escuchando en el puerto 1521 usando `netca`.

```
sudo su - oracle -c '$ORACLE_HOME/bin/netca -silent -responsefile $ORACLE_HOME/assistants/netca/netca.rsp'
sudo su - oracle -c '$ORACLE_HOME/bin/lsnrctl status'

```

```
[INSERTA AQUÍ LA SALIDA DEL COMANDO EN TU TERMINAL]

```

#### Fundamentos de la Arquitectura Multitenant (CDB y PDB)

A partir de las versiones modernas de Oracle Database, la arquitectura **Multitenant** es el estándar obligatorio para desplegar bases de datos. Se compone de dos elementos principales:

* **Container Database (CDB):** Es la base de datos contenedora o raíz. Corresponde a la instancia física real que administra los procesos de segundo plano del sistema operativo, asigna la memoria RAM (SGA y PGA), gestiona los archivos de control y alberga el Diccionario de Datos global (`CDB$ROOT`).

* **Pluggable Database (PDB):** Es una base de datos enchufable o portátil que reside dentro de la CDB. Representa el entorno lógico dedicado a la aplicación, alojando los esquemas, tablas e índices del usuario en completo aislamiento de otras PDBs.

**¿Por qué es obligatorio configurar ambas?**
Oracle ha descontinuado el modelo tradicional no contenedor (*Non-CDB*). Para cumplir con los requerimientos del motor y las mejores prácticas de administración:

1. El contenedor raíz (`CDB$ROOT`) está reservado exclusivamente para los metadatos y tareas globales de Oracle; el sistema prohíbe crear tablas de aplicación directamente en él.

2. Es indispensable crear al menos **una PDB activa** (como `PDB1`) para almacenar la información de los usuarios y garantizar la separación entre la infraestructura de la base de datos y los datos de negocio.

Antes de poder ejecutar el binario dbca para crear la bd, como nos encontramos en Debian y no en un sistema basado en redhat, es necesario que creemos un synlink de /bin/true como /bin/rpm ya que dbca usa este binario para comprobar requisitos del sistema antes de hacer nada, así que como sabemos que todas las dependencias ya están presentes usaremos este truco para saltarnos la verificación y que no nos de error.
    
```
sudo ln -sf /bin/true /bin/rpm
```

A continuación, ejecutamos `dbca` en modo silencioso para crear la base de datos contenedora `ORCL` (CDB) junto con la Pluggable Database inicial `PDB1`. (Podemos modificar parametros como totalMemory a los requerimientos del sistema, en este caso lo e dejado 3GB ya que la ram maxima del sistema son 4)

```
sudo su - oracle -c '$ORACLE_HOME/bin/dbca -silent -createDatabase \
  -templateName General_Purpose.dbc \
  -gdbname ORCL -sid ORCL \
  -createAsContainerDatabase true \
  -numberOfPDBs 1 -pdbName PDB1 \
  -sysPassword <PASSWORD> \
  -systemPassword <PASSWORD> \
  -pdbAdminPassword <PASSWORD> \
  -storageType FS \
  -datafileDestination /u01/oradata \
  -recoveryAreaDestination /u01/fast_recovery_area \
  -recoveryAreaSize 10240 \
  -characterSet AL32UTF8 \
  -nationalCharacterSet AL16UTF16 \
  -memoryMgmtType AUTO_SGA \
  -totalMemory 3072 \
  -emConfiguration NONE \
  -ignorePrereqFailure'

```

```
[INSERTA AQUÍ LA SALIDA DEL COMANDO EN TU TERMINAL]

```

## 4. Configuración de Red TNS y Parámetros del SPFILE

### Configuración de tnsnames.ora

Creamos el archivo `$ORACLE_HOME/network/admin/tnsnames.ora` definiendo los alias de red locales para facilitar la resolución de nombres de la CDB (`ORCL`) y de la PDB (`PDB1`).

```
sudo su - oracle -c 'cat > $ORACLE_HOME/network/admin/tnsnames.ora <<EOF
ORCL =
  (DESCRIPTION =
    (ADDRESS = (PROTOCOL = TCP)(HOST = ora26ai.example.com)(PORT = 1521))
    (CONNECT_DATA =
      (SERVER = DEDICATED)
      (SERVICE_NAME = ORCL)
    )
  )

PDB1 =
  (DESCRIPTION =
    (ADDRESS = (PROTOCOL = TCP)(HOST = ora26ai.example.com)(PORT = 1521))
    (CONNECT_DATA =
      (SERVER = DEDICATED)
      (SERVICE_NAME = PDB1)
    )
  )
EOF'

```

Validamos la resolución de los alias TNS creados:

```
sudo su - oracle -c 'tnsping ORCL'
sudo su - oracle -c 'tnsping PDB1'

```

```
[INSERTA AQUÍ LA SALIDA DEL COMANDO EN TU TERMINAL]

```

### Verificación y ajuste de parámetros en el SPFILE

Accedemos a la instancia mediante `sqlplus` para auditar los parámetros de arranque guardados en el `SPFILE`, registrar los servicios y guardar el estado de apertura automática de la PDB.

```
sudo su - oracle -c 'sqlplus / as sysdba'
-- Comprobar que la instancia ha arrancado utilizando un archivo SPFILE
SHOW PARAMETER spfile;

-- Consultar parámetros de nombre de BD, nombre único de instancia y servicios
SHOW PARAMETER db_name;
SHOW PARAMETER db_unique_name;
SHOW PARAMETER service_names;

-- Registrar los servicios explícitamente en el SPFILE para el Listener
ALTER SYSTEM SET service_names='ORCL','PDB1' SCOPE=BOTH;

-- Guardar el estado de la PDB1 para que se abra automáticamente al iniciar la CDB
ALTER PLUGGABLE DATABASE PDB1 SAVE STATE;
EOF

```

```
[INSERTA AQUÍ LA SALIDA DEL COMANDO EN TU TERMINAL]

```

## 5. Automatización del Arranque del Servicio (`systemd`)

Para asegurar el arranque y parada automática de la base de datos y del Listener con el sistema operativo:

1. Editamos el archivo `/etc/oratab` sustituyendo el indicador `N` por `Y` en la entrada correspondiente a la instancia `ORCL`.

```
sudo sed -i 's|^ORCL:\(.*\):N$|ORCL:\1:Y|' /etc/oratab
grep ^ORCL /etc/oratab

```

```
[INSERTA AQUÍ LA SALIDA DEL COMANDO EN TU TERMINAL]

```

2. Creamos la unidad de servicio `systemd` en `/etc/systemd/system/oracle-db.service`:

```
sudo tee /etc/systemd/system/oracle-db.service <<'EOF'
[Unit]
Description=Oracle Database 26ai Service
After=network.target

[Service]
Type=forking
RemainAfterExit=yes
User=oracle
Group=oinstall
Environment="ORACLE_BASE=/u01/app/oracle"
Environment="ORACLE_HOME=/u01/app/oracle/product/26.0.0/dbhome_1"
Environment="ORACLE_SID=ORCL"
ExecStart=/u01/app/oracle/product/26.0.0/dbhome_1/bin/dbstart /u01/app/oracle/product/26.0.0/dbhome_1
ExecStop=/u01/app/oracle/product/26.0.0/dbhome_1/bin/dbshut /u01/app/oracle/product/26.0.0/dbhome_1
TimeoutStartSec=600
TimeoutStopSec=600
LimitNOFILE=65536
LimitNPROC=16384
LimitMEMLOCK=infinity

[Install]
WantedBy=multi-user.target
EOF

```

3. Recargamos la configuración de `systemd`, habilitamos e iniciamos el servicio:

```
sudo systemctl daemon-reload
sudo systemctl enable oracle-db.service
sudo systemctl start oracle-db.service
sudo systemctl status oracle-db.service

```

```
[INSERTA AQUÍ LA SALIDA DEL COMANDO EN TU TERMINAL]

```

## 6. Verificación Final de Conectividad Local

Por último, comprobamos la conectividad usando los alias definidos en `tnsnames.ora` hacia la CDB y la PDB:

```
sudo su - oracle -c 'sqlplus system/<PASSWORD>@ORCL' <<'EOF'
SELECT name, open_mode, cdb FROM v$database;
EXIT;
EOF

sudo su - oracle -c 'sqlplus system/<PASSWORD>@PDB1' <<'EOF'
SELECT name, open_mode FROM v$pdbs;
EXIT;
EOF

```

```
[INSERTA AQUÍ LA SALIDA DEL COMANDO EN TU TERMINAL]

```
