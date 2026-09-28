"""
    Author: Jon Ander Gomez Adrian (jon@dsic.upv.es, http://personales.upv.es/jon)
    Version: 1.0
    Date: October 2025

    Subject: 14009 "Scalable Machine Learning Techniques"
    Bachelor's degree in Data Science
    School of Informatics  (http://www.etsinf.upv.es)
    Technical University of Valencia (http://www.upv.es)

    Using different ML techniques for classification

    This code is for being used in all the ML techniques.
"""

import numpy

# ------------------------------------------------------------------------------------------------------------------------
def distribute(n: int, p: int):
    l = [n // p] * p
    c = sum(l)
    i = 0
    while c < n:
        l[i] += 1
        c += 1
        i += 1
    return l
# ------------------------------------------------------------------------------------------------------------------------
def do_prediction_considering_sequenciality(labels, prediction, y_proba, DELTA):
    if DELTA == 1:
        y_true = numpy.array([t[3] for t in prediction])
        y_pred = y_proba.argmax(axis = 1)
        return y_true, y_pred
    #
    y_true_and_pred = list()
    probabilities = numpy.zeros(len(labels))
    fifo = list()
    t = 0
    counter = 0
    previous_patient = -1
    previous_index = 0
    while t < len(prediction):
        current_patient, current_index, current_tts, current_label, current_probabilities = prediction[t]
        current_probabilities = y_proba[t]
        #
        if current_patient != previous_patient or current_index != previous_index + 1:
            probabilities[:] = 0.0
            counter = 0
            fifo = list()
        #
        probabilities += current_probabilities
        fifo.append(current_probabilities)
        counter += 1
        if counter >= DELTA:
            k = probabilities.argmax()
            y_true_and_pred.append((current_label, k))
            #
            probabilities -= fifo[0]
            fifo.pop(0)
        #
        previous_patient = current_patient
        previous_index = current_index
        t += 1
    # end of while t
    y_true = numpy.array([x[0] for x in y_true_and_pred])
    y_pred = numpy.array([x[1] for x in y_true_and_pred])
    #
    return y_true, y_pred
# ------------------------------------------------------------------------------------------------------------------------
