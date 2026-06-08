"""Aisee CLI scaffold."""

from __future__ import annotations

import argparse
from pathlib import Path

from aisee_cli import __version__
from aisee_cli.author_check import build_author_check
from aisee_cli.bootstrap import build_bootstrap_apply_response, build_bootstrap_plan
from aisee_cli.change import build_change_inspect
from aisee_cli.change_checks import build_archive_check, build_verify_check
from aisee_cli.contract import build_contract_get, build_contract_manifest, build_contract_summary
from aisee_cli.contract_server import lan_warning, serve_contract_context
from aisee_cli.context_pack import build_context_pack
from aisee_cli.doctor import build_doctor
from aisee_cli.flow import build_flow
from aisee_cli.id_registry import activate_id, check_registry, deprecate_id, next_id, reserve_ids
from aisee_cli.index import build_index
from aisee_cli.knowledge import (
    build_knowledge_check,
    build_knowledge_doctor,
    build_knowledge_index,
    build_knowledge_inspect,
    build_knowledge_install,
    build_knowledge_promote_batch,
    build_knowledge_query,
    build_knowledge_scaffold,
    build_knowledge_update,
)
from aisee_cli.lookup import get_id, trace_id
from aisee_cli.openspec_init import run_openspec_init
from aisee_cli.output import error_response, exit_code_for, print_json
from aisee_cli.plugin_assets import export_plugin_assets, inspect_plugin_assets, plugin_path
from aisee_cli.project import resolve_project_root
from aisee_cli.schema_pack import check_schema_packs, install_schema_packs, list_schema_packs
from aisee_cli.sources import add_source, check_sources, list_sources, remove_source


