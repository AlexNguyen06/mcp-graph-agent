from pathlib import Path
from typing import Any, Callable
import ast
import json
import select
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.invalidator_tool import invalidate_conjecture
from tools.verify_counterexample_tool import verify_counterexample_from_path

WORKSPACE = PROJECT_ROOT / "workspace"
WORKSPACE.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".py", ".md", ".txt", ".json", ".yaml", ".yml", ".toml"}
MAX_FILE_SIZE = 200_000

def invalidate_annor():
    """
    Test the Annor domination conjecture ANNOR-001.
    """
    return invalidate_conjecture("data/conjectures/annor/ANNOR-001.json")


def invalidate_from_path(conjecture_path: str):
    """
    Test a graph theory conjecture from a local JSON file path.
    Example: data/conjectures/annor/ANNOR-001.json
    """
    return invalidate_conjecture(conjecture_path)


def verify_counterexample_from_path_tool(conjecture_path: str):
    """
    Verify the known graph6 counterexample stored in a conjecture JSON file.
    """
    return verify_counterexample_from_path(conjecture_path)


verify_counterexample_from_path_tool.__name__ = "verify_counterexample_from_path"


def resolve_safe_path(path: str) -> Path:
    candidate = Path(path)

    if candidate.is_absolute():
        raise ValueError("Chemin absolu interdit.")

    target = (WORKSPACE / candidate).resolve()

    if target != WORKSPACE and WORKSPACE not in target.parents:
        raise ValueError("Chemin hors du workspace interdit.")

    if target == WORKSPACE:
        raise ValueError("Impossible d'utiliser le workspace comme fichier.")

    return target


def validate_extension(path: Path) -> None:
    if path.suffix and path.suffix not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Extension non autorisée : {path.suffix}")


def list_files() -> str:
    """Liste les fichiers dans le workspace."""
    files = sorted(
        str(p.relative_to(WORKSPACE))
        for p in WORKSPACE.rglob("*")
        if p.is_file()
    )
    return "\n".join(files) if files else "Aucun fichier dans le workspace."


def read_file(path: str) -> str:
    """Lit un fichier texte dans le workspace."""
    target = resolve_safe_path(path)
    validate_extension(target)

    if not target.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")

    return target.read_text(encoding="utf-8")


def write_file(path: str, content: str, overwrite: bool = False) -> str:
    """Écrit un fichier texte dans le workspace."""
    target = resolve_safe_path(path)
    validate_extension(target)

    if len(content.encode("utf-8")) > MAX_FILE_SIZE:
        raise ValueError("Fichier trop volumineux.")

    if target.exists() and not overwrite:
        raise FileExistsError(
            f"Le fichier {target.relative_to(WORKSPACE)} existe déjà. "
            "Utilise overwrite=True si tu veux l'écraser."
        )

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")

    return f"Fichier écrit : {target.relative_to(WORKSPACE)}"


AVAILABLE_TOOLS: dict[str, Callable[..., str]] = {
    "list_files": list_files,
    "read_file": read_file,
    "write_file": write_file,
    "invalidate_annor": invalidate_annor,
    "tool_invalidate_annor": invalidate_annor,
    "invalidate_from_path": invalidate_from_path,
    "tool_invalidate_from_path": invalidate_from_path,
    "verify_counterexample_from_path": verify_counterexample_from_path_tool,
    "tool_verify_counterexample_from_path": verify_counterexample_from_path_tool
}

CONJECTURE_PATH_TOOLS = {
    "invalidate_from_path",
    "verify_counterexample_from_path"
}

INVALID_CONJECTURE_PATH_MESSAGE = (
    "Invalid conjecture_path. Expected a relative JSON path such as "
    "data/conjectures/annor/ANNOR-001.json"
)


