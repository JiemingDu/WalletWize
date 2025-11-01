''' 
assuming we have address of the user
and there university

call get_<transportation_name>_price() to get the prices
'''


A_cities = [
        "Baie-D'Urfé",
        "Beaconsfield",
        "Côte-Saint-Luc",
        "Dollard-des-Ormeaux",
        "Dorval",
        "Hampstead",
        "Kirkland",
        "L'Île-Dorval",
        "Montréal",
        "Montréal-Est",
        "Montréal-Ouest",
        "Mont-Royal",
        "Pointe-Claire",
        "Sainte-Anne-de-Bellevue",
        "Senneville",
        "Westmount"
    ]
B_cities = [
        'Boucherville', 
        'Brossard', 
        'Longueuil', 
        'Saint-Bruno-de-Montarville', 
        'Saint-Lambert',
        'Laval'
    ]
C_cities = [
    "Blainville",
    "Boisbriand",
    "Bois-des-Filion",
    "Charlemagne",
    "Deux-Montagnes",
    "L'Assomption",
    "Lorraine",
    "Mascouche",
    "Mirabel",
    "Oka",
    "Pointe-Calumet",
    "Couronne Nord",
    "Repentigny",
    "Rosemère",
    "Sainte-Anne-des-Plaines",
    "Sainte-Marthe-sur-le-lac",
    "Sainte-Thérèse",
    "Saint-Eustache",
    "Saint-Jérôme",
    "Saint-Joseph-du-Lac",
    "Saint-Sulpice",
    "Terrebonne",
    "Beauharnois",
    "Beloeil",
    "Candiac",
    "Carignan",
    "Chambly",
    "Châteauguay",
    "Contrecoeur",
    "Delson",
    "Hudson",
    "Kahnawake",
    "La Prairie",
    "Couronne Sud",
    "Léry",
    "L'Île-Perrot",
    "McMasterville",
    "Mercier",
    "Mont-Saint-Hilaire",
    "Notre-Dame-de-l'Île-Perrot",
    "Otterburn Park",
    "Pincourt",
    "Richelieu",
    "Saint-Amable",
    "Saint-Basile-le-Grand",
    "Couronne Sud",
    "Saint-Constant",
    "Sainte-Catherine",
    "Sainte-Julie",
    "Saint-Lazare",
    "Saint-Mathias-sur-Richelieu",
    "Saint-Mathieu-de-Beloeil",
    "Saint-Philippe",
    "Terrasse-Vaudreuil",
    "Varennes",
    "Vaudreuil-Dorion",
    "Verchères"
]
D_cities = [
"L'Épiphanie",
"Lavaltrie",
"Marieville",
"Rigaud",
"Sainte-Madeleine",
"Sainte-Marie-Madeleine",
"Sainte-Martine",
"Saint-Hyacinthe",
"Saint-Placide"
]

STM_zones = {
    'A': A_cities,
    'B': B_cities,
    'C': C_cities,
    'D': D_cities
    }
tarif = {
    'A' : 62.75,
    'AB' : 98.75,
    'ABC' : 120.25, 
    'ABCD' : 165.25
}

def get_stm_price(address, skl_add):
    '''input: 
        address: standard address notation of user's home (ex: '98 Croissant des Trèfles, L'Île-Perrot, QC J7V 2G2')
        skl_add: address of the school the user attends

        raise NameValueError if the home address or university is not in the greater area of montreal
        '''
    my_zone = get_zone(address)
    uni_zone = get_zone(skl_add)
    if my_zone == 'D' or uni_zone == 'D':
        my_tarif = tarif['ABCD']
    elif my_zone == 'C' or uni_zone == 'C':
        my_tarif = tarif['ABC']
    elif my_zone == 'B' or uni_zone == 'B':
        my_tarif = tarif['AB']
    else:
        my_tarif = tarif['A']
    return my_tarif

def get_zone(address):
    add_city = address.split(', ')[1]
    try:
        if add_city in A_cities:
            zone = 'A'
        elif add_city in B_cities:
            zone = 'B'
        elif add_city in C_cities:
            zone = 'C'
        elif add_city in D_cities:
            zone = 'D'
        return zone
    except NameError as e:
        print(e)
        raise NameError("There is no Montreal public transportation available near this address")

def get_bixi_price():
    return 23

#print(get_zone("2401 Rue Workman, Montréal, QC H3J 2N3"))
if __name__ == "main":
    print(get_stm_price('1287 Rue Ropery, Montréal, QC H3K 2X1', "98 Croissant des Trèfles, L'Île-Perrot, QC J7V 2G2"))
        



