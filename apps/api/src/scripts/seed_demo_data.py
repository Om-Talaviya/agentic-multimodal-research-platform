"""Comprehensive Demo Seed Script for Agentic Multimodal Research Platform (AI Research OS).

Hydrates the database with realistic, high-fidelity research data across all 34 phases:
- Admin and Researcher users
- User Quotas & Tier limits
- Workspaces and Projects
- Research Jobs, Tasks, Sources, Evidence, Reports
- Adversarial Multi-Agent Debate with Elo ratings & Dialectical consensus
- Systematic Literature Review (SLR), Risk of Bias, and PRISMA Meta-Analysis
- In-Silico Computational Reproducibility with Sandboxed Execution Traces
- Multimodal 16:9 Presentation Slides & 2-Speaker Executive Podcast Script
- Blinded Academic Peer Review Manuscript with Referee Scorecards
- Collaborative 2D Visual Research Canvas with Directed Graph Nodes & Edges
- Synthetic Instruction Dataset with Alpaca/ShareGPT/DPO preference pairs
- Autonomous Patent Landscape Corpus with Prior Art Evals & Freedom-to-Operate Report
- Long-Term Knowledge Graph Entities, Relations & Persistent Research Memory
- Infrastructure Worker Nodes & System Telemetry
"""

import asyncio
import os
import sys
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List

# Ensure python path resolution
current_dir = os.path.dirname(os.path.abspath(__file__))
api_dir = os.path.dirname(current_dir)
apps_dir = os.path.dirname(api_dir)
root_dir = os.path.dirname(apps_dir)
sys.path.insert(0, os.path.join(root_dir, "packages", "database", "src"))
sys.path.insert(0, os.path.join(root_dir, "packages", "shared", "src"))
sys.path.insert(0, os.path.join(root_dir, "packages", "research", "src"))
sys.path.insert(0, os.path.join(root_dir, "packages", "retrieval", "src"))
sys.path.insert(0, os.path.join(root_dir, "packages", "ai", "src"))
sys.path.insert(0, api_dir)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import async_session_maker, engine, Base
from database.models import (
    User,
    UserQuota,
    DBWorkspace,
    DBWorkspaceMember,
    DBProject,
    ResearchJob,
    ResearchTask,
    Source,
    Evidence,
    Report,
    DBAgentDebate,
    DBDebateRound,
    DBDebateConsensus,
    DBLiteratureReview,
    DBSLRCriterion,
    DBSLRStudyCandidate,
    DBRiskOfBiasAssessment,
    DBMetaAnalysisReport,
    DBExperimentProtocol,
    DBReproducibilityRun,
    DBClaimVerificationTrace,
    DBSynthesisPresentation,
    DBPresentationSlide,
    DBPodcastBriefing,
    DBPeerReviewManuscript,
    DBPeerReviewReport,
    DBCanvasBoard,
    DBCanvasNode,
    DBCanvasEdge,
    DBSyntheticDataset,
    DBInstructionSample,
    DBPatentCorpus,
    DBPatentDocument,
    DBPatentClaim,
    DBPriorArtEvaluation,
    DBFreedomToOperateReport,
    DBKnowledgeEntity,
    DBKnowledgeRelation,
    DBResearchMemory,
    DBWorkerNode,
)
from shared.auth import hash_password
from shared.logging import get_logger

logger = get_logger(__name__)


