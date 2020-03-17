# Word Engine

Ce moteur fait partie de la collection des `publiposting-engine` d'api-doc2


Il permet de pousser les document `Word` publiposté sur un serveur compatible S3

## Endpoints

### POST /configure

Sur cet endpoint le client est configuré

Il reçoit sa configuration minio et cela lui permet d'initialiser sa connexion au dépot de documents

```json
{
    "host":"host",
    "access_key":"access_key",
    "pass_key":"pass_key"
}
```

200 en cas de réussite et 500 en cas d'erreur

Tant que l'api n'a pas été configurée par une requête HTTP sur cet endpoint elle va renvoyer un message d'erreur disant qu'elle n'est pas configurée.

Pour utiliser ce moteur en standalone il faut le donc le configurer en HTTP.

### POST /load_templates

Sur cet endpoint sont indiqués quels templates charger depuis le dépot

```json
[
    {
        "template_name":"name",
        "bucket_name":"nale"
    },
    {
        "template_name":"name",
        "bucket_name":"nale"
    },   
]
```

- `template_name` est donc le chemin d'accès ou aller chercher le document, il sera exposé avec le même nom pour la suite des actions.
- `bucket_name` est simplement le nom du bucket dans lequel aller charger le document

La requête contient donc une liste d'objet contenant ces deux informations.

Il renvoit une liste de success et error

### POST /get_placeholders

```json
{
    "name": "template_name"
}
```

Renvoie toutes les variables du document sous la forme d'une liste de string

### POST /publipost

Sur cet endpoint on peut publiposter des documents

```json
{
    "data":{},
    "name":"template_name",
    "output_bucket": "name",
    "output_name": "name",
    "options":{
        "push_result": true
    }
}
```

- `data` est un JSON arbitraire qui sera utilisé pour mettre les informations dans le document
- `name` est le nom du template à utilisé
- `output_bucket` nom du bucket sur lequel poussé le fichier de sortie
- `output_name` nom du fichier de sortie
- `options` contient les options de rendu (pour l'instant, il n'y a pas de support)

Le résutat renvoyé actuellement est juste un boolean donnant le succès ou l'échec de l'opération

## Comment ça marche

Cette application repose la bibliothèque de publipostage docxTpl écrite en python 
et qui repose sur le moteur de template Jinja2.

Il est donc possible de faire du templating de façon assez puissante dans le document

La syntaxe est donc celle du Jinja2 à quelques exceptions près.


## Comment run

### En prod 

Le Dockerfile permet de construire une image Docker exposant l'application sur le port `5000`, il suffit donc de mettre cette application derrière la gateway api-doc2

Pour cela rien de très compliqué, il faut juste indiqué dans la conf d'api-doc2 l'addresse et le port de ce container

### En dev

Apres avoir installé le `requirements.txt` on peut faire 
```bash 
$ ./start_dev.sh
``` 
pour démarrer l'application.

Normalement il n'y a presque rien à faire sur ce moteur, toute la manipulation de données se déroule sur api-doc2.

### Utiliser en vrai

Le moteur ici ne sait pas manipuler les données et ça tombe bien ce n'est pas son rôle. Ici le moteur est bête et toute l'intelligence se trouve dans api-doc2.

Pourquoi faire comme ça ?

Eh bien cela permet de séparer les problèmes en cas de bug.

De plus cela permet d'avoir un seul endroit ou les données sont manipulées, du coup aucun des moteur n'a besoin de savoir le faire.

Ainsi quand ce moteur parse le champs :

`mission.StudentDocRef___student_REM__`

c'est api-doc2 qui fait la transformation vers `mission.StudentDocRef(#student, "REM")` et le jour les règles de parsing changent alors on peut mettre à jour d'un coup pour tous les moteurs.

Du coup c'est assez simple à utiliser, il suffit d'utiliser l'opérateur "." pour traverser l'objet et avoir la propriété qui nous interresse.

## TODO

- ajouter le renvoie du doc compléter dans la reqûete en option, cela permet de ne pas utiliser de client S3 si on en a pas besoin
- ajouter le choix d'upload le template directement dans le /load_templates
