"""Solution du laboratoire, permettant de bien comprendre comment hériter d'un widget de tkinter, de dessiner
un échiquier dans un Canvas, puis de déterminer quelle case a été sélectionnée.

"""
from tkinter import NSEW, Canvas, Label, Tk, Button, Entry, END, Message, CENTER, Text, INSERT, PhotoImage
from pychecs2.echecs.partie import Partie
import webbrowser
from pychecs2.interface import *
from pychecs2.echecs.echiquier import Echiquier

# Création des classes d'exceptions qui seront utilisées dans la méthode sélectionner
# Allo vinc

class AucunePieceAPosition(Exception):
    pass


class DeplacementInvalide(Exception):
    pass


class PieceDeMauvaiseCouleur(Exception):
    pass

class CouleurNonValide(Exception):
    pass

class CanvasEchiquier(Canvas):
    """Classe héritant d'un Canvas, et affichant un échiquier qui se redimensionne automatique lorsque
    la fenêtre est étirée.

    """
    def __init__(self, parent, n_pixels_par_case):
        # Nombre de lignes et de colonnes.
        self.n_lignes = 8
        self.n_colonnes = 8

        # Création d'une partie d'échec dans le Canvas
        self.partie = Partie()

        # Noms des lignes et des colonnes.
        self.chiffres_rangees = ['1', '2', '3', '4', '5', '6', '7', '8']
        self.lettres_colonnes = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

        # Nombre de pixels par case, variable.
        self.n_pixels_par_case = n_pixels_par_case

        # Appel du constructeur de la classe de base (Canvas).
        # La largeur et la hauteur sont déterminés en fonction du nombre de cases.
        super().__init__(parent, width=self.n_lignes * n_pixels_par_case,
                         height=self.n_colonnes * self.n_pixels_par_case)

        # On utilise le dictionnaire de pièces intégré dans l'échiquier
        self.pieces = self.partie.echiquier.dictionnaire_pieces

        # Couleur d'arrière plan de l'échiquier (Avec le blanc)
        self.couleur_theme = 'grey'

        # On fait en sorte que le redimensionnement du canvas redimensionne son contenu. Cet événement étant également
        # généré lors de la création de la fenêtre, nous n'avons pas à dessiner les cases et les pièces dans le
        # constructeur.
        self.bind('<Configure>', self.redimensionner)

    def dessiner_cases(self):
        """Méthode qui dessine les cases de l'échiquier.

        """
        for i in range(self.n_lignes):
            for j in range(self.n_colonnes):
                debut_ligne = i * self.n_pixels_par_case
                fin_ligne = debut_ligne + self.n_pixels_par_case
                debut_colonne = j * self.n_pixels_par_case
                fin_colonne = debut_colonne + self.n_pixels_par_case

                # On détermine la couleur.
                if (i + j) % 2 == 0:
                    couleur = 'white'
                else:
                    couleur = self.couleur_theme

                # On dessine le rectangle. On utilise l'attribut "tags" pour être en mesure de récupérer les éléments
                # par la suite.
                self.create_rectangle(debut_colonne, debut_ligne, fin_colonne, fin_ligne, fill=couleur, tags='case')

    def dessiner_pieces(self):
        self.pieces = self.partie.echiquier.dictionnaire_pieces
        # Caractères unicode représentant les pièces. Vous avez besoin de la police d'écriture DejaVu.
        caracteres_pieces = {'PB': '\u2659',
                             'PN': '\u265f',
                             'TB': '\u2656',
                             'TN': '\u265c',
                             'CB': '\u2658',
                             'CN': '\u265e',
                             'FB': '\u2657',
                             'FN': '\u265d',
                             'RB': '\u2654',
                             'RN': '\u265a',
                             'DB': '\u2655',
                             'DN': '\u265b',
                             }

        # Pour tout paire position, pièce:
        for position, piece in self.pieces.items():
            # On dessine la pièce dans le canvas, au centre de la case. On utilise l'attribut "tags" pour être en
            # Mesure de récupérer les éléments dans le canvas.
            coordonnee_y = (self.n_lignes - self.chiffres_rangees.index(position[1]) - 1) * \
                           self.n_pixels_par_case + self.n_pixels_par_case // 2
            coordonnee_x = self.lettres_colonnes.index(position[0]) * self.n_pixels_par_case + self.\
                n_pixels_par_case // 2
            self.create_text(coordonnee_x, coordonnee_y, text=caracteres_pieces[str(piece)],
                             font=('Deja Vu', self.n_pixels_par_case//2), tags='piece')

    def redimensionner(self, event):
        # Nous recevons dans le "event" la nouvelle dimension dans les attributs width et height. On veut un damier
        # carré, alors on ne conserve que la plus petite de ces deux valeurs.
        nouvelle_taille = min(event.width, event.height)

        # Calcul de la nouvelle dimension des cases.
        self.n_pixels_par_case = nouvelle_taille // self.n_lignes

        # On supprime les anciennes cases et on ajoute les nouvelles.
        self.delete('case')
        self.dessiner_cases()

        # On supprime les anciennes pièces et on ajoute les nouvelles.
        self.delete('piece')
        self.dessiner_pieces()


class Fenetre(Tk):

    def __init__(self):
        super().__init__()

        # Nom de la fenêtre.
        self.title("Échiquier")

        # La position sélectionnée.
        self.position_selectionnee = None

        # Truc pour le redimensionnement automatique des éléments de la fenêtre.
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Lien des règlements
        self.url = "https://actionsports50plus.ca/data/documents/Reglements-Echecs.pdf"

        # Compteur de temps
        self.compteur = 0

        # Création du canvas échiquier.
        self.canvas_echiquier = CanvasEchiquier(self, 80)
        self.canvas_echiquier.grid(sticky=NSEW)

        # Ajout d'une étiquette d'information.
        self.messages = Label(self)
        self.messages.grid()

        # Joueur débutant la partie
        self.messages['foreground'] = 'black'
        self.messages['text'] = 'Le joueur {} débute la partie. '.format(self.canvas_echiquier.partie.joueur_actif)

        # On lie un clic sur le CanvasEchiquier à une méthode.
        self.canvas_echiquier.bind('<Button-1>', self.selectionner)

        # Bouton démarer le temps
        self.button_compteur = Button(self, text='Démarer le temps')
        self.button_compteur.grid()
        self.button_compteur.bind('<Button-1>', self.debut_temps)

        # Label de compteur de temps
        self.temps_afficher = Label(self, text='Vous avez 60 secondes pour jouer:')
        self.temps_afficher.grid()
        self.compteur_label = Label(self, text=str(self.compteur))
        self.compteur_label.grid()

        # Bouton arrêter le temps
        self.button_compteur = Button(self, text='Arrêter le temps')
        self.button_compteur.grid()
        self.button_compteur.bind('<Button-1>', self.arret_temps)

        # Lire les règlements
        self.button_regles = Button(self, text='Lire les règlements')
        self.button_regles.grid()
        self.button_regles.bind('<Button-1>', self.regles)

        # Bouton Nouvelle Partie
        self.button_nouvelle_partie = Button(self, text='Nouvelle Partie')
        self.button_nouvelle_partie.grid()
        self.button_nouvelle_partie.bind('<Button-1>', self.nouvelle_partie)

        # Bouton Sauvegarder la Partie
        self.button_save = Button(self, text='Sauvegarder la Partie')
        self.button_save.grid()
        self.button_save.bind('<Button-1>', self.sauvegarder_partie)

        # Bouton charger Partie
        self.button_load = Button(self, text='Charger une partie')
        self.button_load.grid()
        self.button_load.bind('<Button-1>', self.charger_partie)

        # Saisie du choix de thème
        self.label_theme = Label(self, text='Entrez la couleur que vous désirez')
        self.label_theme.grid()
        self.entry_couleur = Entry(self, text='Entrez la couleur que vous désirez')
        self.entry_couleur.grid()
        self.entry_couleur.bind('<Return>', self.theme_couleur)

        # Bouton de règlements

    def selectionner(self, event):
        # Gestion des excpetions pour le choix de la pièce à bouger
        try:
            # On trouve le numéro de ligne/colonne en divisant les positions en y/x par le nombre de pixels par case.
            ligne = event.y // self.canvas_echiquier.n_pixels_par_case
            colonne = event.x // self.canvas_echiquier.n_pixels_par_case
            nb_pix = self.canvas_echiquier.n_pixels_par_case

            position = "{}{}".format(self.canvas_echiquier.lettres_colonnes[colonne],
                                     int(self.canvas_echiquier.chiffres_rangees[self.
                                         canvas_echiquier.n_lignes - ligne - 1]))

            if self.position_selectionnee is None:  # Permet de vérifier s'il s'agit du premier clic.
                piece = self.canvas_echiquier.pieces[position]
                couleur_piece = self.canvas_echiquier.partie.echiquier.couleur_piece_a_position(position)
                couleur_joueur_actif = self.canvas_echiquier.partie.joueur_actif

                # On change la valeur de l'attribut position_selectionnee.
                if couleur_piece == couleur_joueur_actif:
                    self.position_selectionnee = position

                    # On change la couleur de la case sélectionnée
                    debut_ligne = colonne * nb_pix
                    fin_ligne = debut_ligne + nb_pix
                    debut_colonne = ligne * nb_pix
                    fin_colonne = debut_colonne + nb_pix
                    self.canvas_echiquier.create_rectangle(debut_ligne, debut_colonne, fin_ligne, fin_colonne,
                                                           fill='yellow')
                    self.canvas_echiquier.dessiner_pieces()

                    # Label de la pièce sélectionnée
                    self.messages['foreground'] = 'black'
                    self.messages['text'] = 'Pièce sélectionnée : {} à la position {}. Cliquez de nouveau pour ' \
                                            'désélectionner la pièce.'.format(piece, self.position_selectionnee)
                else:
                    self.messages['foreground'] = 'red'
                    self.messages['text'] = " Attention! La pièce sélectionnée n'est pas de la bonne couleur."

            else:  # Gère le cas où il s'agit d'un deuxième clic soit la position cible
                if self.canvas_echiquier.partie.echiquier.deplacement_est_valide(self.position_selectionnee,position):
                    self.canvas_echiquier.partie.echiquier.deplacer(self.position_selectionnee, position)
                    self.canvas_echiquier.delete('piece')
                    self.canvas_echiquier.dessiner_cases()
                    self.canvas_echiquier.dessiner_pieces()
                    self.position_selectionnee = None

                    if self.canvas_echiquier.partie.determiner_gagnant() == 'aucun':
                        self.canvas_echiquier.partie.joueur_suivant()
                        self.compteur = 0

                        self.messages['foreground'] = 'black'
                        self.messages['text'] = 'Au tour du joueur {}. '.format(self.canvas_echiquier.partie.
                                                                                joueur_actif)
                    else:
                        self.messages['foreground'] = 'green'
                        self.messages['text'] = 'Félécitation! Joueur {} vous avez gagner!. '.format(
                            self.canvas_echiquier.partie.determiner_gagnant())
                else:
                    if self.position_selectionnee == position:
                        self.canvas_echiquier.dessiner_cases()
                        self.canvas_echiquier.dessiner_pieces()
                        self.position_selectionnee = None
                        self.messages['foreground'] = 'black'
                        self.messages['text'] = 'Au tour du joueur {}. '.format(self.canvas_echiquier.partie.
                                                                                joueur_actif)
                    else:
                        self.messages['foreground'] = 'red'
                        self.messages['text'] = 'Attention! Ce déplacement est invalide'

        except KeyError:
            self.messages['foreground'] = 'red'
            self.messages['text'] = 'Erreur: Aucune pièce à cet endroit.'

        except IndexError:
            self.messages['foreground'] = 'red'
            self.messages['text'] = "Erreur: Vous n'êtes pas sur l'échiquier."

    def nouvelle_partie(self, event):

        # On réinitialise l'échiquier de départ.
        self.canvas_echiquier.partie.echiquier.initialiser_echiquier_depart()

        # On supprime les anciennes pièces et anciennes cases et on ajoute les nouvelles.
        self.canvas_echiquier.delete('piece')
        self.canvas_echiquier.delete('cases')
        self.canvas_echiquier.dessiner_cases()
        self.canvas_echiquier.dessiner_pieces()

        # Aucune position séléctionnnée
        self.position_selectionnee = None

        # Redémarer le compteur
        self.compteur = 0

        # Joueur débutant la partie
        self.canvas_echiquier.partie.joueur_actif = 'blanc'
        self.messages['foreground'] = 'black'
        self.messages['text'] = 'Le joueur {} débute la partie. '.format(self.canvas_echiquier.partie.joueur_actif)

    def sauvegarder_partie(self, event):
        colonnes = self.canvas_echiquier.lettres_colonnes
        lignes = self.canvas_echiquier.chiffres_rangees
        liste_position_possible = []
        for colonne in colonnes:
            for ligne in lignes:
                liste_position_possible.append(colonne+ligne)

        f = open('partie_echec', 'w')
        for position, pieces in self.canvas_echiquier.partie.echiquier.dictionnaire_pieces.items():
            f.write(position)
            f.write(str(pieces))
            f.write('\n')

        f.write(self.canvas_echiquier.partie.joueur_actif)

        self.messages['foreground'] = 'black'
        self.messages['text'] = "Votre partie a bien été sauvegardée."
        f.close()

    def charger_partie(self,event):
        self.canvas_echiquier.delete('piece')
        f = open('partie_echec', 'r')
        liste_piece_position = f.readlines()
        liste_position = []
        liste_piece = []

        for element in liste_piece_position:
            liste_position.append(element[:2])
            liste_piece.append(element[2:4])

        # liste_pos_enlever = []
        # for j in self.canvas_echiquier.partie.echiquier.dictionnaire_pieces:
        #     if j not in liste_position:
        #         liste_pos_enlever.append(j)
        #
        # for k in liste_pos_enlever:
        #     del(self.canvas_echiquier.partie.echiquier.dictionnaire_pieces[k])

        for i in range(len(liste_position)):
            self.canvas_echiquier.partie.echiquier.dictionnaire_pieces[str(liste_position[i])] = liste_piece[i]

        #self.canvas_echiquier.dessiner_pieces()

    def theme_couleur(self, event):
        dictionnaire_couleur = {'rouge': 'red',
                                'bleu': 'blue',
                                'vert': 'green',
                                'jaune': 'yellow',
                                'orange': 'orange',
                                'mauve': 'purple',
                                'violet': 'purple',
                                'rose': 'pink',
                                'gris': 'grey',
                                'noir': 'black',
                                'brun': 'brown'}
        couleur_choisis = str(self.entry_couleur.get())

        if couleur_choisis in dictionnaire_couleur:
            couleur_anglais = dictionnaire_couleur[couleur_choisis]
            self.canvas_echiquier.couleur_theme = couleur_anglais
            self.canvas_echiquier.dessiner_cases()
            self.canvas_echiquier.dessiner_pieces()
            self.entry_couleur.delete(0, END)
            self.compteur = 0
        else:
            self.messages['foreground'] = 'red'
            self.messages['text'] = "Erreur: La couleur entrée n'est pas valide."
            self.entry_couleur.delete(0, END)

    def regles(self, event):
        webbrowser.open(self.url)

    def debut_temps(self, event):
        "Incrémente le compteur à chaque seconde"
        #global compteur
        if self.compteur == 60:
            self.compteur = 0
            self.compteur_label['text'] = str(self.compteur)

        else:
            self.compteur += 1
            self.compteur_label['text'] = str(self.compteur)
            self.after(1000, self.debut_temps, self)

    def arret_temps(self, event):
        self.compteur = 60








## Essais de Fenetre de bienvenue:
# class CanvasImage(Canvas):
#     def __init__(self, parent):
#
#         # Appel du constructeur de la classe de base (Canvas).
#         super().__init__(parent, width=30,height=50)
#
#         # Ajout d'une image d'accueil.
#         image = Image.open("/Users/vincentcharest/Documents/Université/H20/Python/111156019_tp4/pychecs2/interface/image.jpg")
#         photo = ImageTk.PhotoImage(image)
#         print(photo)
#         #self.insert(INSERT, '\n')
#         self.create_image(0, 0, image=photo)
#
#
# class FenetreAccueil(Tk):
#
#     def __init__(self):
#         super().__init__()
#
#         # Nom de la fenêtre.
#         self.title("Partie d'échec!")
#
#         # La position sélectionnée.
#         self.position_selectionnee = None
#
#         # Truc pour le redimensionnement automatique des éléments de la fenêtre.
#         #self.grid_columnconfigure(0, weight=1)
#         #self.grid_rowconfigure(0, weight=1)
#
#         # Création du canvas image.
#         self.canvas_image = CanvasImage(self)
#         self.canvas_image.grid()

        # Ajout d'un message d'accueil.
        # self.texte_accueil = Text(self, height=7, width=50)
        # self.texte_accueil.grid()
        # self.texte_accueil.insert(INSERT, "\n             Bienvenue au jeu d'échec!\n\n\n\nVoici vos options:")

        # # On lie un clic sur le CanvasEchiquier à une méthode.
        # self.canvas_echiquier.bind('<Button-1>', self.selectionner)
        #
        # Bouton Nouvelle Partie
        #self.button_nouvelle_partie = Button(self, text='Nouvelle Partie')
        #self.button_nouvelle_partie.grid()
        #self.button_nouvelle_partie.bind('<Button-1>', self.nouvelle_partie)
        #
        # # Bouton Sauvegarder la Partie
        # self.button_save = Button(self, text='Sauvegarder la Partie')
        # self.button_save.grid()
        # self.button_save.bind('<Button-1>', self.sauvegarder_partie)
        #
        # # Bouton charger Partie
        # self.button_load = Button(self, text='Charger une partie')
        # self.button_load.grid()
        # self.button_load.bind('<Button-1>', self.charger_partie)
        #
        # # Saisie du choix de thème
        # self.label_theme = Label(self, text='Entrez la couleur que vous désirez')
        # self.label_theme.grid()
        # self.entry_couleur = Entry(self, text='Entrez la couleur que vous désirez')
        # self.entry_couleur.grid()
        # self.entry_couleur.bind('<Return>', self.theme_couleur)
