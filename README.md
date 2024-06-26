##ESPAÑOL

The User Manual is translated to English below the Spanish version.

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

-Tqdm

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

![image](https://github.com/AlbertoftheRivers/TFG_NLP_2024/assets/170938834/4e5ebb24-7132-4ce0-a0e7-0b2e7f0043a2)

Del mismo modo para ‘EVOLUTIVOS’ donde ‘PACIENTE’, ‘ESPECIALIDAD’ y ‘ANOTACION’ están dispuestas en ese orden. La columna ‘FECHA’ debe tener ese nombre sin importar el lugar de la tabla en el que esté. 

![image](https://github.com/AlbertoftheRivers/TFG_NLP_2024/assets/170938834/b2c830b0-815a-4896-bb04-0c6035f825cb)

Una vez verificados estos títulos de columnas, podemos ejecutar el código. 
El código que debemos ejecutar es TFG_ALBERTO_2024.py y recibe como argumento el nombre del Excel que queremos extraer con el prefijo del formato de Excel que es. Por ejemplo sep2022.xls o mayo2023.xlsx. El formato puede verse al abrir el Excel en la pantalla flotante que aparece antes de iniciarse y ver su contenido. 


NOTA: Es imprescindible cerrar el Excel con los datos en crudo antes de ejecutar el código dado que este último accede al Excel. Si el archivo está abierto nos saltará un error.
En el terminal situándose en la carpeta ‘CODIGO_TFG_2024’:
W: “python TFG_ALBERTO_2024.py <nombre de Excel y formato>”
M: “python3 TFG_ALBERTO_2024.py <nombre de Excel y formato>”

Ejemplo: 
W: “python TFG_ALBERTO_2024.py mayo2023.xlsx“
M: “python3 TFG_ALBERTO_2024.py mayo2023.xlsx”

Nada más ejecutar el código nos aparecerá una barra de progreso en la que veremos cuánto falta para terminar de ejecutarse. Una vez terminado de ejecutarse nos aparecerá el tiempo que ha tardado y se abrirá automáticamente el Excel con los datos extraídos. 


Este Excel se guarda en la carpeta ‘Clasificacion’ y se le asigna el nombre: 
“<nombre de Excel y formato sin extraer>_resultados_<fecha y hora actual>

Ejemplo: mayo2023.xlsx_resultados_2024-04-24-11-40-23 


De esta manera podemos identificar rápidamente de que Excel provienen los resultados y el instante en el que lo obtuvimos. 
Podemos ejecutar el código cuantas veces queramos y los datos no se sobrescribirán dado que a cada ejecución se asigna un nombre de fichero distinto. 

Para ejecutar el código confusion_matrix.py como argumento hay que indicar el path del modelo empleado, el fichero jsonl con los datos anotados y el nombre de la carpeta donde queremos que se guarde a la matriz de confusion multivariable creada. 


##ENGLISH

User Manual for Data Extraction from Clinical Records
The NLP model is integrated and included in the project folder. This folder consists of two subfolders: one storing raw data (Data folder) and the other containing the extracted data (Classification folder).

First, we need to install Python as the code interpreter and add it to the PATH of our computer’s environment variables. It is recommended to download version 3.10.10, which is the version used to implement the model.

Python_version_3.10.10 Windows installer (64bit)

Python_version_3.10.10 MacOS installer (64 bit)

Adding Python to PATH in Windows 10

How to add Python to PATH in macOS

Let W be the abbreviation for Windows OS and M for Mac. It is necessary to have the pip package installed for module and dependency installation.

W: python -m pip version
M: python3 -m pip version

If pip is installed, the version will be displayed. If not:

W: python -m pip install pip
M: python3 -m pip install pip --user

Next, we need to install the modules and libraries used by the code:

Tqdm

W: python -m pip install tqdm

M: python3 -m pip install tqdm --user

Pandas

W: python -m pip install pandas

M: python3 -m pip install pandas --user

bs4

W: python -m pip install bs4

M: python3 -m pip install bs4 --user

spacy

W: python -m pip install spacy

M: python3 -m pip install spacy --user

datefinder

W: python -m pip install datefinder

M: python3 -m pip install datefinder --user

xlrd

W: python -m pip install xlrd

M: python3 -m pip install xlrd --user

openpyxl

W: python -m pip install openpyxl

M: python3 -m pip install openpyxl --user

This is all we need to do before running the code.

Next, open the terminal and navigate to the directory where you downloaded the folder "CODIGO_TFG_2024". As previously mentioned, this folder consists of two subfolders and three executable Python scripts. Download the Excel file with the data you want to extract and place it in the 'Data' folder.

The first step is to rename the file to something shorter and simpler, such as sep2022 or mayo2023. This is not strictly necessary but will make the work easier. Ensure that the Excel file contains the sheets named 'DATOS INFORMES' (in uppercase with a space). It is crucial that the sheet names match exactly. Similarly for the 'EVOLUTIVOS' sheet. Additionally, verify that for the 'DATOS INFORMES' sheet, the columns 'PACIENTES', 'DESCR_LARGA', and 'VALOR' are contiguous. They might not have exactly these names, but it is crucial that they are in this order.

Ensure the same for 'EVOLUTIVOS' where 'PACIENTE', 'ESPECIALIDAD', and 'ANOTACION' are arranged in this order. The 'FECHA' column must have this name regardless of its position in the table.

Once these column titles are verified, we can run the code. The code to execute is TFG_ALBERTO_2024.py and it takes as an argument the name of the Excel file to extract, with its format prefix. For example, sep2022.xls or mayo2023.xlsx. The format can be seen by opening the Excel file in the floating screen that appears before starting and viewing its contents.

NOTE: It is essential to close the Excel file with raw data before running the code since the code accesses the Excel file. If the file is open, an error will occur. In the terminal, navigate to the ‘CODIGO_TFG_2024’ folder:

W: python TFG_ALBERTO_2024 <filename>
M: python3 TFG_ALBERTO_2024 <filename>

Example:

W: python TFG_ALBERTO_2024.py mayo2023.xlsx
M: python3 TFG_ALBERTO_2024.py mayo2023.xlsx

Upon executing the code, a progress bar will appear, showing the remaining time for completion. Once finished, the execution time will be displayed, and the Excel file with the extracted data will open automatically.

This Excel file is saved in the 'Classification' folder and named as follows:

Example: mayo2023.xlsx_resultados_2024-04-24-11-40-23
This way, we can quickly identify which Excel file the results come from and when they were obtained. The code can be executed as many times as needed, and the data will not be overwritten as each execution is assigned a different file name.

To execute the code confusion_matrix.py, the path of the used model, the jsonl file with the annotated data, and the name of the folder where we want to save the created multivariable confusion matrix must be indicated as arguments.