SYSTEM_PROMPT = """
Tu as accès à l’outil suivant :
invalidate_annor :
Utilise cet outil lorsque l’utilisateur demande de tester, valider, réfuter ou trouver un contre-exemple à la conjecture de domination d’Annor.
Cet outil exécute une recherche locale sur des graphes ainsi qu’un vérificateur indépendant.
Il retourne un résultat JSON contenant le statut, les informations de recherche, le meilleur graphe testé, les invariants et le résultat de la vérification.
Si l’outil retourne "no_counterexample_found", explique qu’il s’agit seulement d’une recherche échouée, et non d’une preuve mathématique.
Si l’outil retourne "counterexample_found", explique que la conjecture est réfutée uniquement si le vérificateur confirme que le graphe satisfait les hypothèses et viole l’inégalité.

invalidate_from_path:
Use this tool when the user gives a JSON conjecture path and asks to test, validate, refute, or find a counterexample.
The path must be relative to the project root.
Example: data/conjectures/annor/ANNOR-001.json

verify_counterexample_from_path:
Use this tool when the user wants to verify a known graph6 counterexample stored in a conjecture JSON file.
The path must be relative to the project root.
Example: data/conjectures/hdr_false/HDR-001.json

/no_think
Tu es un agent local de programmation.
Tu peux utiliser les outils list_files, read_file, write_file, invalidate_annor, invalidate_from_path et verify_counterexample_from_path.
Tu n’as pas accès directement au disque.
Pour créer un fichier, tu dois appeler write_file.
Pour lire un fichier, tu dois appeler read_file.
Pour lister les fichiers, tu dois appeler list_files.
list_files ne prend aucun argument path.
Le marqueur /no_think n’est jamais un argument d’un outil et ne doit jamais être utilisé comme conjecture_path.
Si l’utilisateur demande plusieurs étapes, continue les étapes demandées après chaque appel d’outil; ne t’arrête pas après list_files.
Utilise uniquement des chemins relatifs.
N’affirme jamais qu’un fichier a été écrit avant d’avoir reçu le résultat de l’outil.
""".strip()


def normalize_arguments(arguments: Any) -> dict[str, Any]:
    if isinstance(arguments, dict):
        return arguments
    if isinstance(arguments, str):
        return json.loads(arguments)
    return {}


def validate_conjecture_path_argument(args: dict[str, Any]) -> None:
    conjecture_path = args.get("conjecture_path")

    if (
        not isinstance(conjecture_path, str)
        or conjecture_path == "/no_think"
        or not conjecture_path.endswith(".json")
        or conjecture_path.startswith("/")
    ):
        raise ValueError(INVALID_CONJECTURE_PATH_MESSAGE)


def parse_tool_result(tool_result: Any) -> Any:
    if not isinstance(tool_result, str):
        return tool_result

    try:
        return json.loads(tool_result)
    except Exception:
        pass

    try:
        return ast.literal_eval(tool_result)
    except Exception:
        return tool_result


def summarize_tool_result(tool_result: Any) -> str:
    parsed_result = parse_tool_result(tool_result)

    if not isinstance(parsed_result, dict):
        return str(tool_result)

    conjecture_id = parsed_result.get("conjecture_id", "conjecture inconnue")
    status = parsed_result.get("status")
    search = parsed_result.get("search") or {}
    best_result = parsed_result.get("best_result") or {}
    verification = parsed_result.get("verification") or {}

    evaluated = search.get("evaluated")
    best_gap = parsed_result.get("best_gap")
    best_violation_score = parsed_result.get("best_violation_score")
    conjecture_satisfied = best_result.get(
        "conjecture_satisfied",
        verification.get("conjecture_satisfied")
    )
    is_counterexample = best_result.get(
        "is_counterexample",
        verification.get("is_counterexample", parsed_result.get("is_counterexample"))
    )
    message = parsed_result.get("message")

    counterexample_found = status == "counterexample_found" or is_counterexample is True
    counterexample_text = "oui" if counterexample_found else "non"

    lines = [
        f"Résultat pour {conjecture_id} :",
        f"- Statut : {status if status is not None else 'non renseigné'}",
        f"- Graphes évalués : {evaluated if evaluated is not None else 'non renseigné'}",
        f"- Best gap : {best_gap if best_gap is not None else 'non renseigné'}",
        f"- Best violation score : {best_violation_score if best_violation_score is not None else 'non renseigné'}",
        f"- Conjecture satisfaite pour le meilleur résultat : {conjecture_satisfied if conjecture_satisfied is not None else 'non renseigné'}",
        f"- Contre-exemple trouvé : {counterexample_text}",
    ]

    if counterexample_found:
        lines.append("")
        lines.append("Un contre-exemple a été trouvé et vérifié.")
    elif status == "no_counterexample_found":
        lines.append("")
        lines.append(
            "Aucun contre-exemple n’a été trouvé dans les limites de la recherche. "
            "Ce n’est pas une preuve mathématique : cela signifie seulement que "
            "l’invalidateur n’a pas trouvé de graphe qui viole l’inégalité."
        )
    elif message:
        lines.append("")
        lines.append(str(message))

    return "\n".join(lines)


