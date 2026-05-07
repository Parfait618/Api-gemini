def decoder_systeme_offusque(chaine_codee):
    elements = chaine_codee.split(',')
    alphabet_min = "abcdefghijklmnopqrstuvwxyz"
    resultat = []

    for item in elements:
        item = item.strip()
        if not item:
            continue

        # Règle 1 : Majuscules (.z -> A)
        if item.startswith('.'):
            lettre_fin = item[1]
            pos = alphabet_min.find(lettre_fin)
            majuscule_origine = alphabet_min[25 - pos].upper()
            resultat.append(majuscule_origine)

        # Règle 2 : Lettres minuscules (nombres 0-25)
        elif item.isdigit():
            pos = int(item)
            resultat.append(alphabet_min[pos])

        # Règle 3 : Chiffres (lettres a-j -> 0-9)
        elif len(item) == 1 and 'a' <= item <= 'j':
            chiffre = str(alphabet_min.find(item))
            resultat.append(chiffre)

        # Règle 4 : Caractères Spéciaux
        else:
            resultat.append(item)

    return "".join(resultat)

# Voici la version encodée de ton texte cible
code_cible = ".z,.r,25,0,.h,24,.z,a,.b,17,.k,.z,.n,9,1,2,.n,3,.i,.s,6,.o,.j,16,.b,j,.x,.u,17,23,.h,.o,c,.j,c,.g,.b,.a,.n"

phrase_decodee = decoder_systeme_offusque(code_cible)
print(phrase_decodee)
