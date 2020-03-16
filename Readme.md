# Word Engine

Ce moteur fait partie de la collection des `publiposting-engine` d'api-doc2


Il permet de pousser les document `Word` publiposté sur un serveur compatible S3

## Endpoints

### POST /configure

Sur cet endpoint le client est configuré

Il reçoit sa configuration minio et cela lui permet d'initialiser sa connexion au dépot de documents

200 en cas de réussite et 500 en cas d'erreur

### POST /load_templates

Sur cet endpoint son indiqué quels templates charger depuis le dépot

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


Il renvoit une liste de sucess et error


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

Actuellement les options ne sont pas prises en compte sur ce moteur

Le résutat renvoyé actuellement est juste un boolean donnant le succès ou l'échec de l'opération

## Comment ça marche

Cette application repose la bibliothèque de publipostage docxTpl écrite en python 
et qui repose sur le moteur de template Jinja2.

Il est donc possible de faire du templating de façon assez puissante dans le document

La syntaxe est donc celle du Jinja2 à quelques exceptions près.
