#coding=utf-8

''' Author: Albert de los Ríos Salmerón
    mail: delosrios.salmeron.alberto@gmail.com
    Date: 2024-04-24
    Tutoras: Carolina de la Pinta, Maria Elena Hernando
    Colaboración con el Servicio de Oncología Radioterápica del Hospital Universitario Ramón y Cajal
'''

import spacy 
import json
import pandas as pd
import logging
import subprocess
import platform
import datefinder
import datetime
import numpy as np
import os 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#DESCARGA MODELO NLP PARA USARLO
nlp = spacy.load('Datos/modelo_NLP_TFG_2024/model-last')


def datos_informes_excel():

    labels_informes = ['SEX','AGE','AP','PRIM','MET','LOC_M','DOSIS','DOSIS_D','INI_RT','FIN_RT']

    #EXTRACCION DATOS FICHERO datos_HCO_pacientes.jsonl con datos de Historias Clínicas
    try:
        rows = []
        with open("Datos/datos_HCO_pacientes.jsonl", 'r', encoding='utf-8') as archivo:
            for line in archivo:
                HCO = json.loads(line)
                texto =HCO['text']

                # Procesa el texto y obtenie las entidades
                doc = nlp(texto)

                # Buscamos los códigos de los pacientes
                paciente = HCO.get('PACIENTE')

                # Generamos un array con el contenido de los labels para cada paciente
                row = [paciente] + [procesar_label(label, doc) for label in labels_informes]
                rows.append(row)

        df = pd.DataFrame(rows, columns=['PACIENTE'] + labels_informes)
        df.replace('', pd.NA, inplace=True)
        #os.remove('Datos/datos_HCO_pacientes.jsonl') # COMENTAR ESTA LINEA PARA EXTRAER LOS ARCHIVOS A ANOTAR

    except:
        logger.info('El archivo excel no ha sido creado correctamente')

    recist = ['RC','RP','EE','PG']
        
    #EXTRACCION DATOS FICHERO evolutivos_ONR_pacientes.jsonl con datos de los Evolutivos
    try:
        rows = []
        with open("Datos/evolutivos_ONR_pacientes.jsonl", 'r', encoding='utf-8') as archivo_evo:
            for line in archivo_evo:
                EVO = json.loads(line)
                texto = EVO['text']
                doc = nlp(texto)

                paciente_evo = EVO.get('PACIENTE')
                fecha_evo = EVO.get('FECHA')

                row= [paciente_evo] + [fecha_evo] + [procesar_label(label,doc) for label in recist] + [procesar_label(label,doc) for label in labels_informes]
                rows.append(row)
            
        df_evo = pd.DataFrame(rows, columns =['PACIENTE'] + ['FECHA'] + recist + labels_informes).drop_duplicates(subset=['PACIENTE','FECHA'], keep='last')
        df_evo['labels'] = df_evo[recist].apply(lambda row: ''.join(row), axis=1)
        df_evo.replace('', pd.NA, inplace=True)
        df_evo = df_evo.sort_values(by=['PACIENTE', 'FECHA'], ascending=[False, False])
        #os.remove('Datos/evolutivos_ONR_pacientes.jsonl') # COMENTAR ESTA LINEA PARA EXTRAER LOS ARCHIVOS A ANOTAR
 
    except:
        logger.info('evolutivos extraidos de manera erróneas')

    try: 
        #RELLENO DE COLUMNAS DE DF CON DATOS DF_EVO, DATOS DE DF TIENE PRIORIDAD
        for _, paciente_row in df.iterrows():
            paciente = paciente_row['PACIENTE'] # pacientes de df
            paciente_evo = df_evo[df_evo['PACIENTE'] == paciente] #paciente de df_evo
        
            for fecha in paciente_evo['FECHA']:
                reciente = paciente_evo[paciente_evo['FECHA'] == fecha].iloc[0]#identificar fechas mñas recientes de df_evo con pacientes iguales a df

                for col in labels_informes:
                    if pd.isna(paciente_row[col]) and reciente[col] is not pd.NA: 
                        df.at[_, col] = reciente[col] #relleno de df con valores de df_evo cuando df is NA y df_evo no lo es para la fecha más reciente. Si en la fecha no hay datos se pasa al siguiente.

        df_evo = df_evo.drop(columns =['SEX','AGE','AP','PRIM','MET','LOC_M','DOSIS','DOSIS_D','INI_RT','FIN_RT']) #AÑADIR EL DROP COLUMNAS RC,RP,EE,PG  ¿Se puede poner df_evo = df_evo.drop(columns =[recist, label_informes])?

        for col in ['INI_RT','FIN_RT']:
            df[col] = df[col].apply(fechas_RT)

    except:
        logger.info('Dataframe df completa con datos de df_evo de forma errónea')

    try:
        df_merged = pd.merge(df[['PACIENTE','INI_RT','FIN_RT']], df_evo[['PACIENTE','FECHA','labels']], on='PACIENTE')
        df_merged['FECHA'] = pd.to_datetime(df_merged['FECHA'], errors='coerce') 

        for col in ['INI_RT','FIN_RT']:
            df_merged[col] = pd.to_datetime(df_merged[col], errors='coerce')
            fechas_no_null = df_merged[col].notnull()
            df_merged.loc[fechas_no_null,'INTER_'+ col] = (df_merged['FECHA'] - df_merged[col]).dt.days
    
    
        for col in ['FECHA', 'INI_RT', 'FIN_RT']:
            df_merged[col] = df_merged[col].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else '')
        
    except:
        logger.info('Intervalos entre fechas de evolutivos y fechas de RT extraidas de manera errónea')

                
    try:  

        labels_evo = ['1M','3M','6M','1A']
        for evo in labels_evo:
            df[evo] = ''
        #intervalos temporales filtrado de evolutivos
        df_merged = df_merged.dropna(subset=['labels'], how='all')
        df_merged = df_merged.dropna(subset=['INTER_INI_RT', 'INTER_FIN_RT'], how='all')
        df_merged = df_merged[df_merged['INTER_FIN_RT'].between(0, 420)]
        df_merged = df_merged[df_merged['INTER_FIN_RT'].between(30, 450)]

    
        for index, row in df_merged.iterrows():
            paciente = row['PACIENTE']
            inter_fin_rt = row['INTER_FIN_RT']
            inter_ini_rt = row['INTER_INI_RT']
            label = row['labels']

        # Verifica si INTER_FIN_RT existe y aplica las condiciones temporales correspondientes
            if not pd.isnull(inter_fin_rt):
                if inter_fin_rt <= 89:
                    df.loc[df['PACIENTE'] == paciente, '1M'] = label
                elif 90 <= inter_fin_rt <= 179:
                    df.loc[df['PACIENTE'] == paciente, '3M'] = label
                elif 180 <= inter_fin_rt <= 269:
                    df.loc[df['PACIENTE'] == paciente, '6M'] = label
                elif 270 <= inter_fin_rt <= 420:
                    df.loc[df['PACIENTE'] == paciente, '1A'] = label
        # Verifica si INTER_FIN_RT no existe pero INTER_INI_RT sí y aplica las condiciones temporales correspondientes
            elif not pd.isnull(inter_ini_rt):
                if 30 <= inter_ini_rt <= 119:
                    df.loc[df['PACIENTE'] == paciente, '1M'] = label
                elif 120 <= inter_ini_rt <= 209:
                    df.loc[df['PACIENTE'] == paciente, '3M'] = label
                elif 210 <= inter_ini_rt <= 299:
                    df.loc[df['PACIENTE'] == paciente, '6M'] = label
                elif 300 <= inter_ini_rt <= 450:
                    df.loc[df['PACIENTE'] == paciente, '1A'] = label

    except:
        logger.info('Error condiciones criterios recist periodo de observación')

        #DICCIONARIO DE ELEMENTOS EXTRAIDOS, REAGRUPADOS EN GRUPOS DETERMINADOS
    try:
        diccionario_replace = {'SEX': {('hombre','VARON','HOMBRE','varón','Várón','Váron','Varon','Varón'):'Hombre',('mujer','MUJER','diagnosticada','La paciente','Diagnosticada','Diagnsoticada'):'Mujer',('Diagnosticado','diagnosticado','remitido','74 años','El paciente','45 años','75 años'):''},
                            'AP': {('carcinoma','Carcinoma seroso de','carcinoma de células pequeñas','Ca epidermoides','carcinoma ductal','CARCINOMA','CARCINOMA DUCTAL INFILTRANTE','ca. neuroendocrino','CARCINOMA DUCTAL INFILTRANTE','Carcinoma ductal infiltrante','Carcinoma ductal infiltrante','Carcinoma ductal infiltrante','carcinoma epidermoide','carcinoma adenoescamoso','ca. adenoescamoso','adenocaricnoma','carcinoma epidermoide infiltrante','CARCINOMA DUCTAL INFILTRANTE','Carcinoma ductal infiltrante','carcinoma ductal infiltrante','Ca. epidermoide','Carcinoma','Carcinoma ductal infiltrante','Carcinoma endometrioide','Carcinoma infiltrante','Carcinoma adenoide quístico','carcinoma broncogénico','carcinoma de célula pequeña','carcinoma ducal infiltrante','Ca epidermoide','carcinoma de células no pequeñas','Carcinoma adenoescamoso','Carcinoma de células escamosas','carcinoma de células  no pequeñas','carcinoma indiferenciado','ca. epidermoide','carcinoma no microcítico','CDI','carcinoma de','ca. escamos','carcinoma epidemoide','Carcinoma de células','carcinoma lobulillar infiltrante','carcinomas','carcinoma microcítico','ca.epidermoide','Carcinoma broncogénico epidermoide','Carcinoma broncogénico','Carcinoma epidermoide','carcinoma de células escamosas','Carcinoma epidermoide infiltrante','ca epidermoide moderadamente diferenciado','CARCINOMA BRONCOGENICO','ca epidermoide','ca. epidermoide infiltrante','Ca lobulillar infiltrante','carcinoma broncogenico','caricnoma','Ca edometroide','Carcinoma ductal','carcinoma epidermoide moderadamente diferenciado','Carcinoma ductal infiltrante','carcinoma pobremente diferenciado','carcinoma de celulas escamosas','Ca broncogénico','carcinoma escamoso','CARCINOMA DUCTAL INFILTRANTE','ca ductal infiltrante','colangiocarcinoma','colangicarcinoma'):'Carcinoma',('adenocarcinoma','Adenocarcinoma bien diferenciado','adenocarcinoma moderadamente diferenciado','adenocarcinoma infiltrante','Adenocarcinoma moderadamente diferenciado','adenocarcinoma bien diferenciado','adenocarcinoma coloide','Adenocarcinoma infiltrante','ADC','adenocarcinoma ductal bien diferenciado','adenocarcinoma ductal infiltrante','Adenocarcinoma acinar','adenocarcinomas','AC','adenocarcinoma endometrioide','adenocarcinoma infiltrante bien diferenciado','Adenocarcinoma papilar'):'Adenocarcinoma',('melanoma','melanoma maligno'):'Melanoma',('hepatocarcinoma','HEPATOCARCINOMA','carcinoma hepatocelular','Carcinoma hepatocelular','colangiohepatocarcinoma',):'Hepatocarcinoma',('Carcinosarcoma','Liposarcoma mixoide','Sarcoma','Liposarcoma','rabdomiosarcoma alveolar','Osteosarcoma','liposarcoma bien diferenciado','angiosarcoma'):'Sarcoma',('mesotelioma maligno'):'Mesotelioma',('glioblastoma'):'Glioblastoma',('meningioma'):'Meningioma',('Neurinoma'):'Neurinoma',('hemangiopericitoma'):'Hemangiopericitoma',('mioepitelioma maligno'):'Mioepitelioma',('linfoma'):'Linfoma',('Adenoma','microadenoma','adenoma'):'Adenoma',('Schwannoma'):'Schwannoma',('Hemangioblastoma'):'Hemangioblastoma',('oligodendroglioma'):'Oligodendroglioma',('neurofibroma'):'Neurofibroma',('fibrohistiocitoma'):'Fibrohistocitoma',('Carcinoma seroso de alto grado. La lesión expresa de forma difusa p53','sugestivo de recidiva tumoral','metastasico','neoplasia maligna','glioneuronal anaplásico'):''},
                            'PRIM': {('pulmón','ca. microcítico de pulmón','Lesión pulmonar en LSI','nódulo de pulmón','tumor de pulmón derecho','Ca LSD','LID sugestivos de tumoración primaria','pulmón LSD','neoformación pulmonar derecha','LSD pulmón','PULMON','ca. de pulmón','tumor pulmón entre el','pulmón en LSD','pulmonar en LII','pulmonar','ca pulmón','CA de pulmón','Ca de pulmón','pulmón derecho','tumoración pulmonar primaria','neoplasia pulmonar','LSD','Ca. de pulmón','pulmón de LII','neoplásico primario pulmonar','Lesiones en LSI sugestivas de','neoplasia primaria de pulmón','ca de pulmón','tumor pulmón izquierdo','pulmon','tumor pulmonar primario','primario pulmonar','pulmón dcho','PULMONAR','LSI','LSI','neoplasia de pulmón','CA broncogénico','cáncer de pulmón','neoplasia primaria pulmonar','volumen tumoral en LSI','LID','4 tumores primarios sincrónicos de pulmón','Neoplasia pulmonar en LSI','lesión maligna primaria en segmento posterior del lóbulo superior derecho','neoformación pulmonar','tumoración pulmonar primario','lesión pulmonar en LSI','tumor pulmón entre el 11/2/22','tumor primario pulmonar','LSI altamente sospechoso de tumoración primaria','nódulo pulmoar sugestivo de neoplaisa primaria','primarios pulmonares','tumor pulmón','Neoformación en LSI','Ca pulmón','LSI pulmón','cáncer broncogénico','Ca broncogenico','lóbulo superior izquierdo','neoplasia pulmonar primaria','pumonar','pulmonar en LID','ca. de pulmón izquierdo','Ca pulmonar','origen pulmonar','ca. pulmón'):'Pulmón', ('orofaringe','oído derecho','laringe','glótico','ocular izquierda','hoz frontal derecho','ca. de laringe','amígdala derecha','seno piriforme derecho','cuerdas vocales','órbita derecha','hipófisis','cerebeloso izquierdo','cerebral y seno sagital superior','hoz cerebral','occipital','hemiadenohipofisis izquierda','ala nasal izquierda','lengua','ca lengua','Lesión neoplásica laríngea','transglótico','nervio óptico','seno maxilar izquierdo y órbita izquierda','coroideo','Duramadre','seno transverso derecho','hemicuerpo izquierdo','orofaringe-cavidad oral','parietal derecho','cervical','ca cervical','meningotelial','esfenoideo izquierdo','ca. de seno piriforme derecho','etmoides','T.M. DEL SENO ETMOIDAL','nasofaringe','N.optico izquierdo','papilar'):'CyC',('vértebra L2','femoral derecho','columna lumbar'):'Óseo',('urotelial papilar','urotelial sólido vesical','urotelial de pelvis renal','urotelial izquierdo','Ca urotelial de vejiga','urotelial','urotelial papilar vesical','urotelial vesical','ca urotelial'):'Urotelio',('renal derecho','renal','TUMOR RENAL DERECHO','renales','conductos colectores','conductos de Bellini','suprarrenal izquierdo','Ca. renal','cáncer renal','RENAL'):'Riñón',('de mama izquierda','MAMA IZQUIERDA','mama izquierda','ca. de mama','Ca de mama','"mama izquierda          "','Mama izquierda','Ca de mama izquierdo','ca de mama','Cáncer de mama derecha','mama derecha','mama','cáncer de mama derecha','Ca mama izquierda','ca mama hermana','primario de mama','mamario','cáncer de mama','MD','Ca. de mama','de mama derecha','Ca mama','cilindros Receptor de progesterona'):'Mama',('segmento VII-VIII','SEGMENTOS VIII, VII Y IV','segmento II','neoformación hepática','neoplasia obstructiva a nivel de ángulo hepático','segmento IV','LHD','hígado','LDH','Hepático','intrahepático',):'Hígado',('páncreas','acinar','páncreas ductal','cáncer de páncreas','ca de páncreas','cabeza de páncreas','neoplasia pancreática','pancreático','Tumor neuroendocrino pancreático','neoplasia de páncreas','neoplasia primaria pancreática'):'Páncreas',('neoplasia quística de ovario','ovario'):'Ovario',('sigma','recto-sigma','recto medio-superior','recto medio-superior','neoplasia de colon','NEOFORMACIÓN DE COLON','NEOFORMACIóN DE COLON','neoplasia de recto','NEOPLASIA RECTAL','ángulo hepático colon','Cáncer de colon','NEOPLASIA DE COLON','ca. de recto','recto inferior','recto','cáncer de colon','colon','recto-sigma estadio IIA','CCR','recto superior','colon derecho','recto medio-superior','ca. de colon','ca de colon','colorrectal','neoplasia rectal','neoplasia de sigma estenosante','lesión neoplásica en sigma','neoplásica de sigma','recto medio','recto medio-superior','ca de recto','neoplasia de sigma','colon izquierdo','recto sigma','recto medio-superior'):'CCR',('cutáneo','piel','dermis reticular superficial','muslo','Ca epidermoides cutáneos','dermis reticular profunda','dermis papilar','ca. epidermoide de'):'Piel',('prostático','PROSTATA','próstata','ca de próstata','ca. próstata','cáncer de próstata','prostáta','neoplasia de próstata','ca próstata','Ca de prostata','prostata','ca. de próstata'):'Próstata',('endometrio','Ca endometroide de','neoplasia endometrial'):'Endometrio',('cérvix','cáncer de cérvix'):'Cérvix',('Intestinal','intestino grueso','intestino','tipo intestinal','intestinal','gástrico'):'Gastrointestinal',('tiroides'):'Tiroides',('ca primarios sincrónicos','ca. neuroendocrino','parrilla costal izquierda','neoplasia maligna','neoplasia primaria','Ca células claras','neoplasia estenosante','hemicuerpo izquierdo D8','lesión neoplásica primaria','Ca multicéntrico','concha','músculo pectoral izquierdo','ca. de células escamosas','inferior izquierdo','pleural izquierdo','neuroendocrino','tumor primario sin','axilar izquierdo','ca. adenoescamoso de','ca primarios','axilar izquierdo de','región frontopolar derecha','esófago tipo intestinal','uterina'):''},
                            'MET':{('MTS','METÁSTASIS','METáSTASIS','metastasis','Metástasis','afectación MTX','afectación metastásica','metástasis','progresión','Oligometástasis','oligometástasis','oligometastática','micrometástasis','mtx','única','Lesión única','depósito secundario','metástasis cerebelosa','oligometastásica','metástasis única','afectación','metástasis de','MT','metastásica','metastasica','Progresión','oligoprogresion','Recaída','MACROMETÁSTASIS','metastásico','con mtx','afectación secundaria','enfermedad mestastasica','oligometastásico','Mtx','afectacion','metástasica','afectación metástasica','lesión','Mts oseasa','afectación secundaria','Metátasis óseas','mts','PROGRESIÓN','Metástasis cerebral','Metastasis','lesión única','oligoprogresión','recaída única','afectacion ósea','MTX'):'1',('dos lesiones','dos metástasis cerebrales','dos nódulos pulmonares,','dos lesiones óseas descritas, una lítica y otra esclerosante, ambas concordantes con metástasis','2 lesiones focales parenquimatosas córtico-subcorticales','2 lesiones','2 lesiones pulmonares','2 LOEs','dos pequeñas','Dos','Dos metástasis','2 lesiones compatibles con metástasis'):'2',('Tres nódulos','tres LOES','3 nódulos metastásicos','Tres lesiones','3 lesiones','3 lesiones visibles','tres nodulos','tres lesiones pulmonares'):'3',('afecta a cuatro'):'4',('Cinco lesiones'):'5',('múltiples metástasis','oligomts','Metástasis óseas','Múltiples lesiones','metastásicas','Nuevas lesiones','Múltiples','depósitos secundarios','conglomerado metastásico','metástasis óseas'):'Múltiples',('hepática','recaída','recaída a nivel de la arteria mesentérica en julio de 2020','afecta a','meningioma','lesiones focales óseas líticas','recaída a nivel de adenopatía ','solo 1 con mts','Recaída ósea en','Las del lóbulo inferior recuperan distalmente su calibre y vascularización.Contacta con la aorta, en la superficie medial del cayado, rodeando la porción proximal de la aorta descendente en aproximadamente un 50% de su circunferencia. Cranealmente, ocupa la ventana aorto-pulmonar, y asciende infiltrando la grasa mediastínica en la región prevascular','EE','Nuevas lesiones óseas líticas','afectación osea en','óseas, hepáticas, pulmonares','Afectación','Gnglio estacion 7','1/2 micrometástasis)','coloide','Lesiones focales','hepática SVI, pulmonar LID y LII','recaída a nivel de adenopatía ','recaída a nivel de la arteria mesentérica en julio de 2020'):''},
                            'LOC_M': {('vertebral D10','C1-C2','L1','fémur derecho','lesión ósea sacroilíaca izquierda','T3','sacra','L4','T12 y L1','osea','T2','arco costal a nivel de T5','diáfisis de femur derecho','escápula izquierda','vertebrales','ósea lumbar y en hueso ilíaco','lumbar','vértebra D8','hemivertebra dcha L2 y D7','acetábulo derecho','sacro izquierdo, sacro derecho, pubis derecho y acetábulo izquierdo','7ª costilla','D11 a L5','L3','pélvica','T11 y L1','inguinal dcho','D3D7','ala sacra derecha','óseas escleróticas','T8','T9','clavicula derecha','isquión derecho','acetábulo izquierdo','óseas en hombro izquierdo y acetábulo con ganglio supraclavicular izquierdo','rama isquiopubiana derecha a comprobar','sacro','rama isquiática derecha','isquión','subcapsular','ósea','L4, L2 y T9','manubrio esternal','6º arco costal derecho','óseas','rama isquiopubiana izquierda','ósea en rama isquiática','vertebrales cervicales, dorsales y lumbares','L5-S1','columna vertebral y pelvis','vertebrales cervicales','ósea sacra','ósea en cabeza femoral derecha y suprarrenal izquierda','vértebra D4','ósea en rama isquiática, dorsales y lumbares','ósea en pala ilíaca derecha','ósea en L5','D10 y articulacion costo-vertebral','costal derecha'):'Ósea',('cerbral','frontal derecha y occipital izquierda respectivamente,','occipital izquierda','parietal derecha','cerebral en lóbulo frontal izquierdo','cerebralde','lóbulos frontal y occipital izquierdo','T1','cerebral temporal derecho','cerebra única parietal izquierda','intraparenquimatosas','región parahipocampal izquierda','frontoparietal derecha','parietoocipital izquierda','frontal derecha','cerebral occipital derecha','intraaxial frontal derecha','asta frontal del ventriculo lateral izquierdo','cerebelosa anterolateral derecha','orígen cervical','Lesiones cerebrales','cerebral con lesión parietal izquierda','cerebral','tronco del encéfalo','frontal izquierda','cerebelosa','lesión tumoral extraaxial parietal parasagital derecha','cerebral localizada en','cerebrales','cerebral parietal post derecha','cerebelosa izquierda','circunvolución frontal superior derecha','durales','nódulo parasagital frontal izquierdo','Lesión intraaxial corticosubcortical temporobasal izquierda','parietal izquierda','supra e infratentoriales','región temporal izquierda','región frontal','hemisferio cerebeloso derecho'):'Cerebral',('nódulos pulmonares en LSI','subcentimétricas en LHD y lóbulo caudado','pulmonares','pulmón','LID','lesión del LSI','LSI','lesion en LID','pulmonares apicales derechoso','pulmonar en LSI','pulmonar','LSD','lesión en LSI sugestivo de tumor primario','ventrículo derecho'):'Pulmonar',('hepática','hepatica','hepática subcentimétrica en LHD','hepática y ha iniciado','hepáticas','segmento IV hepático','segmento VIII y segmento VI','hepática e ILE','LHI','situadas en lóbulo hepático derecho','heaticas','hepática en S-VIII','segmento IV y III'):'Hepática',('adenopatías mediastínicas','1 ganglio de nivel I y 2 de nivel III','ganglio paraaortico','lesión ganglionar','ganglio linfático','ganglios linfáticos','ganglios','ganglionar','ganglionar cervical','ganglionar en cadena iliaca externa derecha','adenopatía ilíaca derecha','1 ganglio de nivel III izquierdo y ninguno derecho','1 ganglio del nivel III','ganglionares','Ganglios linfaticos','ganglios basales derechos','lesión ilíaca','cadena ilíaca','iliaca interna derecha','cadena iliaca comun izquierda','iliaca derecha','hiliar izquierda','adenopatía hiliar remitida y en el ganglio peribronquial aislado de la pieza delobectomía','hilio derecho','Iliaco derecho y psoas ipsilateral','situadas en la cadena iliaca común derecha y en el espacio presacro izquierdo','AXILA DERECHA','ADENOPATÍA AXILAR IZQUIERDA','adenopatía iliaca interna derecha','1 ganglio linfático intraparotídeo','cadena ganglionar iliaca externa','ganglionar derecha','adenopatía iliaca izda','axilar izquierdo'):'Ganglionar',('próstata'):'Prostática',('tiroides'):'Toroidea',('pancreática','pancreas'):'Pancreatica',('glándula suprarrenal izquierda','renal izquierda'):'Renal',('nódulo mesenterico','ósea y hepática','ganglionar y ósea','cabeza del núcleo caudado derecho','lesión en','hepática y dudoso nódulo pulmonar en LSD','adenopatía neoplásica paraórtica infrarrenal izquierda','16/1/2023','celula grande de pulmón','la calota, ambos húmeros','óseas y ganglionares','vesícula seminal y pelvis','óseas, hepáticas, pulmonares','coloide','Lesiones focales','hepática SVI, pulmonar LID y LII','cadena hipogástrica izquierda','gl suprarrenal derecha','suprarrenal izquierda','suprarrenal','adenopatía hiliar remitida y en el ganglio peribronquial aislado de la pieza delobectomía','vértebra D8'):''}}

        df = filtrar_resultados(df,diccionario_replace)
        df['AGE'] = df['AGE'].str.extract('(\d+)', expand=False)
        df['AGE'] = pd.to_numeric(df['AGE'], errors='coerce')
        df['DOSIS_N'] = df['DOSIS_D'].str.extractall('(\d+(?:[\.,]\d+)?)').groupby(level=0).agg('/'.join)
        df['DOSIS'] = df['DOSIS'].str.replace(',','.')
            
        for index, row in df.iterrows():
            if pd.isnull(row['DOSIS']):  
                if pd.isnull(row['DOSIS_D']):  
                    continue  
                else:
                        
                    if pd.notnull(row['DOSIS_N']) and '/' in row['DOSIS_N']:
                        dosis_nums = [float(num.replace(',', '.')) for num in row['DOSIS_N'].split('/')]
                        if len(dosis_nums) == 2:
                            
                            df.at[index, 'DOSIS'] = str(np.multiply(dosis_nums[0],dosis_nums[1])).replace(',','.') 
                        else:
                            continue  
            else:
            
                continue
        
        df.drop(columns=['DOSIS_N'], inplace=True)
        df['DOSIS'] = df['DOSIS'].str.extract('(\d+(?:\.\d+)?)',expand= False).apply(lambda x: dosis(x))


        for columna in labels_evo:
            filas_recist_ok = df[df[columna].isin(recist)].index
            df[columna] = df.loc[filas_recist_ok,columna]

    except:
        logger.info('Diccionarios o método replace en DF presenta error')

    return df, df_evo

    #GUARDADO DE EXCEL CON NOMBRE ESPECIFICO

