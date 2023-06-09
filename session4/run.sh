#! /bin/bash

BASEDIR=../DDI

# ./corenlp-server.sh -quiet true -port 9000 -timeout 15000  &
# sleep 1

# extract features
# echo "Extracting features"
# python3 extract-features.py $BASEDIR/data/devel/ > devel.cod &
# python3 extract-features.py $BASEDIR/data/train/ | tee train.cod | cut -f4- > train.cod.cl

# kill `cat /tmp/corenlp-server.running`

# train model
# echo "Training model"
# python3 train-sklearn.py model.joblib vectorizer.joblib < train.cod.cl
# run model
# echo "Running model..."
# python3 predict-sklearn.py model.joblib vectorizer.joblib < devel.cod > devel.out
# evaluate results
# echo "Evaluating results..."
# python3 evaluator.py DDI $BASEDIR/data/devel/ devel.out > devel.stats


# echo "Training model SGD"
# python3 train-sgd.py sgd.joblib vectorizer.joblib < train.cod.cl
# run model
# echo "Running model..."
# python3 predict-sklearn.py sgd.joblib vectorizer.joblib < devel.cod > devel.out
# evaluate results
# echo "Evaluating results..."
# python3 evaluator.py DDI $BASEDIR/data/devel/ devel.out > devel-sgd.stats

# echo "Training model SVC"
# python3 train-svc.py svc.joblib vectorizer.joblib < train.cod.cl
# run model
# echo "Running model..."
# python3 predict-sklearn.py svc.joblib vectorizer.joblib < devel.cod > devel.out
# evaluate results
# echo "Evaluating results..."
# python3 evaluator.py DDI $BASEDIR/data/devel/ devel.out > devel-svc.stats

echo "Training model RF"
python3 train-rf.py rf.joblib vectorizer.joblib < train.cod.cl
# run model
echo "Running model..."
python3 predict-sklearn.py rf.joblib vectorizer.joblib < devel.cod > devel.out
# evaluate results
echo "Evaluating results..."
python3 evaluator.py DDI $BASEDIR/data/devel/ devel.out > devel-rf.stats