def main() -> int:
    parser = argparse.ArgumentParser(prog="aisee")
    parser.add_argument("--version", action="store_true", help="print version")
    subparsers = parser.add_subparsers(dest="command")
    doctor_parser = subparsers.add_parser("doctor")
    doctor_parser.add_argument("--json", action="store_true", help="output JSON")
    doctor_parser.add_argument("--fail-on-blocker", action="store_true", help="return non-zero when blockers exist")
    bootstrap_parser = subparsers.add_parser("bootstrap")
    bootstrap_group = bootstrap_parser.add_mutually_exclusive_group()
    bootstrap_group.add_argument("--plan", action="store_true", help="output bootstrap plan")
    bootstrap_group.add_argument("--apply", action="store_true", help="apply bootstrap plan")
    bootstrap_parser.add_argument("--json", action="store_true", help="output JSON")
    openspec_parser = subparsers.add_parser("openspec")
    openspec_parser.add_argument("--json", action="store_true", help="output JSON")
    openspec_subparsers = openspec_parser.add_subparsers(dest="openspec_command")
    openspec_ensure_parser = openspec_subparsers.add_parser("ensure")
    openspec_ensure_parser.add_argument("--profile", default="core", help="OpenSpec profile preset; default: core")
    openspec_ensure_parser.add_argument("--tools", default="none", help="OpenSpec AI tools value for init; default: none")
    openspec_ensure_parser.add_argument("--skip-profile", action="store_true", help="do not run openspec config profile")
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
    plugin_export_parser = plugin_subparsers.add_parser("export", description="deprecated: return a JSON blocker; plugin content is installed through Codex marketplace")
    plugin_export_parser.add_argument("--target", choices=["codex", "claude", "cursor"], required=True, help="agent runtime target")
    plugin_export_parser.add_argument("--dest", required=True, help="legacy destination argument; no files are written")
    plugin_export_parser.add_argument("--force", action="store_true", help="legacy compatibility flag; no files are overwritten")
    plugin_export_parser.add_argument("--json", action="store_true", help="output JSON")
    sources_parser = subparsers.add_parser("sources")
    sources_parser.add_argument("--json", action="store_true", help="output JSON")
    sources_subparsers = sources_parser.add_subparsers(dest="sources_command")
    sources_list_parser = sources_subparsers.add_parser("list")
    sources_list_parser.add_argument("--json", action="store_true", help="output JSON")
    sources_check_parser = sources_subparsers.add_parser("check")
    sources_check_parser.add_argument("--json", action="store_true", help="output JSON")
    sources_check_parser.add_argument("--fail-on-blocker", action="store_true", help="return non-zero when blockers exist")
    sources_add_parser = sources_subparsers.add_parser("add")
    sources_add_parser.add_argument("--scope", required=True, help="source scope")
    sources_add_parser.add_argument("--type", required=True, help="source type")
    sources_add_parser.add_argument("--path", required=True, help="source path")
    sources_add_parser.add_argument("--template", help="source template")
    sources_add_parser.add_argument("--parser", help="source parser")
    sources_add_parser.add_argument("--json", action="store_true", help="output JSON")
    sources_remove_parser = sources_subparsers.add_parser("remove")
    sources_remove_parser.add_argument("--scope", required=True, help="source scope")
    sources_remove_parser.add_argument("--type", required=True, help="source type")
    sources_remove_parser.add_argument("--path", required=True, help="source path")
    sources_remove_parser.add_argument("--json", action="store_true", help="output JSON")
    schemas_parser = subparsers.add_parser("schemas")
    schemas_parser.add_argument("--json", action="store_true", help="output JSON")
    schemas_subparsers = schemas_parser.add_subparsers(dest="schemas_command")
    schemas_list_parser = schemas_subparsers.add_parser("list")
    schemas_list_parser.add_argument("--json", action="store_true", help="output JSON")
    schemas_check_parser = schemas_subparsers.add_parser("check")
    schemas_check_parser.add_argument("--json", action="store_true", help="output JSON")
    schemas_check_parser.add_argument("--fail-on-blocker", action="store_true", help="return non-zero when blockers exist")
    schemas_install_parser = schemas_subparsers.add_parser("install", description="deprecated: return a JSON blocker; schema packs come from the marketplace plugin")
    schemas_install_parser.add_argument("--schema", action="append", default=[], help="legacy schema selection argument; no schema is installed")
    schemas_install_parser.add_argument("--all", action="store_true", help="legacy compatibility flag; no schemas are installed")
    schemas_install_parser.add_argument("--force", action="store_true", help="legacy compatibility flag; no schemas are overwritten")
    schemas_install_parser.add_argument("--json", action="store_true", help="output JSON")
    index_parser = subparsers.add_parser("index")
    index_parser.add_argument("--json", action="store_true", help="output JSON")
    index_parser.add_argument("--fail-on-blocker", action="store_true", help="return non-zero when blockers exist")
    change_parser = subparsers.add_parser("change")
    change_parser.add_argument("--json", action="store_true", help="output JSON")
    change_subparsers = change_parser.add_subparsers(dest="change_command")
    inspect_parser = change_subparsers.add_parser("inspect")
    inspect_parser.add_argument("change", help="OpenSpec change name")
    inspect_parser.add_argument("--json", action="store_true", help="output JSON")
    author_check_parser = change_subparsers.add_parser("author-check")
    author_check_parser.add_argument("change", help="OpenSpec change name")
    author_check_parser.add_argument("--json", action="store_true", help="output JSON")
    verify_check_parser = change_subparsers.add_parser("verify-check")
    verify_check_parser.add_argument("change", help="OpenSpec change name")
    verify_check_parser.add_argument("--json", action="store_true", help="output JSON")
    verify_check_parser.add_argument("--fail-on-blocker", action="store_true", help="return non-zero when blockers exist")
    archive_check_parser = change_subparsers.add_parser("archive-check")
    archive_check_parser.add_argument("change", help="OpenSpec change name")
    archive_check_parser.add_argument("--json", action="store_true", help="output JSON")
    archive_check_parser.add_argument("--fail-on-blocker", action="store_true", help="return non-zero when blockers exist")
    context_parser = subparsers.add_parser("context")
    context_parser.add_argument("--json", action="store_true", help="output JSON")
    context_subparsers = context_parser.add_subparsers(dest="context_command")
    pack_parser = context_subparsers.add_parser("pack")
    pack_parser.add_argument("--change", required=True, help="OpenSpec change name")
    pack_parser.add_argument("--for", dest="target", required=True, help="context target")
    pack_parser.add_argument("--knowledge", action="store_true", help="include knowledge guardrail matches")
    pack_parser.add_argument("--json", action="store_true", help="output JSON")
    knowledge_parser = subparsers.add_parser("knowledge")
    knowledge_parser.add_argument("--json", action="store_true", help="output JSON")
    knowledge_subparsers = knowledge_parser.add_subparsers(dest="knowledge_command")
    knowledge_inspect_parser = knowledge_subparsers.add_parser("inspect")
    knowledge_inspect_parser.add_argument("--json", action="store_true", help="output JSON")
    knowledge_check_parser = knowledge_subparsers.add_parser("check")
    knowledge_check_parser.add_argument("--team-path", help="team knowledge repository path")
    knowledge_check_parser.add_argument("--json", action="store_true", help="output JSON")
    knowledge_doctor_parser = knowledge_subparsers.add_parser("doctor")
    knowledge_doctor_parser.add_argument("--team-path", help="team knowledge repository path to compare with config")
    knowledge_doctor_parser.add_argument("--json", action="store_true", help="output JSON")
    knowledge_scaffold_parser = knowledge_subparsers.add_parser("scaffold", description="deprecated: return a JSON blocker; default templates are not copied from the PyPI CLI")
    knowledge_scaffold_parser.add_argument("--dest", required=True, help="legacy destination argument; no scaffold is written")
    knowledge_scaffold_parser.add_argument("--force", action="store_true", help="legacy compatibility flag; no directory is overwritten")
    knowledge_scaffold_parser.add_argument("--update-config", action="store_true", help="legacy compatibility flag; no config is written")
    knowledge_scaffold_parser.add_argument("--pack", action="append", default=[], help="legacy pack argument; can be repeated")
    knowledge_scaffold_parser.add_argument("--json", action="store_true", help="output JSON")
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
    contract_parser = subparsers.add_parser("contract")
    contract_parser.add_argument("--json", action="store_true", help="output JSON")
    contract_subparsers = contract_parser.add_subparsers(dest="contract_command")
    contract_manifest_parser = contract_subparsers.add_parser("manifest")
    contract_manifest_parser.add_argument("--max-chars", type=int, default=800, help="maximum summary characters per contract")
    contract_manifest_parser.add_argument("--json", action="store_true", help="output JSON")
    contract_summary_parser = contract_subparsers.add_parser("summary")
    contract_summary_parser.add_argument("--change", required=True, help="OpenSpec change name")
    contract_summary_parser.add_argument("--max-chars", type=int, default=800, help="maximum summary characters per contract")
    contract_summary_parser.add_argument("--json", action="store_true", help="output JSON")
    contract_get_parser = contract_subparsers.add_parser("get")
    contract_get_parser.add_argument("--change", required=True, help="OpenSpec change name")
    contract_get_parser.add_argument("--artifact", required=True, help="contract artifact id or path")
    contract_get_parser.add_argument("--section", help="contract section id or title")
    contract_get_parser.add_argument("--max-chars", type=int, default=4000, help="maximum content characters")
    contract_get_parser.add_argument("--raw", action="store_true", help="return raw artifact content when no section is selected")
    contract_get_parser.add_argument("--json", action="store_true", help="output JSON")
    contract_serve_parser = contract_subparsers.add_parser("serve")
    contract_serve_parser.add_argument("--host", default="127.0.0.1", help="host to bind; default: 127.0.0.1")
    contract_serve_parser.add_argument("--port", type=int, default=8765, help="port to bind; default: 8765")
    contract_serve_parser.add_argument("--json", action="store_true", help="output JSON startup metadata")
    id_parser = subparsers.add_parser("id")
    id_parser.add_argument("--json", action="store_true", help="output JSON")
    id_subparsers = id_parser.add_subparsers(dest="id_command")
    id_check_parser = id_subparsers.add_parser("check")
    id_check_parser.add_argument("--json", action="store_true", help="output JSON")
    id_check_parser.add_argument("--fail-on-blocker", action="store_true", help="return non-zero when blockers exist")
    id_next_parser = id_subparsers.add_parser("next")
    id_next_parser.add_argument("--scope", required=True, help="ID scope")
    id_next_parser.add_argument("--type", required=True, help="ID type")
    id_next_parser.add_argument("--json", action="store_true", help="output JSON")
    id_reserve_parser = id_subparsers.add_parser("reserve")
    id_reserve_parser.add_argument("--scope", required=True, help="ID scope")
    id_reserve_parser.add_argument("--type", required=True, help="ID type")
    id_reserve_parser.add_argument("--count", type=int, default=1, help="number of IDs to reserve")
    id_reserve_parser.add_argument("--json", action="store_true", help="output JSON")
    id_activate_parser = id_subparsers.add_parser("activate")
    id_activate_parser.add_argument("id", help="full ID, for example auth:FR-001")
    id_activate_parser.add_argument("--owner", required=True, help="owner document path")
    id_activate_parser.add_argument("--title", required=True, help="ID title")
    id_activate_parser.add_argument("--json", action="store_true", help="output JSON")
    id_deprecate_parser = id_subparsers.add_parser("deprecate")
    id_deprecate_parser.add_argument("id", help="full ID, for example auth:FR-001")
    id_deprecate_parser.add_argument("--replaced-by", action="append", default=[], help="replacement full ID")
    id_deprecate_parser.add_argument("--reason", required=True, help="deprecation reason")
    id_deprecate_parser.add_argument("--json", action="store_true", help="output JSON")
    flow_parser = subparsers.add_parser("flow")
    flow_parser.add_argument("--json", action="store_true", help="output JSON")
    flow_subparsers = flow_parser.add_subparsers(dest="flow_command")
    flow_inspect_parser = flow_subparsers.add_parser("inspect")
    flow_inspect_parser.add_argument("--change", help="OpenSpec change name")
    flow_inspect_parser.add_argument("--json", action="store_true", help="output JSON")
    flow_next_parser = flow_subparsers.add_parser("next")
    flow_next_parser.add_argument("--change", help="OpenSpec change name")
    flow_next_parser.add_argument("--json", action="store_true", help="output JSON")
    gaps_parser = subparsers.add_parser("gaps")
    gaps_parser.add_argument("--change", required=True, help="OpenSpec change name")
    gaps_parser.add_argument("--json", action="store_true", help="output JSON")
    trace_parser = subparsers.add_parser("trace")
    trace_parser.add_argument("id", help="full ID to trace")
    trace_parser.add_argument("--json", action="store_true", help="output JSON")
    get_parser = subparsers.add_parser("get")
    get_parser.add_argument("id", help="full ID to get")
    get_parser.add_argument("--json", action="store_true", help="output JSON")
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
        result = build_bootstrap_apply_response() if args.apply else build_bootstrap_plan(root)
        print_json(result)
        return exit_code_for(result, fail_on_blocker=args.apply)

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
            if args.plugin_command == "export":
                result = export_plugin_assets(root, args.target, Path(args.dest), force=args.force)
                print_json(result)
                return 0
        except ValueError as error:
            print_json(error_response(str(error)), stderr=True)
            return 2
        print_json(error_response("Use one of: inspect, path, export.", "MISSING_SUBCOMMAND"), stderr=True)
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
        except ValueError as error:
            print_json(error_response(str(error)), stderr=True)
            return 2
        print_json(pack)
        return 0

    if args.command == "knowledge" and args.knowledge_command is None:
        print_json(error_response("Use one of: inspect, check, doctor, scaffold, install, update, promote-batch, query, index.", "MISSING_SUBCOMMAND"), stderr=True)
        return 2

    if args.command == "knowledge":
        root = resolve_project_root(Path.cwd())
        try:
            if args.knowledge_command == "inspect":
                result = build_knowledge_inspect(root)
            elif args.knowledge_command == "check":
                result = build_knowledge_check(root, team_path=args.team_path)
            elif args.knowledge_command == "doctor":
                result = build_knowledge_doctor(root, team_path=args.team_path)
            elif args.knowledge_command == "scaffold":
                result = build_knowledge_scaffold(root, args.dest, force=args.force, update_config=args.update_config, packs=args.pack)
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
                print_json(error_response("Use one of: inspect, check, doctor, scaffold, install, update, promote-batch, query, index.", "MISSING_SUBCOMMAND"), stderr=True)
                return 2
        except ValueError as error:
            print_json(error_response(str(error), "KNOWLEDGE_ERROR"), stderr=True)
            return 2
        print_json(result)
        return exit_code_for(result, fail_on_blocker=False)

    if args.command == "contract" and args.contract_command is None:
        print_json(error_response("Use one of: manifest, summary, get, serve.", "MISSING_SUBCOMMAND"), stderr=True)
        return 2

    if args.command == "contract":
        try:
            root = resolve_project_root(Path.cwd())
            if args.contract_command == "manifest":
                result = build_contract_manifest(root, max_chars=args.max_chars)
            elif args.contract_command == "summary":
                result = build_contract_summary(root, args.change, max_chars=args.max_chars)
            elif args.contract_command == "get":
                result = build_contract_get(
                    root,
                    args.change,
                    args.artifact,
                    section=args.section,
                    max_chars=args.max_chars,
                    raw=args.raw,
                )
            elif args.contract_command == "serve":
                if not args.host:
                    print_json(error_response("contract serve host must not be empty", "CONTRACT_CONTEXT_ERROR"), stderr=True)
                    return 2
                startup = {
                    "schema_version": "1.0",
                    "status": "serving",
                    "host": args.host,
                    "port": args.port,
                    "warning": lan_warning(args.host),
                }
                print_json(startup, stderr=True)
                serve_contract_context(root, host=args.host, port=args.port)
                return 0
            else:
                print_json(error_response("Use one of: manifest, summary, get, serve.", "MISSING_SUBCOMMAND"), stderr=True)
                return 2
        except ValueError as error:
            print_json(error_response(str(error), "CONTRACT_CONTEXT_ERROR"), stderr=True)
            return 2
        print_json(result)
        return 0

    if args.command == "gaps":
        root = resolve_project_root(Path.cwd())
        pack = build_context_pack(root, args.change, "aisee-verify")
        result = {
            "schema_version": pack["schema_version"],
            "change": pack["change"],
            "result": summarize_gaps(pack["gaps"]),
            "gaps": pack["gaps"],
            "guardrails": pack["guardrails"],
            "meta": {
                "command": f"aisee gaps --change {args.change} --json",
                "source_context_target": "aisee-verify",
            },
        }
        print_json(result)
        return 0

    if args.command == "change" and args.change_command is None:
        print_json(error_response("Use one of: inspect, author-check, verify-check, archive-check.", "MISSING_SUBCOMMAND"), stderr=True)
        return 2

    if args.command == "change" and args.change_command == "inspect":
        root = resolve_project_root(Path.cwd())
        result = build_change_inspect(root, args.change)
        print_json(result)
        return 0

    if args.command == "change" and args.change_command == "author-check":
        root = resolve_project_root(Path.cwd())
        result = build_author_check(root, args.change)
        print_json(result)
        return 0

    if args.command == "change" and args.change_command == "verify-check":
        root = resolve_project_root(Path.cwd())
        result = build_verify_check(root, args.change)
        print_json(result)
        return exit_code_for(result, fail_on_blocker=args.fail_on_blocker)

    if args.command == "change" and args.change_command == "archive-check":
        root = resolve_project_root(Path.cwd())
        result = build_archive_check(root, args.change)
        print_json(result)
        return exit_code_for(result, fail_on_blocker=args.fail_on_blocker)

    if args.command == "sources":
        root = resolve_project_root(Path.cwd())
        try:
            if args.sources_command in {None, "list"}:
                result = list_sources(root)
                print_json(result)
                return 0
            if args.sources_command == "check":
                result = check_sources(root)
                print_json(result)
                return exit_code_for(result, fail_on_blocker=args.fail_on_blocker)
            if args.sources_command == "add":
                result = add_source(root, args.scope, args.type, args.path, args.template, args.parser)
                print_json(result)
                return 0
            if args.sources_command == "remove":
                result = remove_source(root, args.scope, args.type, args.path)
                print_json(result)
                return 0
        except ValueError as error:
            print_json(error_response(str(error)), stderr=True)
            return 2
        print_json(error_response("Use one of: list, check, add, remove.", "MISSING_SUBCOMMAND"), stderr=True)
        return 2

    if args.command == "schemas":
        root = resolve_project_root(Path.cwd())
        try:
            if args.schemas_command in {None, "list"}:
                result = list_schema_packs(root)
                print_json(result)
                return 0
            if args.schemas_command == "check":
                result = check_schema_packs(root)
                print_json(result)
                return exit_code_for(result, fail_on_blocker=args.fail_on_blocker)
            if args.schemas_command == "install":
                selected = ["*"] if args.all else args.schema
                result = install_schema_packs(root, selected, force=args.force)
                print_json(result)
                return 0
        except ValueError as error:
            print_json(error_response(str(error)), stderr=True)
            return 2
        print_json(error_response("Use one of: list, check, install.", "MISSING_SUBCOMMAND"), stderr=True)
        return 2

    if args.command == "index":
        root = resolve_project_root(Path.cwd())
        result = build_index(root, write_cache=True)
        print_json(result)
        return exit_code_for(result, fail_on_blocker=args.fail_on_blocker)

    if args.command == "id":
        root = resolve_project_root(Path.cwd())
        try:
            if args.id_command == "check":
                result = check_registry(root)
            elif args.id_command == "next":
                result = next_id(root, args.scope, args.type)
            elif args.id_command == "reserve":
                result = reserve_ids(root, args.scope, args.type, args.count)
            elif args.id_command == "activate":
                result = activate_id(root, args.id, args.owner, args.title)
            elif args.id_command == "deprecate":
                result = deprecate_id(root, args.id, args.replaced_by, args.reason)
            else:
                print_json(error_response("Use one of: check, next, reserve, activate, deprecate.", "MISSING_SUBCOMMAND"), stderr=True)
                return 2
        except ValueError as error:
            print_json(error_response(str(error)), stderr=True)
            return 2
        print_json(result)
        fail_on_blocker = bool(getattr(args, "fail_on_blocker", False))
        return exit_code_for(result, fail_on_blocker=fail_on_blocker)

    if args.command == "trace":
        root = resolve_project_root(Path.cwd())
        try:
            result = trace_id(root, args.id)
        except ValueError as error:
            print_json(error_response(str(error)), stderr=True)
            return 2
        print_json(result)
        return 0

    if args.command == "get":
        root = resolve_project_root(Path.cwd())
        try:
            result = get_id(root, args.id)
        except ValueError as error:
            print_json(error_response(str(error)), stderr=True)
            return 2
        print_json(result)
        return 0

    if args.command == "flow":
        root = resolve_project_root(Path.cwd())
        if args.flow_command is None:
            print_json(error_response("Use one of: inspect, next.", "MISSING_SUBCOMMAND"), stderr=True)
            return 2
        result = build_flow(root, change=getattr(args, "change", None), command=args.flow_command)
        print_json(result)
        return 0

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


def summarize_gaps(gaps: list[dict[str, object]]) -> dict[str, int | str]:
    blocker = sum(1 for gap in gaps if gap.get("severity") == "blocker")
    risk = sum(1 for gap in gaps if gap.get("severity") == "risk")
    info = sum(1 for gap in gaps if gap.get("severity") == "info")
    status = "blocked" if blocker else ("risk" if risk else "clear")
    return {
        "status": status,
        "blocker": blocker,
        "risk": risk,
        "info": info,
        "total": len(gaps),
    }


if __name__ == "__main__":
    raise SystemExit(main())
