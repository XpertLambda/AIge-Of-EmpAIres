import webbrowser  # Add this import at the top
import os  # Add this import at the top

def write_html(team):
    """
    Génère une page HTML avec les informations du joueur sélectionné.
    
    Args:
        team (Team): L'objet Team représentant le joueur sélectionné.
    """
    template = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Données du jeu - Joueur {team.nb}</title>
    </head>
    <body>
        <h1>Données du jeu - Joueur {team.nb}</h1>
        
        <h2>Arme</h2>
        <details>
            <summary>Unités</summary>
    """
    
    for unit in team.units:
        template += f"""
            <p>
                <b>ID</b>: {unit.id}<br>
                <b>Acronyme</b>: {unit.acronym}<br>
                <b>Tâche</b>: {unit.task}<br>
                <b>HP</b>: {unit.hp}<br>
                <b>Position</b>: ({unit.x}, {unit.y})<br>
            </p>
        """
    
    template += """
        </details>
        
        <h2>Bâtiments</h2>
        <details>
            <summary>Bâtiments</summary>
    """
    
    for building in team.buildings:
        template += f"""
            <p>
                <b>Type</b>: {type(building).__name__}<br>
                <b>Position</b>: ({building.x}, {building.y})<br>
            </p>
        """
    
    template += """
        </details>
    </body>
    </html>
    """
    
    # Enregistrer le fichier HTML avec un nom unique pour chaque joueur
    filename = f"donnees_player_{team.nb}.html"
    with open(filename, "w", encoding="utf-8") as file:  # Specify encoding
        file.write(template)
    
    print(f"Données du joueur {team.nb} enregistrées dans {filename}.")
    
    webbrowser.open(f'file:///{os.path.abspath(filename)}')  # Add this line to open the HTML file