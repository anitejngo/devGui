import pandas as pd
import shortuuid
df = pd.read_csv ('orders/desShort.csv',  header=None)

measurements = []
for index, row in df.iterrows():
    firstCol = str(row[0])
    if 'Layout' in firstCol:
        pass
    elif '#' in firstCol:
        pass
    elif 'of' in firstCol:
        measurements.append({"id": str(shortuuid.uuid()), "value": str(row[10])+" - "+str(row[11]), 'layout': True})
    elif 'nan' == firstCol:
        pass
    else:
        measurements.append({"id": str(shortuuid.uuid()), "value": str(row[10]), 'description':  str(row[5]) if str(row[5])!= 'nan' else ''})


print(measurements)



