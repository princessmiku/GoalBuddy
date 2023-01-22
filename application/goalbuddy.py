import sqlite3
import sys
from sys import argv

from plyer import notification
from terminaltables import AsciiTable

db = sqlite3.connect("goalbuddy.db")

print(argv)


class Goal:

    def __init__(self, title, description, finish: int, *, id=None):
        self.id: int = id
        self.title: str = title
        self.description: str = description
        self.finish: bool = bool(finish)

    def save(self):
        if self.id is not None:
            db.execute(
                'UPDATE goals SET title=?, description=?, finish=? WHERE id=?',
                [self.title, self.description, int(self.finish), self.id]
            )
            db.commit()
        else:
            db.execute(
                'INSERT INTO goals(title, description, finish) VALUES (?, ?, ?)',
                [self.title, self.description, int(self.finish)]
            )
            db.commit()

    def last_id(self):
        return db.execute("SELECT seq FROM sqlite_sequence WHERE name='goals'").fetchone()[0]

def print_header():
    print("Goal Buddy")
    print(" ")

print_header()
if len(argv) < 1 or argv[1] == "-help":
    print("befehls Beispiel aufbau | goalbuddy.py -help")
    table = AsciiTable([
        ["Befehl", "Beschreibung"],
        ["-help", "rufe diese Hilfe seite auf"],
        ['add "title" "description"', "füge ein Ziel der Liste hinzu"],
        ["list", "liste alle Ziele auf"],
        ["finish id", "setze ein Ziel als erledigt"],
        ["remove id", "entferne ein Ziel von der Liste"],
        ["cleanup", "räume deine Liste durch das Löschen erledigter Ziele auf"],
        ["notifi", "sende eine benachrichtigung das offene Ziele existieren"]
    ], "Hilfe seite")
    print(table.table)
elif argv[1] == "add":
    if len(argv) < 4:
        print("invalid arguments")
        sys.exit()
    goal = Goal(argv[2], argv[3], False)
    goal.save()
    table = AsciiTable([
        [],
        ["name", argv[2]],
        ["beschreibung", argv[3]],
        ["id", goal.last_id()]
    ], "Ziel Hinzugefügt")
    print(table.table)

elif argv[1] == "list":
    data = db.execute("select * from goals").fetchall()
    display_data = []
    for d in data:
        display_data.append([d[0], d[1], d[2], "Ja" if d[3] == 1 else "Nein"])

    table = AsciiTable([["id", "titel", "beschreibung", "erledigt"]] + display_data)
    print(table.table)
elif argv[1] == "finish":
    if len(argv) < 3:
        print("invalid arguments")
        sys.exit()
    if not argv[2].isnumeric():
        print("invalid arguments")
        sys.exit()
    if len(db.execute("SELECT id FROM goals where id=?", [int(argv[2])]).fetchall()) == 0:
        print("Die ID konnte keinem Goal zugeordnet werden")
        sys.exit()
    db.execute("UPDATE goals SET finish=1 WHERE id=?", [int(argv[2])])
    db.commit()
    print("Goal wurde als erledigt gekennzeichnet")
elif argv[1] == "remove":
    if len(argv) < 3:
        print("invalid arguments")
        sys.exit()
    if not argv[2].isnumeric():
        print("invalid arguments")
        sys.exit()
    if len(db.execute("SELECT id FROM goals where id=?", [int(argv[2])]).fetchall()) == 0:
        print("Die ID konnte keinem Goal zugeordnet werden")
        sys.exit()
    db.execute("DELETE FROM goals WHERE id=?", [int(argv[2])])
    db.commit()
    print("Goal wurde gelöscht")
elif argv[1] == "cleanup":
    db.execute("DELETE FROM goals WHERE finish=?", [1])
    db.commit()
    print("Abgeschlossende Ziele wurden gelöscht")
elif argv[1] == "notifi":
    if len(db.execute("SELECT id FROM goals where finish=0").fetchall()) == 0:
        print("Es gibt keine Offenen Ziele")
        sys.exit()
    notification.notify(
        title="Goal Buddy",
        message="Du hast noch offene Ziele, schaue deine aktuellen Ziele an",
        timeout=10,
        app_icon="./images/logo.ico"
    )
else:
    print("invalid argument, schaue dir die Hilfeseite an")