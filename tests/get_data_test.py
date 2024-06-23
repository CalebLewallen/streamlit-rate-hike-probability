import pytest
from src.get_data import get_cme_data

def test_get_cme_data():
    
    results = get_cme_data()
    
    assert results != None