#!/usr/bin/env python3
"""Unified Developer & Researcher CLI for Agentic Multimodal Research Platform (AI Research OS).

Provides convenient terminal commands to manage and run research pipelines, debates,
meta-analyses, reproducibility evaluations, demo seeding, and system health checks.

Usage:
  python scripts/research_cli.py --help
  python scripts/research_cli.py seed
  python scripts/research_cli.py health
  python scripts/research_cli.py run "Investigate room-temperature hydrides"
  python scripts/research_cli.py debate "Is KV cache pruning lossless?"
  python scripts/research_cli.py slr "Comparative efficacy of DPO vs PPO"
  python scripts/research_cli.py reproduce tests/fixtures/sample_script.py
"""

import argparse
import asyncio
import os
import sys
import json

# Setup Python paths
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(root_dir, "packages", "shared", "src"))
sys.path.insert(0, os.path.join(root_dir, "packages", "database", "src"))
sys.path.insert(0, os.path.join(root_dir, "packages", "ai", "src"))
sys.path.insert(0, os.path.join(root_dir, "packages", "tools", "src"))
sys.path.insert(0, os.path.join(root_dir, "packages", "ingestion", "src"))
sys.path.insert(0, os.path.join(root_dir, "packages", "retrieval", "src"))
sys.path.insert(0, os.path.join(root_dir, "packages", "research", "src"))
sys.path.insert(0, os.path.join(root_dir, "packages", "agents", "src"))
sys.path.insert(0, os.path.join(root_dir, "apps", "api", "src"))


def cmd_seed(args):
    """Seed the database with comprehensive 34-phase demo data."""
    from src.scripts.seed_demo_data import main as seed_main
    print("[CLI] Starting demo data hydration pipeline...")
    asyncio.run(seed_main())


def cmd_health(args):
    """Check the health status of local services, database, and models."""
    async def _check():
        print("==================================================")
        print("  AI RESEARCH OPERATING SYSTEM - HEALTH CHECK")
        print("==================================================")
        from shared.config import settings
        print(f"[*] Environment: {settings.environment}")
        print(f"[*] Database URL: {settings.database_url.split('@')[-1]}")

        # Test DB connection
        try:
            from database.connection import engine
            from sqlalchemy import text
            async with engine.connect() as conn:
                res = await conn.execute(text("SELECT 1"))
                print("[+] Database Connection: HEALTHY (PostgreSQL/SQLite responsive)")
        except Exception as e:
            print(f"[-] Database Connection: OFFLINE ({e})")

        # Test Model Gateway
        try:
            from ai.gateway import ModelGateway
            gateway = ModelGateway()
            providers = gateway.get_available_providers()
            print(f"[+] AI Model Gateway: READY (Providers: {', '.join(providers) if providers else 'Local Fallback'})")
        except Exception as e:
            print(f"[-] AI Model Gateway: ERROR ({e})")

        print("==================================================")

    asyncio.run(_check())


def cmd_run_research(args):
    """Trigger a deep multimodal research pipeline for a query."""
    async def _run():
        print(f"[CLI] Launching Deep Research Pipeline for query: '{args.query}'")
        from research.pipeline import ResearchPipeline
        pipeline = ResearchPipeline()
        job = await pipeline.create_job(
            query=args.query,
            config={"max_iterations": args.max_iterations, "depth": args.depth}
        )
        print(f"[+] Job Created: {job.id}")
        print("[*] Executing Task DAG Orchestration...")
        report = await pipeline.run_job(job.id)
        print("\n=================== RESEARCH REPORT ===================")
        print(f"Title: {report.title}")
        print(f"Executive Summary:\n{report.executive_summary}\n")
        print("Key Findings:")
        for f in (report.findings or []):
            print(f"  - {f}")
        print("=======================================================")

    asyncio.run(_run())


def cmd_debate(args):
    """Trigger an adversarial multi-agent debate session."""
    async def _debate():
        print(f"[CLI] Initiating Multi-Agent Debate on: '{args.topic}'")
        from research.debate.engine import DebateEngine
        engine = DebateEngine()
        debate = await engine.conduct_full_debate(
            topic=args.topic,
            rounds=args.rounds,
        )
        print("\n=================== DEBATE VERDICT ===================")
        print(f"Status: {debate.status}")
        print(f"Proposer (Elo: {debate.proposer_elo}): {debate.proposer_model}")
        print(f"Opposer (Elo: {debate.opposer_elo}): {debate.opposer_model}")
        if debate.consensus:
            print(f"\nConsensus Statement:\n{debate.consensus.consensus_statement}")
            print(f"\nAgreement Score: {debate.consensus.agreement_score}")
        print("======================================================")

    asyncio.run(_debate())


def cmd_slr(args):
    """Execute a systematic literature review and meta-analysis synthesis."""
    async def _slr():
        print(f"[CLI] Running PRISMA Meta-Analysis for: '{args.question}'")
        from research.literature.meta_analysis import SystematicLiteratureEngine
        engine = SystematicLiteratureEngine()
        result = await engine.run_meta_analysis(research_question=args.question)
        print("\n=================== META-ANALYSIS SUMMARY ===================")
        print(f"Synthesis Method: {result.get('model_type', 'random_effects')}")
        print(f"Pooled Effect Size: {result.get('pooled_effect_size')} (95% CI: [{result.get('ci_lower')}, {result.get('ci_upper')}])")
        print(f"Heterogeneity I^2: {result.get('i_squared')}%")
        print("=============================================================")

    asyncio.run(_slr())


def main():
    parser = argparse.ArgumentParser(description="Agentic Multimodal Research Platform CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Seed
    subparsers.add_parser("seed", help="Seed database with full 34-phase demo data")

    # Health
    subparsers.add_parser("health", help="Check database and model gateway health")

    # Run Research
    run_parser = subparsers.add_parser("run", help="Run deep multimodal research pipeline")
    run_parser.add_argument("query", type=str, help="Research question or topic")
    run_parser.add_argument("--depth", type=str, default="deep_research", help="Research depth profile")
    run_parser.add_argument("--max-iterations", type=int, default=3, help="Max DAG replanning iterations")

    # Debate
    debate_parser = subparsers.add_parser("debate", help="Run adversarial debate between model agents")
    debate_parser.add_argument("topic", type=str, help="Dialectical thesis or debate topic")
    debate_parser.add_argument("--rounds", type=int, default=3, help="Number of debate rounds")

    # SLR Meta-Analysis
    slr_parser = subparsers.add_parser("slr", help="Run systematic literature review and meta-analysis")
    slr_parser.add_argument("question", type=str, help="PICOS research question")

    args = parser.parse_args()

    if args.command == "seed":
        cmd_seed(args)
    elif args.command == "health":
        cmd_health(args)
    elif args.command == "run":
        cmd_run_research(args)
    elif args.command == "debate":
        cmd_debate(args)
    elif args.command == "slr":
        cmd_slr(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