def run_agent(user_request: str, model: str = "qwen3:8b", max_steps: int = 5) -> str:
    from ollama import chat

    last_tool_result = None

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_request},
    ]

    for step in range(max_steps):
        print(f"[debug] étape {step + 1}: appel du modèle...")

        response = chat(
            model=model,
            messages=messages,
            tools=list(AVAILABLE_TOOLS.values()),
            think=False,
            stream=False,
            options={
                "temperature": 0,
                "num_predict": 500,
                "num_ctx": 2048,
            },
        )

        assistant_message = response.message
        messages.append(assistant_message)

        tool_calls = assistant_message.tool_calls or []

        if not tool_calls:
            if assistant_message.content:
                return assistant_message.content
            if last_tool_result is not None:
                return summarize_tool_result(last_tool_result)
            return ""

        for call in tool_calls:
            tool_name = call.function.name
            raw_args = call.function.arguments

            print(f"[tool] {tool_name}({raw_args})")

            if tool_name not in AVAILABLE_TOOLS and tool_name.startswith("tool_"):
                normalized_tool_name = tool_name.removeprefix("tool_")
            else:
                normalized_tool_name = tool_name

            if normalized_tool_name not in AVAILABLE_TOOLS:
                tool_result = f"Erreur : outil inconnu {tool_name}"
            else:
                try:
                    if normalized_tool_name in CONJECTURE_PATH_TOOLS and isinstance(raw_args, str):
                        raw_args_str = raw_args.strip()
                        if raw_args_str and not raw_args_str.startswith("{"):
                            args = {"conjecture_path": raw_args_str}
                        else:
                            args = normalize_arguments(raw_args)
                    else:
                        args = normalize_arguments(raw_args)

                    if "path" in args and "conjecture_path" not in args:
                        args["conjecture_path"] = args["path"]
                    if normalized_tool_name in CONJECTURE_PATH_TOOLS:
                        validate_conjecture_path_argument(args)
                    tool_result = AVAILABLE_TOOLS[normalized_tool_name](**args)
                except Exception as exc:
                    tool_result = f"Erreur pendant {normalized_tool_name} : {exc}"

            last_tool_result = tool_result

            print(f"[result] {tool_result}")

            messages.append({
                "role": "tool",
                "tool_name": normalized_tool_name,
                "content": str(tool_result),
            })

    if last_tool_result is not None:
        return summarize_tool_result(last_tool_result)

    return "Arrêt : trop d'étapes."


def collect_pasted_prompt(first_line: str) -> str:
    lines = [first_line]

    while "/no_think" not in "\n".join(lines):
        readable, _, _ = select.select([sys.stdin], [], [], 0.05)
        if not readable:
            break

        next_line = sys.stdin.readline()
        if not next_line:
            break

        lines.append(next_line.rstrip("\n"))

    return "\n".join(lines).strip()


def main() -> None:
    print(f"Workspace autorisé : {WORKSPACE}")
    print("Tape exit pour quitter.")
    print()

    while True:
        prompt = collect_pasted_prompt(input("> ").strip())

        if prompt.lower() in {"exit", "quit"}:
            break

        if not prompt:
            continue

        answer = run_agent(prompt)
        print("\n" + answer + "\n")


if __name__ == "__main__":
    main()