async def seed_all_demo_data(session: AsyncSession) -> Dict[str, Any]:
    """Populates the database with rich out-of-the-box demo data across all platform modules."""
    logger.info("Starting demo data seeding pipeline...")

    # 1. Seed Users
    admin_user_stmt = select(User).where(User.username == "admin")
    admin_res = await session.execute(admin_user_stmt)
    admin_user = admin_res.scalar_one_or_none()

    if not admin_user:
        admin_user = User(
            id=uuid.uuid4(),
            username="admin",
            email="admin@research-os.ai",
            password_hash=hash_password("Password123!"),
            role="admin",
            is_active=True,
        )
        session.add(admin_user)
        await session.flush()
        logger.info("Created Admin user", username="admin")

    researcher_stmt = select(User).where(User.username == "elena")
    researcher_res = await session.execute(researcher_stmt)
    researcher_user = researcher_res.scalar_one_or_none()

    if not researcher_user:
        researcher_user = User(
            id=uuid.uuid4(),
            username="elena",
            email="elena.rostova@deepmind.org",
            password_hash=hash_password("Password123!"),
            role="researcher",
            is_active=True,
        )
        session.add(researcher_user)
        await session.flush()
        logger.info("Created Researcher user", username="elena")

    # 2. Seed User Quotas
    quota_stmt = select(UserQuota).where(UserQuota.user_id == admin_user.id)
    quota_res = await session.execute(quota_stmt)
    if not quota_res.scalar_one_or_none():
        admin_quota = UserQuota(
            id=uuid.uuid4(),
            user_id=admin_user.id,
            daily_token_limit=10000000,
            daily_cost_limit=500.0,
            tokens_used_today=125400,
            cost_used_today=14.25,
            max_concurrent_jobs=10,
        )
        session.add(admin_quota)

    # 3. Seed Workspaces & Projects
    ws_stmt = select(DBWorkspace).where(DBWorkspace.slug == "frontier-ai-lab")
    ws_res = await session.execute(ws_stmt)
    workspace = ws_res.scalar_one_or_none()

    if not workspace:
        workspace = DBWorkspace(
            id=uuid.uuid4(),
            name="Frontier AI & Quantum Materials Lab",
            slug="frontier-ai-lab",
            description="Accelerating autonomous material discovery and multi-agent scientific reasoning.",
            owner_id=admin_user.id,
            settings_json={"default_model": "gemini-1.5-pro", "auto_debate": True, "strict_eval": True},
        )
        session.add(workspace)
        await session.flush()

        member1 = DBWorkspaceMember(
            id=uuid.uuid4(),
            workspace_id=workspace.id,
            user_id=admin_user.id,
            role="owner",
        )
        member2 = DBWorkspaceMember(
            id=uuid.uuid4(),
            workspace_id=workspace.id,
            user_id=researcher_user.id,
            role="collaborator",
        )
        session.add_all([member1, member2])

    proj_stmt = select(DBProject).where(DBProject.slug == "superconductor-discovery")
    proj_res = await session.execute(proj_stmt)
    project = proj_res.scalar_one_or_none()

    if not project:
        project = DBProject(
            id=uuid.uuid4(),
            workspace_id=workspace.id,
            name="Autonomous LLM-Guided Superconductor Discovery",
            slug="superconductor-discovery",
            description="High-throughput Density Functional Theory (DFT) and active-learning search for room-temperature hydrides.",
            created_by=admin_user.id,
        )
        session.add(project)
        await session.flush()

    # 4. Seed Research Job, Tasks, Source, Evidence & Report
    job_stmt = select(ResearchJob).where(ResearchJob.question.like("%Room-Temperature%"))
    job_res = await session.execute(job_stmt)
    job = job_res.scalar_one_or_none()

    if not job:
        job = ResearchJob(
            id=uuid.uuid4(),
            request_id=uuid.uuid4(),
            user_id=admin_user.id,
            workspace_id=workspace.id,
            project_id=project.id,
            question="Investigating Room-Temperature Ambient-Pressure Hydride Superconductors via High-Throughput DFT",
            objective="Analyze electronic band structure, Eliashberg spectral function, and thermodynamic stability of pressurized clathrate hydrides.",
            domain="Condensed Matter Physics & Computational Materials",
            scope="High-pressure hydrides, ternary alloys, DFT simulations",
            status="completed",
        )
        session.add(job)
        await session.flush()

        src1 = Source(
            id=uuid.uuid4(),
            job_id=job.id,
            type="academic_paper",
            url="https://doi.org/10.1038/s41586-019-1201-8",
            title="Superconductivity at 250 K in lanthanum hydride under high pressure",
            source_metadata={"authors": ["Drozdov et al."], "year": 2019, "journal": "Nature"},
            content_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        )
        session.add(src1)
        await session.flush()

        task1 = ResearchTask(
            id=uuid.uuid4(),
            job_id=job.id,
            type="document_analysis",
            objective="Extract Eliashberg spectral function a2F(w) and Coulomb pseudopotential mu*.",
            agent="doc",
            status="completed",
            priority=1,
            result={"status": "success", "findings": "Extracted Eliashberg spectral function with lambda = 2.45 and mu* = 0.11."},
        )
        task2 = ResearchTask(
            id=uuid.uuid4(),
            job_id=job.id,
            type="web_search",
            objective="Cross-reference Materials Project and OQMD phase diagrams under 0-250 GPa.",
            agent="web",
            status="completed",
            priority=2,
            result={"status": "success", "findings": "Identified metastable cubic Fm-3m ternary phase stable above 165 GPa."},
        )
        session.add_all([task1, task2])

        ev1 = Evidence(
            id=uuid.uuid4(),
            job_id=job.id,
            source_id=src1.id,
            claim="Ternary $La_{0.5}Y_{0.5}H_{10}$ exhibits theoretical superconductivity transition temperature of $T_c = 264\\text{ K}$ at 175 GPa.",
            supporting_text="Calculated phonon dispersion relations confirm dynamical stability above 160 GPa with strongly enhanced electron-phonon coupling constant $\\lambda = 2.68$.",
            confidence=0.96,
            source_reliability=1.0,
            verification_status="verified",
            citation_coordinates={"page": 4, "paragraph": 2, "bbox": [100, 240, 500, 310]},
        )
        session.add(ev1)
        await session.flush()

        report = Report(
            id=uuid.uuid4(),
            job_id=job.id,
            title="Comprehensive Analysis: Ambient & High-Pressure Hydride Superconductivity Mechanisms",
            executive_summary="Through autonomous literature retrieval and DFT thermodynamic validation, this study evaluates the feasibility of achieving high-$T_c$ superconductivity in pressurized hydrides. Key finding: ternary clathrate hydrides overcome the binary stability threshold.",
            methodology="Hierarchical DAG planning with hybrid Reciprocal Rank Fusion retrieval across arXiv and Materials Project DFT band structures.",
            findings=[
                "Clathrate-like hydrogen cages ($H_{24}, H_{32}$) facilitate high electronic density of states at the Fermi level $N(E_F)$.",
                "Dynamical phonon stabilization can be achieved at lower pressures ($<120\\text{ GPa}$) via light-element interstitial doping ($B, C, N$).",
                "Zero electrical resistance was confirmed in reproduced diamond anvil cell (DAC) in-situ 4-probe transports.",
            ],
            evidence_ids=[str(ev1.id)],
            source_ids=[str(src1.id)],
            contradictions=[],
            confidence_score=0.94,
            conclusions=[
                "Laser-heated Diamond Anvil Cell (LH-DAC) experiments should target the 160-180 GPa regime with pulsed synchrotron X-ray diffraction.",
                "Binary hydrides require unphysically high stabilization pressures, but ternary alloy systems show promising metastability.",
            ],
            limitations=[
                "High-pressure experimental synthesis suffers from hydrogen diffusion into diamond anvil culets.",
            ],
        )
        session.add(report)

    # 5. Seed Adversarial Multi-Agent Debate
    debate_stmt = select(DBAgentDebate).where(DBAgentDebate.topic.like("%KV Cache%"))
    debate_res = await session.execute(debate_stmt)
    debate = debate_res.scalar_one_or_none()

    if not debate:
        debate = DBAgentDebate(
            id=uuid.uuid4(),
            user_id=admin_user.id,
            workspace_id=workspace.id,
            project_id=project.id,
            topic="Is Transformer KV Cache Compression via Speculative Streaming Pruning Lossless for Long-Context Mathematical Reasoning?",
            initial_thesis="Dynamic KV cache pruning with attention-budget re-allocation preserves 99.8% of GSM8K precision while slashing VRAM footprints by 4.2x.",
            counter_thesis="Token-eviction heuristics suffer severe retrieval degradation in multi-step transitive reasoning chains where late steps recall obscure context tokens.",
            status="concluded",
            max_rounds=3,
            current_round=3,
            proposer_model="claude-3-5-sonnet",
            opposer_model="gpt-4o",
            arbiter_model="gemini-1.5-pro",
            proposer_elo=1662.5,
            opposer_elo=1638.0,
            config_json={"arbiter_mode": "strict_formal_verification"},
        )
        session.add(debate)
        await session.flush()

        r1 = DBDebateRound(
            id=uuid.uuid4(),
            debate_id=debate.id,
            round_number=1,
            proposer_argument="StreamingLLM and H2O demonstrate that over 95% of attention mass concentrates on initial sink tokens and recent sliding windows. By preserving top-k Heavy Hitters, mathematical proofs maintain step coherence.",
            proposer_score=8.4,
            opposer_argument="The proposer assumes uniform attention distribution across reasoning tasks, ignoring 'needle-in-a-haystack' dependency lemmas in Putnam-style proofs.",
            opposer_score=8.8,
            arbiter_critique="Proposer established baseline efficiency; opposer correctly identified sensitivity to non-monotonic logic dependencies.",
            round_winner="opposer",
            elo_delta=4.2,
        )
        r2 = DBDebateRound(
            id=uuid.uuid4(),
            debate_id=debate.id,
            round_number=2,
            proposer_argument="We introduce Dynamic Lemma-Anchoring: tagging equation labels as persistent memory tokens prevents drift across 128k context windows.",
            proposer_score=9.3,
            opposer_argument="Tagging overhead introduces latency penalties; however, the reasoning fidelity is verifiably preserved.",
            opposer_score=8.7,
            arbiter_critique="Proposer mitigated the primary vulnerability with Lemma-Anchoring.",
            round_winner="proposer",
            elo_delta=6.8,
        )
        session.add_all([r1, r2])

        consensus = DBDebateConsensus(
            id=uuid.uuid4(),
            debate_id=debate.id,
            consensus_statement="Selective KV cache compression is statistically indistinguishable from full-attention baselines when at least 64 sink tokens and dynamically tagged lemma definition spans are strictly pinned.",
            accepted_claims=["Lemma-Anchored KV caching achieves 3.8x compression with <0.2% accuracy drop."],
            refuted_claims=["Naive sliding window eviction is sufficient for multi-step theorem proving."],
            concessions=["Dynamic tagging incurs a 4.5% VRAM indexing overhead."],
        )
        session.add(consensus)

    # 6. Seed Systematic Literature Review & Meta-Analysis (Phase 28)
    slr_stmt = select(DBLiteratureReview).where(DBLiteratureReview.title.like("%Direct Preference Optimization%"))
    slr_res = await session.execute(slr_stmt)
    slr = slr_res.scalar_one_or_none()

    if not slr:
        slr = DBLiteratureReview(
            id=uuid.uuid4(),
            user_id=admin_user.id,
            workspace_id=workspace.id,
            project_id=project.id,
            title="Comparative Efficacy of Direct Preference Optimization (DPO) vs. PPO/RLHF in Complex Scientific Reasoning",
            research_question="Does closed-form DPO optimization achieve superior mathematical problem-solving accuracy compared to online actor-critic PPO across LLMs?",
            protocol_type="PRISMA-2020",
            current_phase="completed",
            pico_framework={
                "population": "Frontier LLMs (7B - 70B parameters)",
                "intervention": "Direct Preference Optimization (DPO)",
                "comparator": "Proximal Policy Optimization (PPO / RLHF)",
                "outcome": "Mathematical benchmark accuracy (GSM8K, MATH, HumanEval)",
            },
            search_strategy={"databases": ["arXiv", "Semantic Scholar", "PubMed"], "keywords": ["DPO", "PPO", "RLHF", "mathematical reasoning"]},
            total_identified=1420,
            total_screened=1110,
            total_eligible=220,
            total_included=24,
            total_excluded=1396,
        )
        session.add(slr)
        await session.flush()

        crit1 = DBSLRCriterion(
            id=uuid.uuid4(),
            review_id=slr.id,
            criterion_type="inclusion",
            category="methodology",
            description="Empirical comparison between DPO and PPO on standardized scientific reasoning benchmarks.",
            order_index=1,
        )
        session.add(crit1)

        c1 = DBSLRStudyCandidate(
            id=uuid.uuid4(),
            review_id=slr.id,
            title="Direct Preference Optimization: Your Language Model is Secretly a Reward Model",
            authors=["Rafailov, R.", "Sharma, A.", "Mitchell, E."],
            publication_year=2023,
            venue="NeurIPS 2023",
            doi="10.48550/arXiv.2305.18290",
            abstract="We introduce DPO, an algorithm that implicitizes the reward function to eliminate RL instability.",
            screening_status="included",
            relevance_score=0.98,
            methodology_type="Benchmark",
            sample_size=10000,
            effect_size=0.44,
            variance=0.03,
            metric_name="cohens_d",
        )
        session.add(c1)
        await session.flush()

        rob1 = DBRiskOfBiasAssessment(
            id=uuid.uuid4(),
            candidate_id=c1.id,
            selection_bias="low_risk",
            confounding_bias="low_risk",
            measurement_bias="low_risk",
            reporting_bias="low_risk",
            overall_risk="low_risk",
            justification_notes="Rigorous open-source benchmark with public seed reproducibility.",
        )
        session.add(rob1)

        meta_rep = DBMetaAnalysisReport(
            id=uuid.uuid4(),
            review_id=slr.id,
            synthesis_name="DPO vs PPO Reasoning Effect Size Synthesis",
            effect_metric="cohens_d",
            model_type="random_effects",
            total_studies_analyzed=24,
            pooled_effect_size=0.425,
            pooled_ci_lower=0.284,
            pooled_ci_upper=0.566,
            pooled_p_value=0.0001,
            z_score=5.88,
            q_statistic=34.9,
            degrees_of_freedom=23,
            i_squared=34.2,
            tau_squared=0.012,
        )
        session.add(meta_rep)

    # 7. Seed In-Silico Reproducibility Run (Phase 29)
    proto_stmt = select(DBExperimentProtocol).where(DBExperimentProtocol.name.like("%Mixture-of-Experts%"))
    proto_res = await session.execute(proto_stmt)
    proto = proto_res.scalar_one_or_none()

    if not proto:
        proto = DBExperimentProtocol(
            id=uuid.uuid4(),
            user_id=admin_user.id,
            workspace_id=workspace.id,
            project_id=project.id,
            name="Verification of Sparse Mixture-of-Experts Dynamic Routing Entropy in Multi-GPU Kernels",
            description="Re-executes the gating entropy evaluation script inside the sandboxed Python AST runtime.",
            source_paper_title="Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer",
            runtime_language="python3",
            executable_code="""import numpy as np
def compute_entropy(logits):
    probs = np.exp(logits) / np.sum(np.exp(logits), axis=-1, keepdims=True)
    entropy = -np.sum(probs * np.log(probs + 1e-9), axis=-1)
    return float(np.mean(entropy))

np.random.seed(42)
test_logits = np.random.randn(1024, 8)
result_entropy = compute_entropy(test_logits)
print(f'Routing Entropy: {result_entropy:.4f}')
""",
            claimed_metrics={"entropy": 2.875},
            verification_status="fully_reproduced",
        )
        session.add(proto)
        await session.flush()

        repro_run = DBReproducibilityRun(
            id=uuid.uuid4(),
            protocol_id=proto.id,
            executed_by=admin_user.id,
            status="succeeded",
            execution_time_ms=14.2,
            memory_peak_mb=128.5,
            reproduced_metrics={"entropy": 2.8748},
            runtime_logs="Routing Entropy: 2.8748\nProcess exited successfully.",
            reproducibility_score=0.9999,
        )
        session.add(repro_run)
        await session.flush()

        trace = DBClaimVerificationTrace(
            id=uuid.uuid4(),
            protocol_id=proto.id,
            run_id=repro_run.id,
            claim_statement="Top-2 Gating entropy remains above 2.85 nats under load balancing.",
            metric_name="entropy",
            claimed_value=2.875,
            reproduced_value=2.8748,
            delta_relative_error=0.00007,
            tolerance_threshold=0.05,
            verdict="reproduced",
            analysis_notes="Variance is well within the 5% tolerance threshold.",
        )
        session.add(trace)

    # 8. Seed Presentation Studio & Executive Podcast (Phase 30)
    pres_stmt = select(DBSynthesisPresentation).where(DBSynthesisPresentation.title.like("%Autonomous Multi-Agent%"))
    pres_res = await session.execute(pres_stmt)
    pres = pres_res.scalar_one_or_none()

    if not pres:
        pres = DBSynthesisPresentation(
            id=uuid.uuid4(),
            user_id=admin_user.id,
            workspace_id=workspace.id,
            project_id=project.id,
            title="Next-Generation Autonomous Multi-Agent Research Architectures",
            subtitle="Scaling Scientific Reasoning with Dynamic Verification DAGs & In-Silico Reproduction",
            target_audience="executive",
            theme="midnight_slate",
            estimated_duration_min=12,
            total_slides=2,
        )
        session.add(pres)
        await session.flush()

        s1 = DBPresentationSlide(
            id=uuid.uuid4(),
            presentation_id=pres.id,
            slide_number=1,
            layout_type="title",
            headline="AI Research OS: Autonomous Scientific Discovery",
            bullet_points=[
                "Moving beyond conversational chatbots to full scientific lifecycles",
                "Dynamic Task DAG planning with formal verification guardrails",
                "In-silico reproducibility and blinded peer review pipelines",
            ],
            speaker_notes="Welcome executive stakeholders. Today we introduce the AI Research OS.",
            visual_metadata={"theme": "midnight_slate", "icon": "sparkles"},
        )
        s2 = DBPresentationSlide(
            id=uuid.uuid4(),
            presentation_id=pres.id,
            slide_number=2,
            layout_type="chart_comparison",
            headline="8 Generations of Agentic Research Architecture",
            bullet_points=[
                "Gen 1-2: Planning & Hybrid RAG",
                "Gen 3-4: Multimodal Ingestion & Grounded Evidence",
                "Gen 5-6: Dialectical Debate & AST Sandboxing",
                "Gen 7-8: Canvas Studio, Synthetic Datasets & Patent Landscape",
            ],
            speaker_notes="Walk through the comprehensive 34 phases across all 8 architectural generations.",
            visual_metadata={"chart_type": "timeline", "generations": 8, "phases": 34},
        )
        session.add_all([s1, s2])

        podcast = DBPodcastBriefing(
            id=uuid.uuid4(),
            user_id=admin_user.id,
            workspace_id=workspace.id,
            project_id=project.id,
            title="The Morning AI Lab Briefing: Week 37 Synthesis",
            episode_topic="Autonomous Hydride Superconductivity Discovery & In-Silico Reproducibility",
            host_name="Dr. Sarah Lin (Lead AI Scientist)",
            expert_name="Alex Chen (Chief Architect)",
            total_duration_sec=390.0,
            total_dialogue_turns=4,
            dialogue_transcript_json=[
                {"speaker": "Dr. Sarah Lin", "text": "Welcome back to the Morning Lab Briefing. Today, we're breaking down a major breakthrough in hydride superconductor screening.", "timestamp_start_sec": 0.0, "timestamp_end_sec": 8.5},
                {"speaker": "Alex Chen", "text": "That's right, Sarah. The autonomous DAG pipeline screened 45,000 crystal candidates overnight, isolating a ternary La-Y-H phase stable at 165 GPa.", "timestamp_start_sec": 8.5, "timestamp_end_sec": 21.0},
                {"speaker": "Dr. Sarah Lin", "text": "And what's remarkable is the reproducibility trace—the sandbox verified the Eliashberg coupling constant with less than 0.01% deviation.", "timestamp_start_sec": 21.0, "timestamp_end_sec": 33.0},
                {"speaker": "Alex Chen", "text": "The patent landscape engine also confirmed a clear Freedom-to-Operate path with a 92% white-space clearance index.", "timestamp_start_sec": 33.0, "timestamp_end_sec": 45.0},
            ],
            status="synthesized",
        )
        session.add(podcast)

    # 9. Seed Blinded Peer Review Manuscript (Phase 31)
    peer_stmt = select(DBPeerReviewManuscript).where(DBPeerReviewManuscript.title.like("%Zero-Shot Theorem Proving%"))
    peer_res = await session.execute(peer_stmt)
    manuscript = peer_res.scalar_one_or_none()

    if not manuscript:
        manuscript = DBPeerReviewManuscript(
            id=uuid.uuid4(),
            user_id=admin_user.id,
            workspace_id=workspace.id,
            project_id=project.id,
            title="Zero-Shot Theorem Proving with Monte Carlo Tree Search and Formal Verification Grounding",
            abstract="We present an autonomous formal reasoning framework combining neural tree guidance with Lean 4 kernel verification, achieving 84.6% on miniF2F.",
            field_of_study="computer_science",
            venue_format="nature",
            status="accepted",
            manuscript_content="# Zero-Shot Theorem Proving\n\n## Abstract\nFormal mathematical theorem proving requires navigating non-convex search spaces...",
            claimed_contributions=["Lean 4 kernel integration", "Dynamic MCTS guidance", "State-of-the-art miniF2F score"],
            keywords=["theorem proving", "lean 4", "mcts", "formal verification"],
            overall_score=8.75,
            camera_ready_doi="10.1038/s41586-026-08891-x",
        )
        session.add(manuscript)
        await session.flush()

        rev1 = DBPeerReviewReport(
            id=uuid.uuid4(),
            manuscript_id=manuscript.id,
            reviewer_persona="formal_verification_critic",
            reviewer_title="Anonymous Referee #1 (Formal Verification Specialist)",
            originality_score=9.0,
            methodology_score=9.2,
            empirical_soundness=8.8,
            clarity_score=8.5,
            composite_score=8.875,
            recommendation="accept",
            summary_verdict="Accept. Grounding MCTS expansions directly within Lean 4 kernel states solves reward hacking in formal proof synthesis.",
            strengths=["Rigorous integration with Lean 4 kernel.", "Solid empirical gains on miniF2F benchmark."],
            weaknesses=["Computational budget scaling curves could be more detailed."],
            detailed_critique="The methodology is exceptionally sound. The ablation study in Table 3 clearly demonstrates the value of dynamic tree pruning.",
            required_revisions=["Add expanded budget plot for 64-step vs 256-step tree depths."],
        )
        session.add(rev1)

    # 10. Seed Collaborative Research Canvas (Phase 32)
    canvas_stmt = select(DBCanvasBoard).where(DBCanvasBoard.title.like("%Quantum-Classical Hybrid%"))
    canvas_res = await session.execute(canvas_stmt)
    board = canvas_res.scalar_one_or_none()

    if not board:
        board = DBCanvasBoard(
            id=uuid.uuid4(),
            user_id=admin_user.id,
            workspace_id=workspace.id,
            project_id=project.id,
            title="Quantum-Classical Hybrid Optimization Workflow",
            description="Visual ideation board mapping variational quantum eigensolver (VQE) pipelines into LLM agentic tool loops.",
            viewport_state={"zoom": 1.0, "pan_x": 0.0, "pan_y": 0.0},
            background_grid="dots",
            status="active",
        )
        session.add(board)
        await session.flush()

        n1 = DBCanvasNode(
            id=uuid.uuid4(),
            canvas_id=board.id,
            node_type="hypothesis",
            title="Hypothesis: VQE Ansatz Compression",
            content="Parameterized quantum circuits can be compressed by 40% using agentic pruning heuristics.",
            confidence_score=0.92,
            status="verified",
            position_x=100.0,
            position_y=150.0,
            width=280.0,
            height=160.0,
            color_accent="#38bdf8",
        )
        n2 = DBCanvasNode(
            id=uuid.uuid4(),
            canvas_id=board.id,
            node_type="evidence",
            title="In-Silico Benchmark: H4 Molecular Ground State",
            content="Simulated VQE run converged to -1.9874 Hartree with 99.98% state fidelity.",
            confidence_score=0.97,
            status="verified",
            position_x=450.0,
            position_y=150.0,
            width=280.0,
            height=160.0,
            color_accent="#4ade80",
        )
        n3 = DBCanvasNode(
            id=uuid.uuid4(),
            canvas_id=board.id,
            node_type="conclusion",
            title="Synthesis Dossier: Quantum Chemistry Milestone",
            content="Ansatz compression preserves ground state chemistry accuracy while reducing 2-qubit CNOT gate count.",
            confidence_score=0.95,
            status="verified",
            position_x=800.0,
            position_y=150.0,
            width=280.0,
            height=160.0,
            color_accent="#a855f7",
        )
        session.add_all([n1, n2, n3])
        await session.flush()

        e1 = DBCanvasEdge(
            id=uuid.uuid4(),
            canvas_id=board.id,
            source_node_id=n1.id,
            target_node_id=n2.id,
            relation_type="supports",
            label="validates via simulation",
            weight=1.0,
        )
        e2 = DBCanvasEdge(
            id=uuid.uuid4(),
            canvas_id=board.id,
            source_node_id=n2.id,
            target_node_id=n3.id,
            relation_type="derives_from",
            label="generates findings",
            weight=1.0,
        )
        session.add_all([e1, e2])

    # 11. Seed Synthetic Instruction Dataset (Phase 33)
    data_stmt = select(DBSyntheticDataset).where(DBSyntheticDataset.name.like("%Frontier-Multimodal%"))
    data_res = await session.execute(data_stmt)
    dataset = data_res.scalar_one_or_none()

    if not dataset:
        dataset = DBSyntheticDataset(
            id=uuid.uuid4(),
            user_id=admin_user.id,
            workspace_id=workspace.id,
            project_id=project.id,
            name="Frontier-Multimodal-Reasoning-100K",
            description="Curated high-quality scientific derivation and multi-step reasoning pairs generated via active agentic self-critique.",
            dataset_format="dpo_preference",
            domain_field="condensed_matter_physics",
            target_model_family="llama_3",
            total_samples=1000,
            quality_filter_threshold=0.85,
            status="curated",
        )
        session.add(dataset)
        await session.flush()

        s1 = DBInstructionSample(
            id=uuid.uuid4(),
            dataset_id=dataset.id,
            sample_index=1,
            system_prompt="You are a theoretical condensed matter physics expert.",
            instruction="Derive the critical temperature Tc expression from the linearized Eliashberg equations in the strong-coupling limit.",
            chosen_response="In the strong-coupling limit (lambda > 2.0), the Allen-Dynes modification to the McMillan equation gives Tc = 0.1827 f1 f2 sqrt(lambda <w2>).",
            rejected_response="Tc is simply proportional to lambda times temperature.",
            quality_score=0.98,
        )
        session.add(s1)

    # 12. Seed Patent Landscape Corpus (Phase 34)
    patent_stmt = select(DBPatentCorpus).where(DBPatentCorpus.title.like("%Autonomous Agent Memory%"))
    patent_res = await session.execute(patent_stmt)
    patent_corpus = patent_res.scalar_one_or_none()

    if not patent_corpus:
        patent_corpus = DBPatentCorpus(
            id=uuid.uuid4(),
            user_id=admin_user.id,
            workspace_id=workspace.id,
            project_id=project.id,
            title="Autonomous Agent Memory Architecture and Dynamic Routing Patents",
            technology_domain="artificial_intelligence",
            cpc_classification="G06N 3/08",
            jurisdiction="GLOBAL",
            status="completed",
            total_patents_indexed=3,
            freedom_to_operate_verdict="clear",
            metadata_json={"white_space_index": 0.92, "active_assignees": ["Google LLC", "OpenAI", "DeepMind"]},
        )
        session.add(patent_corpus)
        await session.flush()

        p1 = DBPatentDocument(
            id=uuid.uuid4(),
            corpus_id=patent_corpus.id,
            patent_number="US-11847321-B2",
            title="Hierarchical Episodic Vector Memory Retrieval in Distributed Cognitive Agent Systems",
            abstract="A distributed computing system configuring memory vectors with reciprocal rank fusion and temporal decay weighting.",
            assignee="DeepMind Technologies Ltd",
            filing_date="2022-04-12",
            publication_date="2023-12-19",
            cpc_classes=["G06N 3/08", "G06F 16/903"],
            status="granted",
            claims_count=20,
            citations_count=14,
        )
        session.add(p1)
        await session.flush()

        pc1 = DBPatentClaim(
            id=uuid.uuid4(),
            patent_id=p1.id,
            claim_number=1,
            claim_type="independent",
            claim_text="A computer-implemented method comprising: receiving a multimodal query; executing reciprocal rank fusion across dense vector and sparse lexical indices; and routing subtasks to specialized agents.",
        )
        session.add(pc1)

        prior_eval = DBPriorArtEvaluation(
            id=uuid.uuid4(),
            corpus_id=patent_corpus.id,
            prior_art_patent_id=p1.id,
            target_invention_claim="Dynamic DAG Task Routing with PRISMA Systematic Screening",
            novelty_score=0.91,
            obviousness_score=0.18,
            overlap_ratio=0.12,
            verdict="distinguishable",
            detailed_rationale="Non-overlapping claim scope; proposed platform utilizes AST-sandboxed execution and PRISMA meta-analysis absent in prior art.",
            mitigation_strategy="Explicitly claim closed-loop reproducibility sandbox in pending filings.",
        )
        session.add(prior_eval)

        fto_rep = DBFreedomToOperateReport(
            id=uuid.uuid4(),
            corpus_id=patent_corpus.id,
            total_examined_patents=48,
            high_risk_claims_count=0,
            medium_risk_claims_count=2,
            fto_clearance_percentage=96.4,
            summary_assessment="Full commercial clearance confirmed. No blocking independent claims found in active US, EP, or WIPO patent families.",
            white_space_opportunities=[
                {"domain": "Closed-loop in-silico sandbox grounding", "white_space_index": 0.94},
                {"domain": "Multi-speaker scientific podcast briefing synthesis", "white_space_index": 0.96},
            ],
            claim_chart_matrices=[],
        )
        session.add(fto_rep)

    # 13. Seed Long-term Knowledge Graph & Research Memory (Phases 16, 17)
    mem_stmt = select(DBResearchMemory).where(DBResearchMemory.title.like("%Lanthanum Hydride%"))
    mem_res = await session.execute(mem_stmt)
    if not mem_res.scalar_one_or_none():
        mem = DBResearchMemory(
            id=uuid.uuid4(),
            user_id=admin_user.id,
            workspace_id=str(workspace.id),
            project_id=str(project.id),
            memory_type="finding",
            title="Lanthanum Hydride High-Tc Phase Stability",
            content="Fm-3m LaH10 phase stabilizes at 170 GPa exhibiting phonon-mediated Tc of 250-264 K.",
            confidence_score=0.98,
            tags=["superconductivity", "hydrides", "dft"],
            provenance_json={"source": "report", "job_id": str(job.id) if job else None},
        )
        session.add(mem)

    ke_stmt = select(DBKnowledgeEntity).where(DBKnowledgeEntity.name == "Lanthanum Superhydride (LaH10)")
    ke_res = await session.execute(ke_stmt)
    ke1 = ke_res.scalar_one_or_none()
    if not ke1:
        ke1 = DBKnowledgeEntity(
            id=uuid.uuid4(),
            workspace_id=workspace.id,
            name="Lanthanum Superhydride (LaH10)",
            canonical_name="lanthanum superhydride (lah10)",
            entity_type="MATERIAL",
            description="High-pressure clathrate hydride with high critical superconducting temperature.",
            properties_json={"crystal_structure": "Fm-3m", "predicted_tc_kelvin": 260},
        )
        ke2 = DBKnowledgeEntity(
            id=uuid.uuid4(),
            workspace_id=workspace.id,
            name="Density Functional Theory (DFT)",
            canonical_name="density functional theory (dft)",
            entity_type="TECHNOLOGY",
            description="Quantum mechanical modeling method used in materials science.",
            properties_json={"accuracy": "ab-initio", "standard_codes": ["VASP", "Quantum ESPRESSO"]},
        )
        session.add_all([ke1, ke2])
        await session.flush()

        rel = DBKnowledgeRelation(
            id=uuid.uuid4(),
            user_id=admin_user.id,
            project_id=project.id,
            source_id=ke1.id,
            target_id=ke2.id,
            relation_type="EVALUATED_ON",
            description="LaH10 electronic structure and Cooper pairing is calculated using DFT.",
            weight=1.0,
            confidence=0.99,
            properties_json={},
        )
        session.add(rel)

    # 14. Seed Infrastructure Worker Node
    worker_stmt = select(DBWorkerNode).where(DBWorkerNode.worker_id == "worker-node-01")
    worker_res = await session.execute(worker_stmt)
    if not worker_res.scalar_one_or_none():
        node = DBWorkerNode(
            id=uuid.uuid4(),
            worker_id="worker-node-01",
            hostname="compute-cluster-alpha.internal",
            concurrency=8,
            active_tasks=["task-dag-executor", "ast-sandbox-evaluator"],
            cpu_percent=24.5,
            memory_mb=4096.0,
            status="HEALTHY",
        )
        session.add(node)

    await session.commit()
    logger.info("Successfully seeded demo data across all platform modules!")
    return {
        "status": "success",
        "message": "Demo data successfully seeded across all 34 research phases.",
        "admin_user": "admin / Password123!",
        "researcher_user": "elena / Password123!",
        "workspace": "frontier-ai-lab",
        "project": "superconductor-discovery",
    }


async def main():
    """Main CLI entry point for seeding demo data."""
    print("Hydrating Agentic Multimodal Research Platform demo database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        result = await seed_all_demo_data(session)
        print(f"[SUCCESS] {result['message']}")
        print(f"  - Admin: {result['admin_user']}")
        print(f"  - Researcher: {result['researcher_user']}")
        print(f"  - Workspace: {result['workspace']}")
        print(f"  - Project: {result['project']}")


if __name__ == "__main__":
    asyncio.run(main())
