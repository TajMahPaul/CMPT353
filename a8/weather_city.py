import sys
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import StandardScaler

OUTPUT_TEMPLATE = (
    'Bayesian classifier training score:    {score:.3f}'
)

def create_model(x, y):
    model = make_pipeline(StandardScaler(), GaussianNB())
    model.fit(x,y)
    return model

def main():
    labeled_data_df = pd.read_csv(sys.argv[1])
    unlabeled_data_df = pd.read_csv(sys.argv[2])

    x = labeled_data_df.iloc[:,2:].values
    y = labeled_data_df['city'].values

    x_train, x_valid, y_train, y_valid = train_test_split(x,y)

    model  = create_model(x_train, y_train)
    unlabeled_values = unlabeled_data_df.iloc[:,2:].values
    predict = model.predict(unlabeled_values)
    
    print(OUTPUT_TEMPLATE.format(
        score=model.score(x_valid, y_valid)
    ))

    pd.Series(predict).to_csv(sys.argv[3], index=False, header=False)

    # df = pd.DataFrame({'truth': y_valid, 'prediction': model.predict(x_valid)})
    # print(df[df['truth'] != df['prediction']])
if __name__ == '__main__':
    main()