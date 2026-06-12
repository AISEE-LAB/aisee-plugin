"""Aisee CLI scaffold."""

from __future__ import annotations

import argparse
from pathlib import Path

from aisee_cli import __version__
from aisee_cli.bootstrap import build_bootstrap_plan
from aisee_cli.context_pack import build_context_pack
from aisee_cli.doctor import build_doctor
from aisee_cli.knowledge import (
    build_knowledge_check,
    build_knowledge_configure,
    build_knowledge_doctor,
    build_knowledge_init_repo,
    build_knowledge_index,
    build_knowledge_inspect,
    build_knowledge_install,
    build_knowledge_promote_batch,
    build_knowledge_query,
    build_knowledge_update,
)
from aisee_cli.memory import (
    build_memory_add,
    build_memory_inspect,
    build_memory_list,
    build_memory_query_for_context_pack,
    build_memory_search,
    build_memory_update_index,
)
from aisee_cli.openspec_init import run_openspec_init
from aisee_cli.output import error_response, exit_code_for, print_json
from aisee_cli.plugin_assets import inspect_plugin_assets, plugin_path
from aisee_cli.project import resolve_project_root
from aisee_cli.schema_pack import check_schema_packs, format_schema_packs, list_schema_packs


def main() -> int:
    parser = argparse.ArgumentParser(prog="aisee")
    parser.add_argument("--version", action="store_true", help="print version")
    subparsers = parser.add_subparsers(dest="command")
    doctor_parser = subparsers.add_parser("doctor")
    doctor_parser.add_argument("--json", action="store_true", help="output JSON")
    doctor_parser.add_argument("--fail-on-blocker", action="store_true", help="return non-zero when blockers exist")
    bootstrap_parser = subparsers.add_parser("bootstrap")
    bootstrap_parser.add_argument("--plan", action="store_true", help="output bootstrap plan")
    bootstrap_parser.add_argument("--json", action="store_true", help="output JSON")
    openspec_parser = subparsers.add_parser("openspec")
    openspec_parser.add_argument("--json", action="store_true", help="output JSON")
    openspec_subparsers = openspec_parser.add_subparsers(dest="openspec_command")
    openspec_ensure_parser = openspec_subparsers.add_parser("ensure")
    openspec_ensure_parser.add_argument(
        "--profile",
        default="expanded",
        help="Aisee OpenSpec workflow profile; supported: expanded, core; default: expanded",
    )
    openspec_ensure_parser.add_argument(
        "--tools",
        help="OpenSpec AI tools value for init; default: auto-detect current agent runtime, fallback: none",
    )
    openspec_ensure_parser.add_argument(
        "--skip-profile",
        action="store_true",
        help="do not align the global OpenSpec workflow profile",
    )
    openspec_ensure_parser.add_argument("--skip-update", action="store_true", help="do not run openspec update")
    openspec_ensure_parser.add_argument("--force", action="store_true", help="pass --force to openspec init when initialization is needed")
    openspec_ensure_parser.add_argument("--json", action="store_true", help="output JSON")
    plugin_parser = subparsers.add_parser("plugin")
    plugin_parser.add_argument("--json", action="store_true", help="output JSON")
    plugin_subparsers = plugin_parser.add_subparsers(dest="plugin_command")
    plugin_inspect_parser = plugin_subparsers.add_parser("inspect")
    plugin_inspect_parser.add_argument("--json", action="store_true", help="output JSON")
    plugin_path_parser = plugin_subparsers.add_parser("path")
    plugin_path_parser.add_argument("--target", choices=["codex", "claude", "cursor"], required=True, help="agent runtime target")
    plugin_path_parser.add_argument("--json", action="store_true", help="output JSON")
    schemas_parser = subparsers.add_parser("schemas")
    schemas_parser.add_argument("--json", action="store_true", help="output JSON")
    schemas_subparsers = schemas_parser.add_subparsers(dest="schemas_command")
    schemas_list_parser = schemas_subparsers.add_parser("list")
    schemas_list_parser.add_argument("--json", action="store_true", help="output JSON")
    schemas_check_parser = schemas_subparsers.add_parser("check")
    schemas_check_parser.add_argument("--json", action="store_true", help="output JSON")
    schemas_check_parser.add_argument("--fail-on-blocker", action="store_true", help="return non-zero when blockers exist")
    schemas_format_parser = schemas_subparsers.add_parser("format")
    schemas_format_parser.add_argument("--check", action="store_true", help="report formatting drift without writing")
    schemas_format_parser.add_argument("--write", action="store_true", help="rewrite schema.yaml files into canonical format")
    schemas_format_parser.add_argument("--json", action="store_true", help="output JSON")
    context_parser = subparsers.add_parser("context")
    context_parser.add_argument("--json", action="store_true", help="output JSON")
    context_subparsers = context_parser.add_subparsers(dest="context_command")
    pack_parser = context_subparsers.add_parser("pack")
    pack_parser.add_argument("--change", required=True, help="OpenSpec change name")
    pack_parser.add_argument("--for", dest="target", required=True, help="context target")
    pack_parser.add_argument("--knowledge", action="store_true", help="include knowledge guardrail matches")
    pack_parser.add_argument("--project-memory", action="store_true", help="include bounded project memory matches")
    pack_parser.add_argument("--json", action="store_true", help="output JSON")
    knowledge_parser = subparsers.add_parser("knowledge")
    knowledge_parser.add_argument("--json", action="store_true", help="output JSON")
    knowledge_subparsers = knowledge_parser.add_subparsers(dest="knowledge_command")
    knowledge_inspect_parser = knowledge_subparsers.add_parser("inspect")
    knowledge_inspect_parser.add_argument("--json", action="store_true", help="output JSON")
    knowledge_check_parser = knowledge_subparsers.add_parser("check")
    knowledge_check_parser.add_argument("--team-path", help="team knowledge repository path")
    knowledge_check_parser.add_argument("--json", action="store_true", help="output JSON")
    knowledge_init_parser = knowledge_subparsers.add_parser("init-repo")
    knowledge_init_parser.add_argument("--dest", required=True, help="destination path for the team knowledge repository")
    knowledge_init_parser.add_argument("--initial-pack", default="web-app", help="initial pack id to create; default: web-app")
    knowledge_init_parser.add_argument("--force", action="store_true", help="allow merging managed files into a non-empty directory")
    knowledge_init_parser.add_argument("--json", action="store_true", help="output JSON")
    knowledge_configure_parser = knowledge_subparsers.add_parser("configure")
    knowledge_configure_parser.add_argument("--path", required=True, help="team knowledge repository path or checkout path")
    knowledge_configure_parser.add_argument("--enable-pack", action="append", default=[], help="pack id to enable; can be repeated")
    knowledge_configure_parser.add_argument("--repo", help="optional remote repository URL")
    knowledge_configure_parser.add_argument("--ref", help="optional ref to pin")
    knowledge_configure_parser.add_argument("--max-cards", type=int, help="maximum knowledge matches to retrieve")
    knowledge_configure_parser.add_argument(
        "--include-project-candidates",
        choices=["true", "false"],
        help="whether retrieval should include project-local candidate knowledge",
    )
    knowledge_configure_parser.add_argument("--json", action="store_true", help="output JSON")
    knowledge_doctor_parser = knowledge_subparsers.add_parser("doctor")
    knowledge_doctor_parser.add_argument("--team-path", help="team knowledge repository path to compare with config")
    knowledge_doctor_parser.add_argument("--json", action="store_true", help="output JSON")
    knowledge_install_parser = knowledge_subparsers.add_parser("install")
    knowledge_install_parser.add_argument("--allow-dirty", action="store_true", help="allow dirty existing checkout")
    knowledge_install_parser.add_argument("--json", action="store_true", help="output JSON")
    knowledge_update_parser = knowledge_subparsers.add_parser("update")
    knowledge_update_parser.add_argument("--allow-dirty", action="store_true", help="allow dirty existing checkout")
    knowledge_update_parser.add_argument("--json", action="store_true", help="output JSON")
    knowledge_promote_parser = knowledge_subparsers.add_parser("promote-batch")
    knowledge_promote_parser.add_argument("--curation", required=True, help="curation report path")
    knowledge_promote_parser.add_argument("--team-path", required=True, help="team knowledge repository path")
    knowledge_promote_parser.add_argument("--pack", help="pack id to update")
    knowledge_promote_parser.add_argument("--category", default="general", help="card category directory")
    knowledge_promote_parser.add_argument("--activate", action="store_true", help="promote drafts as active cards")
    knowledge_promote_parser.add_argument("--json", action="store_true", help="output JSON")
    knowledge_query_parser = knowledge_subparsers.add_parser("query")
    knowledge_query_parser.add_argument("--phase", help="phase feature")
    knowledge_query_parser.add_argument("--surface", action="append", default=[], help="surface feature; can be repeated")
    knowledge_query_parser.add_argument("--schema", help="schema feature")
    knowledge_query_parser.add_argument("--stack", help="stack feature")
    knowledge_query_parser.add_argument("--query", help="free text query")
    knowledge_query_parser.add_argument("--from-change", help="OpenSpec change name to extract features from")
    knowledge_query_parser.add_argument("--for", dest="target", help="context target for --from-change")
    knowledge_query_parser.add_argument("--max-cards", type=int, help="maximum matches")
    knowledge_query_parser.add_argument("--debug", action="store_true", help="include matched body excerpts")
    knowledge_query_parser.add_argument("--json", action="store_true", help="output JSON")
    knowledge_index_parser = knowledge_subparsers.add_parser("index")
    knowledge_index_parser.add_argument("--team-path", help="team knowledge repository path")
    knowledge_index_parser.add_argument("--json", action="store_true", help="output JSON")
    memory_parser = subparsers.add_parser("memory")
    memory_parser.add_argument("--json", action="store_true", help="output JSON")
    memory_subparsers = memory_parser.add_subparsers(dest="memory_command")
    memory_inspect_parser = memory_subparsers.add_parser("inspect")
    memory_inspect_parser.add_argument("--json", action="store_true", help="output JSON")
    memory_list_parser = memory_subparsers.add_parser("list")
    memory_list_parser.add_argument("--type", dest="types", action="append", default=[], help="memory type filter; can be repeated")
    memory_list_parser.add_argument("--status", help="memory status filter; default: active")
    memory_list_parser.add_argument("--priority", help="memory priority filter")
    memory_list_parser.add_argument("--include-body", action="store_true", help="include bounded body excerpts")
    memory_list_parser.add_argument("--json", action="store_true", help="output JSON")
    memory_search_parser = memory_subparsers.add_parser("search")
    memory_search_parser.add_argument("--query", required=True, help="task or topic query")
    memory_search_parser.add_argument("--type", dest="types", action="append", default=[], help="memory type filter; can be repeated")
    memory_search_parser.add_argument("--limit", type=int, help="maximum matches")
    memory_search_parser.add_argument("--include-body", action="store_true", help="include bounded body excerpts")
    memory_search_parser.add_argument("--include-stale", action="store_true", help="include stale entries")
    memory_search_parser.add_argument("--include-deprecated", action="store_true", help="include deprecated entries")
    memory_search_parser.add_argument("--json", action="store_true", help="output JSON")
    memory_add_parser = memory_subparsers.add_parser("add")
    memory_add_parser.add_argument("--type", dest="memory_type", required=True, help="memory type")
    memory_add_parser.add_argument("--title", required=True, help="memory title")
    memory_add_parser.add_argument("--summary", required=True, help="bounded memory summary")
    memory_add_parser.add_argument("--body", required=True, help="memory body")
    memory_add_parser.add_argument("--priority", default="normal", help="memory priority; default: normal")
    memory_add_parser.add_argument("--source-ref", action="append", default=[], help="source reference; can be repeated")
    memory_add_parser.add_argument("--json", action="store_true", help="output JSON")
    memory_update_index_parser = memory_subparsers.add_parser("update-index")
    memory_update_index_parser.add_argument("--json", action="store_true", help="output JSON")
    args = parser.parse_args()

    if args.version:
        print(f"aisee {__version__}")
        return 0

    if args.command == "doctor":
        root = resolve_project_root(Path.cwd())
        result = build_doctor(root)
        print_json(result)
        return exit_code_for(result, fail_on_blocker=args.fail_on_blocker)

    if args.command == "bootstrap":
        root = resolve_project_root(Path.cwd())
        result = build_bootstrap_plan(root)
        print_json(result)
        return exit_code_for(result, fail_on_blocker=False)

    if args.command == "openspec" and args.openspec_command is None:
        print_json(error_response("Use one of: ensure.", "MISSING_SUBCOMMAND"), stderr=True)
        return 2

    if args.command == "openspec" and args.openspec_command == "ensure":
        root = resolve_project_root(Path.cwd())
        result = run_openspec_init(
            root,
            profile=args.profile,
            tools=args.tools,
            skip_profile=args.skip_profile,
            skip_update=args.skip_update,
            force=args.force,
        )
        print_json(result)
        return exit_code_for(result, fail_on_blocker=True)

    if args.command == "plugin":
        root = resolve_project_root(Path.cwd())
        try:
            if args.plugin_command in {None, "inspect"}:
                result = inspect_plugin_assets(root)
                print_json(result)
                return exit_code_for(result, fail_on_blocker=True)
            if args.plugin_command == "path":
                result = plugin_path(root, args.target)
                print_json(result)
                return 0
        except ValueError as error:
            print_json(error_response(str(error)), stderr=True)
            return 2
        print_json(error_response("Use one of: inspect, path.", "MISSING_SUBCOMMAND"), stderr=True)
        return 2

    if args.command == "schemas":
        root = resolve_project_root(Path.cwd())
        if args.schemas_command in {None}:
            print_json(error_response("Use one of: list, check, format.", "MISSING_SUBCOMMAND"), stderr=True)
            return 2
        if args.schemas_command == "list":
            result = list_schema_packs(root)
            print_json(result)
            return 0
        if args.schemas_command == "check":
            result = check_schema_packs(root)
            print_json(result)
            return exit_code_for(result, fail_on_blocker=args.fail_on_blocker)
        if args.schemas_command == "format":
            if args.check and args.write:
                print_json(error_response("Use either --check or --write for schemas format.", "INVALID_ARGUMENT"), stderr=True)
                return 2
            result = format_schema_packs(root, check=args.check or not args.write, write=args.write)
            print_json(result)
            return exit_code_for(result, fail_on_blocker=False)
        print_json(error_response("Use one of: list, check, format.", "MISSING_SUBCOMMAND"), stderr=True)
        return 2

    if args.command == "context" and args.context_command is None:
        print_json(error_response("Use one of: pack.", "MISSING_SUBCOMMAND"), stderr=True)
        return 2

    if args.command == "context" and args.context_command == "pack":
        try:
            root = resolve_project_root(Path.cwd())
            pack = build_context_pack(root, args.change, args.target)
            if args.knowledge:
                knowledge = build_knowledge_query(root, from_change=args.change, target=args.target)
                pack["knowledge"] = compact_knowledge_for_context_pack(knowledge)
            if args.project_memory:
                pack["project_memory"] = build_memory_query_for_context_pack(root, change=args.change, target=args.target)
        except ValueError as error:
            print_json(error_response(str(error)), stderr=True)
            return 2
        print_json(pack)
        return 0

    if args.command == "knowledge" and args.knowledge_command is None:
        print_json(error_response("Use one of: inspect, check, init-repo, configure, doctor, install, update, promote-batch, query, index.", "MISSING_SUBCOMMAND"), stderr=True)
        return 2

    if args.command == "knowledge":
        root = resolve_project_root(Path.cwd())
        try:
            if args.knowledge_command == "inspect":
                result = build_knowledge_inspect(root)
            elif args.knowledge_command == "check":
                result = build_knowledge_check(root, team_path=args.team_path)
            elif args.knowledge_command == "init-repo":
                result = build_knowledge_init_repo(root, dest=args.dest, initial_pack=args.initial_pack, force=args.force)
            elif args.knowledge_command == "configure":
                include_project_candidates = None
                if args.include_project_candidates is not None:
                    include_project_candidates = args.include_project_candidates == "true"
                result = build_knowledge_configure(
                    root,
                    team_path=args.path,
                    enable_packs=args.enable_pack,
                    repo=args.repo,
                    ref=args.ref,
                    max_cards=args.max_cards,
                    include_project_candidates=include_project_candidates,
                )
            elif args.knowledge_command == "doctor":
                result = build_knowledge_doctor(root, team_path=args.team_path)
            elif args.knowledge_command == "install":
                result = build_knowledge_install(root, allow_dirty=args.allow_dirty)
            elif args.knowledge_command == "update":
                result = build_knowledge_update(root, allow_dirty=args.allow_dirty)
            elif args.knowledge_command == "promote-batch":
                result = build_knowledge_promote_batch(
                    root,
                    curation=args.curation,
                    team_path=args.team_path,
                    pack_id=args.pack,
                    category=args.category,
                    activate=args.activate,
                )
            elif args.knowledge_command == "query":
                result = build_knowledge_query(
                    root,
                    phase=args.phase,
                    surfaces=args.surface,
                    schema=args.schema,
                    stack=args.stack,
                    query=args.query,
                    from_change=args.from_change,
                    target=args.target,
                    max_cards=args.max_cards,
                    debug=args.debug,
                )
            elif args.knowledge_command == "index":
                result = build_knowledge_index(root, write_cache=True, team_path=args.team_path)
            else:
                print_json(error_response("Use one of: inspect, check, init-repo, configure, doctor, install, update, promote-batch, query, index.", "MISSING_SUBCOMMAND"), stderr=True)
                return 2
        except ValueError as error:
            print_json(error_response(str(error), "KNOWLEDGE_ERROR"), stderr=True)
            return 2
        print_json(result)
        return exit_code_for(result, fail_on_blocker=False)

    if args.command == "memory" and args.memory_command is None:
        print_json(error_response("Use one of: inspect, list, search, add, update-index.", "MISSING_SUBCOMMAND"), stderr=True)
        return 2

    if args.command == "memory":
        root = resolve_project_root(Path.cwd())
        try:
            if args.memory_command == "inspect":
                result = build_memory_inspect(root)
            elif args.memory_command == "list":
                result = build_memory_list(
                    root,
                    types=args.types,
                    status=args.status,
                    priority=args.priority,
                    include_body=args.include_body,
                )
            elif args.memory_command == "search":
                result = build_memory_search(
                    root,
                    query=args.query,
                    types=args.types,
                    limit=args.limit,
                    include_body=args.include_body,
                    include_stale=args.include_stale,
                    include_deprecated=args.include_deprecated,
                )
            elif args.memory_command == "add":
                result = build_memory_add(
                    root,
                    memory_type=args.memory_type,
                    title=args.title,
                    summary=args.summary,
                    body=args.body,
                    priority=args.priority,
                    source_refs=args.source_ref,
                )
            elif args.memory_command == "update-index":
                result = build_memory_update_index(root)
            else:
                print_json(error_response("Use one of: inspect, list, search, add, update-index.", "MISSING_SUBCOMMAND"), stderr=True)
                return 2
        except ValueError as error:
            print_json(error_response(str(error), "MEMORY_ERROR"), stderr=True)
            return 2
        print_json(result)
        return exit_code_for(result, fail_on_blocker=False)

    print_json(error_response("Use a supported Aisee command.", "MISSING_COMMAND"), stderr=True)
    return 2


def compact_knowledge_for_context_pack(knowledge: dict) -> dict:
    payload = knowledge.get("knowledge", {})
    meta = knowledge.get("meta", {})
    return {
        "status": knowledge.get("status"),
        "enabled": payload.get("enabled"),
        "source": payload.get("source"),
        "matches": payload.get("matches", []),
        "summary": knowledge.get("summary", {}),
        "issues": knowledge.get("issues", []),
        "meta": {
            "cache_is_fact_source": meta.get("cache_is_fact_source", False),
            "full_card_body_read": meta.get("full_card_body_read", False),
        },
    }


if __name__ == "__main__":
    raise SystemExit(main())
