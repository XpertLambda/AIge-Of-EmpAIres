import webbrowser
import os
from Entity.Resource.Resource import Resource

def write_full_html(players, game_map):
    template = """
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Snapshot complet du jeu</title>
    </head>
    <body>
        <h1>Snapshot du jeu</h1>
    """

    for team in players:
        template += f"""
        <h2>Joueur {team.teamID}</h2>
        <details>
            <summary>infos générales</summary>
            <p>
                <!-- Exemples : mimic create_player_info_surface -->
                <b>Resources</b>: Food={team.resources.food}, Wood={team.resources.wood}, Gold={team.resources.gold}<br>
                <b>Population</b>: {team.population}/{team.maximum_population}<br>
            </p>
        </details>

        <details>
            <summary>Unités</summary>
            <ul>
        """
        for unit in team.units:
            template += f"""
            <li>
                <details>
                    <summary>Unité ID: {unit.id} ({unit.acronym})</summary>
                    <p>
                        <b>HP</b>: {unit.hp}/{unit.max_hp}<br>
                        <b>Position</b>: ({unit.x}, {unit.y})<br>
                        <!-- Add any other relevant unit information -->
                    </p>
                </details>
            </li>
            """
        template += """
            </ul>
        </details>

        <details>
            <summary>Bâtiments</summary>
            <ul>
        """
        for building in team.buildings:
            template += f"""
            <li>
                <details>
                    <summary>Bâtiment: {type(building).__name__}</summary>
                    <p>
                        <b>HP</b>: {building.hp}/{building.max_hp}<br>
                        <b>Position</b>: ({building.x}, {building.y})<br>
                        <!-- Add any other relevant building information -->
                    </p>
                </details>
            </li>
            """
        template += """
            </ul>
        </details>

        <details>
            <summary>Tâches en cours</summary>
            <ul>
        """
        # Display buildings/units under construction
        for entity, start_time in team.en_cours.items():
            template += f"""
            <li>{type(entity).__name__} en cours de construction/formation</li>
            """
        # Display busy units (e.g. collecting, fighting)
        for unit in team.units:
            if getattr(unit, 'task', False):
                template += f"""
            <li>Unit ID {unit.id} occupée: {unit.state}</li>
                """
        # Display buildings training units
        for building in team.buildings:
            if hasattr(building, 'current_training_unit') and building.current_training_unit:
                template += f"""
            <li>Bâtiment ID {building.entity_id} forme: {building.current_training_unit}</li>
                """
        template += """
            </ul>
        </details>
        """

    template += """
        <h2>Ressources sur la carte</h2>
        <details>
            <summary>Ressources</summary>
    """
    # Parcours des ressources dans la grille
    # On considère que game_map.grid contient des ressources
    for pos, entities in game_map.grid.items():
        for entity in entities:
            if isinstance(entity, Resource):
                template += f"""
                <p>
                    <b>Type</b>: {entity.acronym}<br>
                    <b>Position</b>: ({entity.x}, {entity.y})<br>
                    <b>Capacité restante</b>: {entity.storage}<br>
                </p>
                """

    template += """
        </details>
    </body>
    </html>
    """

    filename = "full_snapshot.html"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(template)
    webbrowser.open(f'file:///{os.path.abspath(filename)}')
