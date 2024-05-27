#coding=utf-8

''' Author: Albert de los Ríos Salmerón
    mail: delosrios.salmeron.alberto@gmail.com
    Date: 2024-04-24
    Tutoras: Carolina de la Pinta, Maria Elena Hernando
    Colaboración con el Servicio de Oncología Radioterápica del Hospital Universitario Ramón y Cajal
'''
import time
import logging
from tqdm import tqdm
import extraccion_HCO_pacientes
import resultados
import sys
import datetime


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

inicio = time.time()
file=sys.argv[1]
print('El codigo ha sido ejecutado correctamente, el proceso tardará unos minutos')
with tqdm(total=5, desc='Progresión de ejecución del código',unit='fichero') as prog:

    extraccion_HCO_pacientes.datos_excel(file=file)
    time.sleep(1)
    prog.update(1)
    time.sleep(1)

    extraccion_HCO_pacientes.csv_jsonl()
    time.sleep(1)
    prog.update(1)
    time.sleep(1)

    df,df_evo = resultados.datos_informes_excel()
    time.sleep(1)
    prog.update(1)
    time.sleep(1)

    hora = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    titulo = 'Clasificacion' +'\\'+ file +'_resultados_'+ hora +'.xlsx'
    
    resultados.guardar_excel(df=df,df_evo=df_evo, titulo=titulo)
    time.sleep(1)
    prog.update(1)
    time.sleep(1)

    prog.update(1)
    time.sleep(1)
    
print('El Excel se abrirá automáticamente, puede también encontrarlo en la carpeta Clasificación')
resultados.show_excel(titulo=titulo)
time.sleep(1)
    

final = time.time()

print(str(final-inicio) + ' segundos en ejecutar todo el código')


