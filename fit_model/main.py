# gcloud functions deploy python-fitting-model --gen2 --runtime=python311 --region=europe-central2 --source=. --entry-point=fit_model --trigger-http --allow-unauthenticated
# functions-framework --target=fit_model 

from flask import escape

import functions_framework
import numpy as np
import librosa
import io
import tempfile
import json
import requests
from PIL import Image
from operator import itemgetter

#ENDPOINT = "https://model-serving-dplabwnjcq-lm.a.run.app/v1/models/model:predict"

ENDPOINT = "https://m160eu10s-dplabwnjcq-lm.a.run.app/v1/models/160EU10S:predict"

SPECIES = ['Dryobates minor', 'Carduelis carduelis', 'Anthus spinoletta', 'Linaria cannabina', 'Locustella fluviatilis', 'Apus apus', 'Tachybaptus ruficollis', 'Corvus cornix', 'Athene noctua', 'Chlidonias niger', 'Circus aeruginosus', 'Porzana porzana', 'Passer montanus', 'Tetrastes bonasia', 'Dendrocoptes medius', 'Sylvia borin', 'Streptopelia decaocto', 'Anser anser', 'Dendrocopos major', 'Aegolius funereus', 'Zapornia parva', 'Serinus serinus', 'Hirundo rustica', 'Scolopax rusticola', 'Locustella luscinioides', 'Corvus frugilegus', 'Sturnus vulgaris', 'Acrocephalus paludicola', 'Luscinia megarhynchos', 'Ardea cinerea', 'Numenius arquata', 'Lullula arborea', 'Lophophanes cristatus', 'Periparus ater', 'Locustella naevia', 'Cygnus olor', 'Chlidonias leucopterus', 'Gallinago media', 'Merops apiaster', 'Carpodacus erythrinus', 'Jynx torquilla', 'Limosa limosa', 'Spinus spinus', 'Parus major', 'Asio otus', 'Upupa epops', 'Fringilla coelebs', 'Cyanistes caeruleus', 'Curruca nisoria', 'Anser fabalis', 'Turdus pilaris', 'Perdix perdix', 'Luscinia svecica', 'Bombycilla garrulus', 'Emberiza schoeniclus', 'Columba oenas', 'Poecile palustris', 'Certhia familiaris', 'Luscinia luscinia', 'Cuculus canorus', 'Tringa nebularia', 'Prunella modularis', 'Buteo buteo', 'Acrocephalus arundinaceus', 'Lanius collurio', 'Galerida cristata', 'Spatula querquedula', 'Emberiza citrinella', 'Saxicola rubetra', 'Turdus iliacus', 'Riparia riparia', 'Haliaeetus albicilla', 'Remiz pendulinus', 'Coloeus monedula', 'Acrocephalus palustris', 'Gallinago gallinago', 'Lyrurus tetrix', 'Coccothraustes coccothraustes', 'Mareca strepera', 'Corvus corax', 'Chroicocephalus ridibundus', 'Sterna hirundo', 'Columba palumbus', 'Ardea alba', 'Acrocephalus scirpaceus', 'Tetrao urogallus', 'Bucephala clangula', 'Dryocopus martius', 'Streptopelia turtur', 'Panurus biarmicus', 'Caprimulgus europaeus', 'Oriolus oriolus', 'Regulus ignicapilla', 'Curruca communis', 'Accipiter gentilis', 'Anthus pratensis', 'Bubo bubo', 'Picus viridis', 'Motacilla alba', 'Ficedula hypoleuca', 'Muscicapa striata', 'Larus argentatus', 'Chlidonias hybrida', 'Haematopus ostralegus', 'Ficedula albicollis', 'Turdus philomelos', 'Pica pica', 'Poecile montanus', 'Troglodytes troglodytes', 'Alauda arvensis', 'Garrulus glandarius', 'Delichon urbicum', 'Falco tinnunculus', 'Podiceps cristatus', 'Phoenicurus phoenicurus', 'Acrocephalus schoenobaenus', 'Phylloscopus trochilus', 'Grus grus', 'Pyrrhula pyrrhula', 'Cygnus cygnus', 'Regulus regulus', 'Tringa totanus', 'Phylloscopus sibilatrix', 'Vanellus vanellus', 'Oenanthe oenanthe', 'Motacilla flava', 'Podiceps grisegena', 'Phylloscopus collybita', 'Curruca curruca', 'Erithacus rubecula', 'Passer domesticus', 'Tringa glareola', 'Coturnix coturnix', 'Alcedo atthis', 'Nucifraga caryocatactes', 'Strix aluco', 'Crex crex', 'Emberiza hortulana', 'Ciconia ciconia', 'Motacilla cinerea', 'Aythya ferina', 'Phalacrocorax carbo', 'Turdus viscivorus', 'Ficedula parva', 'Glaucidium passerinum', 'Phasianus colchicus', 'Phoenicurus ochruros', 'Tyto alba', 'Anthus trivialis', 'Charadrius dubius', 'Chloris chloris', 'Rallus aquaticus', 'Hippolais icterina', 'Fulica atra', 'Emberiza calandra', 'Botaurus stellaris', 'Sylvia atricapilla', 'Turdus merula', 'Anas platyrhynchos', 'Sitta europaea']



def normalize(D):
    spectrogram_normalized = (D - np.min(D)) / (np.max(D) - np.min(D))
    spectrogram_scaled = (spectrogram_normalized * 255).astype(np.uint8)
    return spectrogram_scaled


@functions_framework.http
def fit_model(request):

    if request.method == 'OPTIONS':
        # Allows GET requests from example.com with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }

        return ('', 204, headers)

    temp = tempfile.NamedTemporaryFile(suffix='.wav')
    temp.write(io.BytesIO(request.data).getbuffer())
    y, sr = librosa.load(temp.name)
    print(f"--------------------------------------> sr = {sr}")
    if sr != 22050:
        y = librosa.resample(y, orig_sr=sr, target_sr=22050)
        sr = 22050

    D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
    D = normalize(D)
    img = Image.fromarray(D)
    newimg = img.resize((212, 384))
    D = np.array(newimg)
    D = D / 255
    to_send = np.zeros((1, 384, 212), dtype='float32')
    if D.shape[1] < 212:
        shortenD = np.zeros((384, 212), dtype='float32')
        shortenD[:,:D.shape[1]] = D[:,:D.shape[1]]
        to_send[0,:,:] = shortenD[:,:]
    elif D.shape[1] >= 212:
        widerD = np.zeros((384, 212), dtype='float32')
        widerD = D[:,:212]
        to_send[0,:,:] = widerD[:,:]
    to_send = np.expand_dims(to_send, axis=-1)
    to_send = to_send.tolist()
    to_send = {"instances": to_send}
    to_send = json.dumps(to_send)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    response = requests.post(ENDPOINT, headers=headers, data=to_send)

    response = json.loads(response.text)
    data_to_return = {}
    for i in range(160):
        data_to_return[SPECIES[i]] = response['predictions'][0][i]

    data_to_return = dict(sorted(data_to_return.items(), key=itemgetter(1), reverse=True)[:5])
    headers = {
        'Access-Control-Allow-Origin': '*'
    }
    return (data_to_return, 200, headers)
