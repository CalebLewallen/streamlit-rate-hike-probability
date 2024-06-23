
# This function will take a value from a dataframe and return 
def highlight_nonzero_cells(val):
    """
    Suggested use in .style.applymap(highlight_nonzero_cells, subset=pd.IndexSlice[:, probability_tree_headers])
    """
    color = '#84dde3' if val > 0.0 else ''
    return 'background-color: {}'.format(color)