# TFG_NLP_2024 
Manual de Uso 
Extracción de Datos en Historia Clínica

El modelo de NLP está integrado e incluido en la carpeta del trabajo. Esta carpeta está compuesta por 2 carpetas a su vez, en las que se almacenan los datos en crudo (carpeta Datos) y los datos ya extraídos (carpeta Clasificación). 
En primer lugar, debemos instalar Python como intérprete de código y asignarlo al PATH de variables de entorno de nuestro ordenador. Se recomienda descargar la versión 3.10.10 que es con la que se ha implementado el modelo. 

Python_version_3.10.10 Windows installer (64bit)
Python_version_3.10.10 MacOS installer (64 bit) 
Agregar Python al path de Windows 10 (kyocode.com)
How to add Python to PATH in macOS (xda-developers.com)

Sea la abreviatura W, el indicador de código para Sistema Operativo Windows y M para Mac.
Es necesario tener instalada el paquete pip de instalación de módulos y dependencias.
W: “python -m pip version” 
M: “python3 -m pip version” 
Si lo tenemos instalado nos aparecerá la versión de pip que tenemos
De no estar instalado:
W: “python -m install pip”
M: “python3 -m install pip --user”

En segundo lugar, debemos instalar los módulos y librerías que emplea el código: 
- Tqdm
W: “python -m pip install tqdm”
M: “python3 -m pip install tqdm --user”
-Pandas 
W: “python -m pip install pandas”
M: “python3 -m pip install pandas –user”
-bs4 
W: “python -m pip install bs4”
M: “python3 -m pip install bs4 --user”
-spacy
W: “python -m pip install spacy”
M: “python3 -m pip install spacy --user”
-datefinder 
W: “python -m pip install datefinder”
M: “python3 -m pip install datefinder --user”
-xlrd 
W: “python -m pip install xlrd”
M: “python3 -m pip install xlrd --user”
-openpyxl
W: “python -m pip install openpyxl”
M: “python3 -m pip install openpyxl --user”
Eso es todo lo que debemos hacer previamente a la ejecución del código.	

A continuación, abrimos el terminal del dispositivo y accedemos al directorio donde tengamos descargado la carpeta “CODIGO_TFG_2024”.
Como hemos visto previamente, esta carpeta está compuesta de 2 carpetas más y de tres códigos ejecutables Python. 
Descargamos le Excel con los datos que queremos extraer y lo metemos en la carpeta ‘Datos’.  
El primer paso es cambiar el nombre del archivo por uno más corto y sencillo como por ejemplo sep2022, mayo2023. Esto no es estrictamente necesario, pero nos facilitará mucho el trabajo.
Debemos cerciorarnos de que en el Excel se encuentras las Hojas ‘DATOS INFORMES’, escrito en mayúsculas y con un espacio. Es de suma importancia que los nombres de las hojas coincidan. Del mismo modo para la hoja ‘EVOLUTIVOS’.
Además, debemos verificar que para la hoja ‘DATOS INFORMES’ las columnas ‘PACIENTES’, ‘DESCR_LARGA’ y ‘VALOR’ están situadas de forma contigua. Es posible que no tengan esos nombres exactamente, pero es fundamenta que estén en ese orden.



Del mismo modo para ‘EVOLUTIVOS’ donde ‘PACIENTE’, ‘ESPECIALIDAD’ y ‘ANOTACION’ están dispuestas en ese orden. La columna ‘FECHA’ debe tener ese nombre sin importar el lugar de la tabla en el que esté. 



Una vez verificados estos títulos de columnas, podemos ejecutar el código. 
El código que debemos ejecutar es TFG_ALBERTO_2024.py y recibe como argumento el nombre del Excel que queremos extraer con el prefijo del formato de Excel que es. Por ejemplo sep2022.xls o mayo2023.xlsx. El formato puede verse al abrir el Excel en la pantalla flotante que aparece antes de iniciarse y ver su contenido. 
NOTA: Es imprescindible cerrar el Excel con los datos en crudo antes de ejecutar el código dado que este último accede al Excel. Si el archivo está abierto nos saltará un error.
En el terminal situándose en la carpeta ‘CODIGO_TFG_2024’:
W: “python TFG_ALBERTO_2024 <nombre de Excel y formato>”
M: “python3 TFG_ALBERTO_2024 <nombre de Excel y formato>”
Ejemplo: 
W: “python TFG_ALBERTO_2024 mayo2023.xlsx“
M: “python3 TFG_ALBERTO_2024 mayo2023.xlsx”

Nada más ejecutar el código nos aparecerá una barra de progreso en la que veremos cuánto falta para terminar de ejecutarse. Una vez terminado de ejecutarse nos aparecerá el tiempo que ha tardado y se abrirá automáticamente el Excel con los datos extraídos. 

Este Excel se guarda en la carpeta ‘Clasificacion’ y se le asigna el nombre: 
“<nombre de Excel y formato sin extraer>_resultados_<fecha y hora actual>
Ejemplo: mayo2023.xlsx_resultados_2024-04-24-11-40-23 
De esta manera podemos identificar rápidamente de que Excel provienen los resultados y el instante en el que lo obtuvimos. 
Podemos ejecutar el código cuantas veces queramos y los datos no se sobrescribirán dado que a cada ejecución se asigna un nombre de fichero distinto. 


