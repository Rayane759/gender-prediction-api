from google.cloud import bigquery
import matplotlib.pyplot as plt
import pandas as pd
import joblib

client = bigquery.Client(project="ensai-2026")
query = "SELECT * FROM `ensai-2026.ml.prenoms`"
df = client.query(query).to_dataframe()
# print(df.head())
# print(df[df['preusuel'] == 'CAMILLE'])

# # Are there null values ?
# print(df.isnull().sum()) # No null values in the dataset

# # Distribution of the gender
# gender_counts = df['sexe'].value_counts()
# plt.bar(gender_counts.index, gender_counts.values)
# plt.xlabel('Gender')
# plt.ylabel('Count')
# plt.title('Distribution of Gender')
# plt.show()
# # The dataset is quite balanced

# # 20 most common names
# top_names = df['preusuel'].value_counts().head(20)
# plt.bar(top_names.index, top_names.values)
# plt.xlabel('Name')
# plt.ylabel('Count')
# plt.title('Top 20 Most Common Names')
# plt.xticks(rotation=90)
# plt.show()  

print(df["sexe"].value_counts())

## Filtering

# We remove the modality which contains "RARES" from the dataset
# make an explicit copy to avoid SettingWithCopyWarning
df_filtered = df[~df['preusuel'].str.contains('_PRENOMS_RARES')].copy()

## Transforming the names into numerical values
# We will use a model that uses only the last letter of a name
# We create a new column "last_letter" which contains the last letter of the name
df_filtered['last_letter'] = df_filtered['preusuel'].str[-1]


## Matrix and vector
# We create X, a matrix which contains the one-hot encoded last letters
# Use the `last_letter` column and one-hot encode it (letters -> numeric features)
X_encoded = pd.get_dummies(df_filtered['last_letter'])
feature_names = X_encoded.columns.tolist()
X = X_encoded.values
# We create y, a vector of 0/1 where 1 means female.
# sexe is encoded as: 1=male, 2=female
y = (df_filtered['sexe'] == 2).astype(int).values


## Splitting the dataset into a training set and a test set
from sklearn.model_selection import train_test_split
# Print class distribution for information
print("Filtered sexe distribution:\n", df_filtered['sexe'].value_counts())
print("y (0=male,1=female) distribution:\n", pd.Series(y).value_counts())

# Use stratify to preserve class proportions in train/test split
X_train, X_test, y_train, y_test = train_test_split(
	X, y, test_size=0.2, random_state=42, stratify=y
)

## Training and Evaluation
# First : Logistic Regression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
model = LogisticRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
print("Logistic Regression Classification Report:")
print(classification_report(y_test, y_pred))
print("Logistic Regression Confusion Matrix:")
print(confusion_matrix(y_test, y_pred)) 

joblib.dump(model, 'logistic_regression_model.joblib')
joblib.dump(feature_names, 'feature_names.joblib')