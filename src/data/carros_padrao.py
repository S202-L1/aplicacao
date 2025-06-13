from typing import List, Dict

# Lista de modelos de carros disponíveis (pra poder gerar os carros da concessionária)
MODELOS_CARROS = [
    {
        "modelo": "Opala SS",
        "fabricante": "Chevrolet",
        "ano": 1976
    },
    {
        "modelo": "Uno",
        "fabricante": "Fiat",
        "ano": 1994
    },
    {
        "modelo": "Gol",
        "fabricante": "Volkswagen",
        "ano": 2005
    },
    {
        "modelo": "Celta",
        "fabricante": "Chevrolet",
        "ano": 2012
    },
    {
        "modelo": "Civic",
        "fabricante": "Honda",
        "ano": 2018
    },
    {
        "modelo": "Nissan Skyline GT-R",
        "fabricante": "Nissan",
        "ano": 1999
    },
    {
        "modelo": "Corolla",
        "fabricante": "Toyota",
        "ano": 2020
    },
    {
        "modelo": "HB20",
        "fabricante": "Hyundai",
        "ano": 2016
    },
    {
        "modelo": "Onix",
        "fabricante": "Chevrolet",
        "ano": 2019
    },
    {
        "modelo": "Argo",
        "fabricante": "Fiat",
        "ano": 2021
    },
    {
        "modelo": "T-Cross",
        "fabricante": "Volkswagen",
        "ano": 2022
    },
    {
        "modelo": "HR-V",
        "fabricante": "Honda",
        "ano": 2017
    },
    {
        "modelo": "Mustang GT",
        "fabricante": "Ford",
        "ano": 1969
    }
]

PREFIXOS_CRLV = {
    "Fiat": "FT",
    "Volkswagen": "VW",
    "Chevrolet": "CH",
    "Honda": "HN",
    "Toyota": "TY",
    "Hyundai": "HY",
    "Ford": "FD",
    "Nissan": "NS"
} 