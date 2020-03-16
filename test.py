
def test_valid(cldf_dataset, cldf_logger):
    assert cldf_dataset.validate(log=cldf_logger)


def test_forms(cldf_dataset, cldf_logger):
    assert len(list(cldf_dataset['FormTable'])) == 1106
    assert len([
        f for f in cldf_dataset['FormTable'] if f['Value'] == 'keek ~ keʔk'
    ]) == 2


def test_languages(cldf_dataset, cldf_logger):
    assert len(list(cldf_dataset['LanguageTable'])) == 10


def test_parameters(cldf_dataset, cldf_logger):
    assert len(list(cldf_dataset['ParameterTable'])) == 110


def test_cognates(cldf_dataset, cldf_logger):
    cogsets = {c['Cognateset_ID'] for c in cldf_dataset['CognateTable']}
    assert len(cogsets) == 339
    

def test_lexemes_and_cognates_align(cldf_dataset, cldf_logger):
    #that	šiiʔ	hæʔæ	hehəmbə	yahyəʔn	hamah	?	heam	?	ga.də	əʔ
    #that	1	6	2	3	2	NA	2	NA	5	4
    
    expected = {
        'šiiʔ': 1,
        'hæʔæ': 6,
        'hehəmbə': 2,
        'yahyəʔn': 3,
        'hamah': 2,
        'heam': 2,
        'ga.də': 5,
        'əʔ': 4,
    }
    # 2x ?, 2x NA
    
    forms = [f for f in cldf_dataset['FormTable'] if f['Parameter_ID'] == '85_that']
    for f in forms:
        assert f['Value'] in expected
        assert f['Cognacy'] == "85_that-%d" % expected.get(f['Value'])
