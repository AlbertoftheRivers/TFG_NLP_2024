#coding=utf-8

''' Author: Albert de los Ríos Salmerón
    mail: delosrios.salmeron.alberto@gmail.com
    Date: 2024-04-24
    Tutoras: Carolina de la Pinta, Maria Elena Hernando
    Colaboración con el Servicio de Oncología Radioterápica del Hospital Universitario Ramón y Cajal
'''
import logging
import pandas as pd
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
import json
import warnings
import numpy
import os
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def datos_excel(file):

    try:
        datos_excel_original_DI = pd.read_excel('Datos' + '/' + file, sheet_name='DATOS INFORME')
        datos_excel_DI = datos_excel_original_DI.iloc[:, [2, 3, 4]].copy()
        nombre_columnas_DI = ['PACIENTE', 'DESCR_LARGA', 'VALOR']
        datos_excel_DI.columns = nombre_columnas_DI

        datos_excel_original_E = pd.read_excel('Datos' +'/' + file, sheet_name='EVOLUTIVOS') 
        datos_excel_E = datos_excel_original_E.iloc[:, [2, 3, 4]].copy()
        datos_excel_E['FECHA'] = datos_excel_original_E['FECHA']
        nombre_columnas_E = ['PACIENTE', 'ESPECIALIDAD', 'ANOTACION','FECHA']
        datos_excel_E.columns = nombre_columnas_E

    except:
        logger.info('dataframe originales extraídos erróneamente')

    #ELIMINACIÓN DE CARACTERES HTML Y REEMPLAZO POR CARACTERES CORRECTOS
    try: 
        diccionario_replace = {
            '&aacute;': 'á',
            '&Aacute;': 'Á',
            '&eacute;': 'é',
            '&Eacute;': 'É',
            '&iacute;': 'í',
            '&Iacute;': 'Í',
            '&oacute;': 'ó',
            '&Oacute;': 'Ó',
            '&uacute;': 'ú',
            '&Uacute;': 'Ú',
            '&ntilde;': 'ñ',
            '&Ntilde;': 'Ñ',
            '&nbsp;': ' ',
            '&ordm;': 'º',
            '&ordf;': 'ª',
            '&micro;': 'µ',
            '&lt;': '<',
            '&gt;': '>',
            '&frac12;': '½',
            '&uuml;': 'ü',
            '&Uuml;': 'Ü',
            '&middot;': '·',
            '&iquest;': '¿',
            '&deg;': 'º',
            '&iexcl;': '!',
            '&Acirc;': 'Â',
            '&acute;': '´',
            '&ccedil;': 'ç',
            '&Ccedil;': 'Ç',
            '&sup3;': '³',
            '&Euml;': 'Ë',
            '&uml;': '¨'
        }

        datos_excel_DI['VALOR'] = datos_excel_DI['VALOR'].apply(lambda x: filtrar_resultados(x, diccionario_replace))
        datos_excel_E['ANOTACION'] = datos_excel_E['ANOTACION'].apply(lambda x: filtrar_resultados(x, diccionario_replace))
        datos_excel_DI.dropna(subset=['VALOR'], inplace=True)
        datos_excel_E.dropna(subset=['ANOTACION'], inplace=True)

    except:
        logger.info('Error en la corrección de caracteres')
        
        #EXTRACCION DATOS DATOS INFORMES
    try:      
    
        df = pd.DataFrame(data = datos_excel_DI)

        Categorias = ['Historia Oncología Radioterápica']
        df_filtrado = df[df['DESCR_LARGA'].isin(Categorias)]
        df_HOR = df_filtrado[df_filtrado['DESCR_LARGA'] == 'Historia Oncología Radioterápica'].drop_duplicates(subset='PACIENTE',keep='last')
        indice_cat = df_HOR.set_index("DESCR_LARGA")
        d = []
        for i in Categorias:
            cat = indice_cat.loc[[i],['VALOR','PACIENTE']]
            d.append(cat)
        tabla_DI = pd.concat(d)

        #EXTRACCIÓN DATOS EN FORMATO XML 

        DI =[]  
        for index, row in tabla_DI.iterrows():
            bs1 = BeautifulSoup(row['VALOR'], 'html.parser')
            bs_txt1 = bs1.get_text(separator=' ', strip=True)
            DI.append(bs_txt1)
        tabla_DI['VALOR'] = DI
        tabla_DI.to_csv('Datos/datos_HCO_pacientes.csv', encoding='utf-8', index=False, header=True)
        
    except:
        logger.info('El archivo Excel no se encuentra en la ruta especificada.')

    warnings.filterwarnings('ignore', category=MarkupResemblesLocatorWarning)
 
        #EXTRACCION DATOS DATOS INFORMES
    try:
    
        df1 = pd.DataFrame(data = datos_excel_E)

        df_ONR = df1[df1['ESPECIALIDAD'] == 'ONR'].copy()
       
        #EXTRACCIÓN DATOS EN FORMATO XML 

        DE =[]
        for index, row in df_ONR.iterrows():
            bs = BeautifulSoup(row['ANOTACION'], 'html.parser')
            bs_txt = bs.get_text(separator=' ', strip=True)
            DE.append(bs_txt)
        df_ONR['ANOTACION'] = DE
        tabla_DE = df_ONR[['ANOTACION','FECHA','PACIENTE']].drop_duplicates(keep='last') #Si quiero poner pacientes, solo tengo que añadir 'PACIENTES' igual en datos_informes
        tabla_DE.to_csv("Datos/evolutivos_ONR_pacientes.csv", encoding='utf-8', index=False, header=True)
        

    except:
       logger.info('El método evolutivo() presenta algún error.')

        #CREACION ARCHIVO JSONL QUE INTERPRETA EL MODELO NLP

def csv_jsonl():
    try: 
        nombre = ['datos_HCO','evolutivos_ONR']
        for file in nombre:
            archivos_csv = pd.read_csv('Datos' +'/' + file +'_pacientes.csv')
            if 'VALOR' or 'ANOTACION' in archivos_csv.columns:
                archivos_csv = archivos_csv.rename(columns={'VALOR':"text",'ANOTACION':"text"})
                with open('Datos' +'/' + file +'_pacientes.jsonl','w', encoding='utf-8') as jsonl:                
                    for _, row in archivos_csv.iterrows():   #no lo pilla a menos que se ponga como un diccionario. for _, row archivo_csv.iterrows(): pero te sale en el jsonl 1ªfila:2ªfila/ 1ªfila:3ªfila. Esto pasa si le quitas el título a la columna del dataframe, coge el contenido de la primera columna como título.
                        archivos_json = row.to_dict()   #SI ESTÁ BIEN PERO COMO EL DATAFRAME NO TIENE NOMBRE DE COLUMNAS, PONE LA PRIMERA FILA COMO SI FUESE EL NOMBRE. HAY QUE PONER ALGO EL ERROR ESTÁ EN LA CREACIÓN DE LOS CSV
                        jsonl.write(json.dumps(archivos_json, ensure_ascii=False, ) +'\n')
            os.remove('Datos' +'/' + file +'_pacientes.csv')
            
        
    except:
        logger.info('Los archivos csv no han sido leidos correctamente')

            # METODO PARA FILTRAR DATOS 
def filtrar_resultados(df,diccionario): 
    try:
        if isinstance(df, str):
            for original, modificado in diccionario.items():
                df = df.replace(original, modificado)

            return df
    except:
       logger.info('Método replace para filtrar resultados presenta error')



            
