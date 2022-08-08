import pandas

# pandas is a little overkill but we'll use it more later


def process_csv_upload(data_file):
    csv_dataframe = pandas.read_csv(data_file)
    # import_file = pandas.read_csv("/home/cr625/yamz/uploads/data/test_1.csv")
    return csv_dataframe.to_dict(orient="records")
