import numpy as  np

def main():
    data = np.load('monthdata.npz')
    totals = data['totals']
    counts = data['counts']
    print("Row with lowest total precipitation:")
    print( np.argmin(totals.sum(axis=1)))
    print("Average precipitation in each month:")
    print( np.true_divide( totals.sum(axis=0), counts.sum(axis=0)) )
    print("Average precipitation in each city:")
    print( np.true_divide( totals.sum(axis=1), counts.sum(axis=1)) )
    print("Quarterly precipitation totals:")
    num_rows, num_cols = totals.shape
    print( totals.reshape(4*num_rows, 3).sum(axis=1).reshape(num_rows,4))

if __name__ == '__main__':
    main()