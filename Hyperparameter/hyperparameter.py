import pandas as pd
from sklearn.svm import SVR
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import numpy as np
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import GridSearchCV
import pickle
import matplotlib.pyplot as plt
import time

# reading the data with specific columns for pre-processing
# irrelevent feature are extracted like currency , description, details for the better training of the model.
DF = pd.read_csv('data.csv', header=None, usecols=[3, 4, 5, 1])
DF.columns = np.arange(len(DF.columns))

DF[0] = DF[0].apply(lambda x: float(x.split()[0]))
DF[3] = DF[3].apply(lambda x: round(float(x.split()[0])))

DF = DF.sort_values(by = 3)

# applying one-hot-encoding
TRANSFORMS = ColumnTransformer(transformers=[
    ('onehot', OneHotEncoder(), [2]),
    ('scale', StandardScaler(), [2])
], remainder='passthrough')

model_start= time.time()

# Transforming the features
FEATURES = TRANSFORMS.fit_transform(DF.iloc[:, 1:])
OUTCOME = DF.iloc[:, 0]
HYPERPARAMETERS = {'kernel': ['rbf'], 'epsilon': [0.05, 0.075, 0.1, 0.15, 0.2],'gamma': [1e-4, 1e-3, 0.01, 0.1, 0.2, 0.5, 0.6, 0.9], 'C': [1, 2, 5, 10, 15],}

# Train the regression model
REGRESSION = GridSearchCV(SVR(), HYPERPARAMETERS)
TRAINING_MODEL = REGRESSION.fit(FEATURES, OUTCOME)

end = time.time()-model_start

# Generate a prediction
MODEL_PREDICTION = TRAINING_MODEL.predict(FEATURES)
REGRESSION_SCORE = REGRESSION.score(FEATURES, OUTCOME)
print(MODEL_PREDICTION)
print('Time taken for training : '+str(end))
print("RMSE: " + str(mean_squared_error(OUTCOME, MODEL_PREDICTION) ** (1 / 2)))
print(REGRESSION.best_params_)

# saving the model
pickle.dump(TRAINING_MODEL, open("Hyperparameter.pkl", 'wb'))

# visualizing th prediction vs actual results

line = 2
plt.scatter(DF[3], DF[0], color='orange', label='Original Data')
plt.scatter(DF[3], MODEL_PREDICTION, color='green', label='Prediction')
plt.xlabel('Area')
plt.ylabel('Price')
plt.title('Support Vector Regression')
plt.legend()
plt.show()

# ------------------------------------

line = 2
plt.scatter(DF[3], DF[0], color='orange', label='Original Data')
plt.plot(DF[3], MODEL_PREDICTION, color='green', lw=line, label='Prediction')
plt.xlabel('Area')
plt.ylabel('Price')
plt.title('Support Vector Regression')
plt.legend()
plt.show()