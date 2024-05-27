import srsly
import typer
import warnings
from pathlib import Path
import spacy
import numpy as np
import os
import pandas as pd
import subprocess

from matplotlib import pyplot
from sklearn.metrics import confusion_matrix
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score
from sklearn.metrics import f1_score
#from sklearn.metrics import classification_report

from tqdm import tqdm
from spacy.training import offsets_to_biluo_tags #allow to entities start and end. Give a target vector if it is in the entity it is given the entity's tag name and if it isn't it is given O.

def _load_data(file_path):
    samples, entities_count = [], 0
    for line in srsly.read_jsonl(file_path):
        sample = {
            "text": line["text"],
            "entities": []
        }
        if "spans" in line.keys():
            entities = [(s["start"], s["end"], s["label"]) for s in line["spans"]]
            sample["entities"] = entities
            entities_count += len(entities)
        else:
            warnings.warn("Sample without entities!")
        samples.append(sample)
    return samples, entities_count


def _get_cleaned_label(label: str):
    if "-" in label:
        return label.split("-")[1]
    else:
        return label


def _create_total_target_vector(nlp, samples):
    target_vector = []
    for sample in samples:
        doc = nlp.make_doc(sample["text"])
        ents = sample["entities"]
        bilou_ents = offsets_to_biluo_tags(doc, ents)
        vec = [_get_cleaned_label(label) for label in bilou_ents]
        target_vector.extend(vec)
    return target_vector
    


def _get_all_ner_predictions(nlp, text):
    doc = nlp(text)
    entities = [(e.start_char, e.end_char, e.label_) for e in doc.ents]
    bilou_entities = offsets_to_biluo_tags(doc, entities)
    return bilou_entities


def _create_prediction_vector(nlp, text):
    return [_get_cleaned_label(prediction) for prediction in _get_all_ner_predictions(nlp, text)]


def _create_total_prediction_vector(nlp, samples):
    prediction_vector = []
    for i in tqdm(range(len(samples))):
        sample = samples[i]
        prediction_vector.extend(_create_prediction_vector(nlp, sample["text"]))

    return prediction_vector


def _plot_confusion_matrix(cm, classes, normalize=False, text=True, cmap=pyplot.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """

    title = "Confusion Matrix"

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    fig, ax = pyplot.subplots()
    im = ax.imshow(cm, interpolation='nearest', cmap=cmap)
    ax.figure.colorbar(im, ax=ax)
    # We want to show all ticks...
    ax.set(xticks=np.arange(cm.shape[1]),
           yticks=np.arange(cm.shape[0]),
           # ... and label them with the respective list entries
           xticklabels=classes, yticklabels=classes,
           title=title,
           ylabel='True label',
           xlabel='Predicted label')

    # Rotate the tick labels and set their alignment.
    pyplot.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    if text:
        fmt = '.2f' if normalize else 'd'
        thresh = cm.max() / 2.
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                ax.text(j, i, format(cm[i, j], fmt),
                        ha="center", va="center",
                        color="white" if cm[i, j] > thresh else "black")
    fig.tight_layout()
    return ax, pyplot


def get_confusion_matrix(model_path: Path, data_path: Path, output_dir: Path):
    spacy.prefer_gpu()
    nlp = spacy.load(model_path)
    print(f"Loaded SpaCy pipeline.")
    samples, entities_count = _load_data(data_path)
    print(f"Loaded {len(samples)} samples including {entities_count} entities.")
    classes = sorted(set(_create_total_target_vector(nlp, samples)))
    print(f"Identified {len(classes)} classes: {', '.join(classes)}")
    y_true = _create_total_target_vector(nlp, samples)
    print("Computed target vector!")
    print("Computing prediction vector...")
    y_pred = _create_total_prediction_vector(nlp, samples)
    matrix = confusion_matrix(y_true, y_pred, labels=classes)
    print("Generated confusion matrix!")
    cm_df = pd.DataFrame(matrix, columns=classes)
    cm_df.insert(0, "variables", classes)
    ax, plot = _plot_confusion_matrix(matrix, classes, normalize=True, text=False)
    print("Plotted confusion matrix!")
    pyplot.show()
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

      
    metrics_dict ={
    'variables': classes,
    'recall': recall_score(y_true,y_pred,average=None),
    'precision': precision_score(y_true,y_pred,average=None),
    'F1': f1_score(y_true,y_pred,average=None),}
    metrics_df = pd.DataFrame(metrics_dict)


    #report_df = pd.DataFrame(report)

    results = []
    for i, label in enumerate(classes):
        FP = matrix.sum(axis=0) - np.diag(matrix) #suma a lo largo del eje 0 es decir sumar las columnas, eje x
        FN = matrix.sum(axis=1) - np.diag(matrix) #suma a lo largo del eje 1 es decir sumar las columnas, eje y
        TP = np.diag(matrix)
        TN = matrix.sum() - (FP + FN + TP)
        results.append({'variables': label, 'TN': TN[i], 'FN':FN[i], 'FP': FP[i], 'TP': TP[i]})
        

    results_df = pd.DataFrame(results)

    for i, label in enumerate(classes):
        # Crear una matriz de confusión binaria para la clase actual
        binary_matrix = np.array([
            [TN[i], FP[i]],
            [FN[i],matrix[i, i]]
        ])
        
        # Visualizar la matriz de confusión
        fig, ax = pyplot.subplots()
        cax = ax.matshow(binary_matrix, cmap='Oranges')
        pyplot.title(f'Matriz de confusión de la etiqueta {label}', pad=20)
        fig.colorbar(cax)
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(['Negativo', 'Positivo'])
        ax.set_yticklabels(['Negativo', 'Positivo'])
        pyplot.xlabel('Predicho')
        pyplot.ylabel('Valor Real')

        # Añadir anotaciones
        for (j, k), val in np.ndenumerate(binary_matrix):
            ax.text(k, j, f'{val}', ha='center', va='center', color='black')
        pyplot.tight_layout()
        pyplot.show()

    excel_file_out = output_dir/'confusion.xlsx'
    with pd.ExcelWriter(excel_file_out) as writer:
        cm_df.to_excel(writer, sheet_name='Matriz Confusion', index=False, header=True)
        results_df.to_excel(writer, sheet_name='Matriz Confusion por variable', index=False, header=True)
        metrics_df.to_excel(writer, sheet_name='Metrics por variable', index=False, header=True)
    print(f"Saving report data to: {output_dir}/confusion.xlsx")
    
    #subprocess.Popen(['start', "Matriz_Confusion/confusion.xlsx"], shell=True)
    print("FINISHED!")


if __name__ == "__main__":
    typer.run(get_confusion_matrix)



