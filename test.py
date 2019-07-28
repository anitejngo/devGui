from services import parse_csv_cutting_list

if __name__ == '__main__':
    for item in parse_csv_cutting_list('stok.csv')[0]:
        print(item)
