# Plan de refonte — gestion des objets Python

Améliorations à mener **avant** d'implémenter les fonctionnalités listées dans la
section `Todo` du [README](README.md). Chaque point est justifié par les todos
qu'il rend plus simples ou plus sûrs à écrire.

Ordre conseillé : 1 → 2 → 3 + 4 → 5 / 6 juste avant les todos `edit` → 7 avec le
todo « afficher les commentaires ».

---

## 1. Typer `AppState.jira_client` (fait)

**Problème** — `app/utils/app_state.py` déclare `jira_client: object` : aucune
vérification de type ni autocomplétion sur tous les appels Jira du projet.

**Impact todos** — les fonctionnalités restantes ajoutent une dizaine d'appels API
(`add_worklog`, `create_issue_link`, `comments`, `assign_issue`…).

**Action** — typer le champ en `JIRA`, et figer la dataclass (`frozen=True`,
`slots=True`) puisque l'état n'est jamais muté après le callback.

## 2. Config : TypedDict → dataclass (fait)

**Problème** — la config est un `TypedDict` lu par indexation
(`ctx.obj.config["default"]["project"]`), sans validation. Une clé absente de
`config.toml` produit un `KeyError` brut au milieu d'une commande. Le motif
« option CLI sinon valeur de config » est recopié à la main dans chaque commande.

**Impact todos** — 5 todos ajoutent exactement ce motif (`--project`, `--status`,
`--assignee` sur `get issues`, labels sur `edit`).

**Action**

- `DefaultConfig` / `AppConfig` en dataclasses gelées, accès `config.default.project` ;
- construction depuis le TOML dans une méthode dédiée qui **valide** les clés et
  lève une erreur lisible (`InvalidConfigError`) rendue par le callback ;
- helper `AppConfig.resolve(override, key)` : renvoie l'override CLI s'il est
  fourni, sinon la valeur de config — en distinguant `None` de `0` / `""`.

## 3. Unifier la signalisation des erreurs

**Problème** — quatre styles pour la même chose :

| Cas | Où | Comment |
| --- | --- | --- |
| Variable d'env manquante | `main.py` | `try/except` manuel |
| Statut invalide | `edit.py` | `@handle_jira_errors` |
| Utilisateur introuvable / ambigu | `create.py` | `console.print` + `typer.Exit` |
| Type de ticket introuvable | `get.py` | `console.print` + `typer.Exit` |

**Impact todos** — au moins trois nouveaux cas d'erreur métier arrivent (label
inexistant, parent invalide, type de lien inconnu).

**Action** — une base `CliJiraError` portant un message français, attrapée par
`handle_jira_errors`. Les commandes ne font plus que `raise` ; le rendu vit à un
seul endroit.

## 4. Extraire la résolution d'assignee

**Problème** — `create.py` mélange dans un même bloc la résolution de
`--owned` / `--owner`, l'affichage et la sortie du programme.

**Impact todos** — « UPDATE - Réassigner un ticket » a besoin de la même logique
dans `edit.py` ; en l'état elle serait dupliquée, `console.print` compris.

**Action** — `resolve_assignee(jira, owned, owner) -> dict | None`, qui **lève**
(cf. point 3) au lieu d'imprimer.

## 5. Découpler les fonctions « service » de Typer

**Problème** — `get_transitions_from_issue(ctx, issue)` et
`get_statuses_for_issue_type(ctx, issue_type)` prennent un `typer.Context` alors
qu'elles n'ont besoin que du client et de la clé projet.

**Action** — soit passer `(jira, project)`, soit introduire un `JiraService`
portant client + projet, exposé par `AppState`. Les commandes redeviennent de la
simple traduction d'arguments. Les tests continuent de mocker le même point
d'injection (`conftest.py::mock_jira_client`).

## 6. Constructeur partagé pour le dict `fields`

**Problème** — `create.py` et `edit.py` construisent les mêmes formes imbriquées
(`{"key": ...}`, `{"timetracking": {"estimate": ...}}`, labels). La liste des
champs demandés à Jira a déjà divergé entre `get.py` et `edit.py`
(`timetracking` présent d'un côté seulement).

**Impact todos** — statut, parent, summary et labels arrivent **des deux côtés**.

**Action** — un `IssueFields` (dataclass + `to_jira()`) et une constante
`ISSUE_FIELDS` unique pour la liste des champs récupérés.

## 7. Normaliser l'objet affiché

**Problème** — `display.py` lit `issue.fields.*` directement, avec des `getattr`
de secours dispersés. Conséquence déjà visible : `timetracking` est écrit par
`create` et `edit`, re-demandé explicitement à Jira par `edit`… mais **jamais
affiché**. L'estimation posée est invisible en sortie.

**Impact todos** — commentaires, worklog et liens entre tickets ajoutent autant
de champs optionnels à afficher.

**Action** — un `IssueView.from_issue(issue)` qui normalise une fois pour toutes
les champs optionnels (assignee `None`, labels absents, timetracking vide), et
qui affiche l'estimation.