def guardar_excel(df,df_evo,titulo):
    try:
        with pd.ExcelWriter(titulo) as writer:
            df.to_excel(writer, sheet_name='DATOS INFORME', index=False, header=True)
            df_evo.to_excel(writer, sheet_name='EVOLUTIVOS', index=False, header=True)
    except:
        logger.info('Error al crear el excel a partir de los DataFrames')



def procesar_label(label, doc):
    if label in ['RC', 'RP', 'EE', 'PG']:
        return next((ent.label_ for ent in doc.ents if ent.label_ == label), '')
    else:
        return next((ent.text for ent in doc.ents if ent.label_ == label), '')


def fechas_RT(fila):
    try:
        matches = list(datefinder.find_dates(str(fila), index=True))  

        if matches:
        
            fecha = matches[0][0]
            return fecha.strftime('%Y-%m-%d')
                      
    except:
        logger.info('Error el formato y localización de fechas en df')


def filtrar_resultados(df,diccionario):
    try:
        for columna, dicc in diccionario.items():
            for original, modificado in dicc.items():
                df[columna] = df[columna].replace(original, modificado)

        return df
    except:
       logger.info('Método replace para filtrar resultados presenta error')
    
def dosis(x):
    if pd.notnull(x):
        dosis = float(x)
        if dosis > 100:
            return f'{dosis/100} Gy'
        else:
            return f'{dosis} Gy' 
    else:
        return ''

#LLAMA AL SISTEMA Y ABRE EL EXCEL AUTOMÁTICAMENTE

def show_excel(titulo):
    try:            
        system = platform.system()
        if system == 'Windows':
            subprocess.Popen(['start',titulo], shell=True)
        elif system == 'Darwin': 
            subprocess.Popen(['open',titulo])
        else:
            logger.info('El SSOO del dispositvo no es el adecuado para abrir el excel de resultados automáticamente, habralo de forma manual.')
        
    except:
        logger.info('El archivo excel no se ha podido abrir')




