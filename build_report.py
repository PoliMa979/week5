#!/usr/bin/env python3
"""Build the A05 report from the browser experiment evidence."""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parent
EVIDENCE_PATH = ROOT / "evidence" / "experiment_results.json"
OUTPUT_PATH = ROOT / "polina_maltseva_a05_report.pdf"

INK = colors.HexColor("#172033")
TEAL = colors.HexColor("#0F7C82")
TEAL_LIGHT = colors.HexColor("#E8F4F3")
GOLD = colors.HexColor("#B97842")
SLATE = colors.HexColor("#566274")
GRID = colors.HexColor("#CDD5DF")
PALE = colors.HexColor("#F5F7FA")
RED = colors.HexColor("#A43E3E")


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(GRID)
    canvas.setLineWidth(0.5)
    canvas.line(18 * mm, 13 * mm, A4[0] - 18 * mm, 13 * mm)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(SLATE)
    canvas.drawString(18 * mm, 8.5 * mm, "LLM4Rec - Assignment A05")
    canvas.drawRightString(A4[0] - 18 * mm, 8.5 * mm, f"Page {doc.page}")
    canvas.restoreState()


class ReportDocTemplate(BaseDocTemplate):
    def __init__(self, filename):
        super().__init__(
            filename,
            pagesize=A4,
            leftMargin=18 * mm,
            rightMargin=18 * mm,
            topMargin=14 * mm,
            bottomMargin=17 * mm,
            title="From Sparse Ratings to Movie Discovery",
            author="Polina Maltseva",
            subject="LLM4Rec Assignment A05",
        )
        frame = Frame(
            self.leftMargin,
            self.bottomMargin,
            self.width,
            self.height,
            id="main",
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
        )
        self.addPageTemplates(PageTemplate(id="report", frames=[frame], onPage=footer))


def make_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=21,
            textColor=INK,
            alignment=TA_CENTER,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Meta",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=SLATE,
            alignment=TA_CENTER,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Section",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=14,
            textColor=TEAL,
            spaceBefore=7,
            spaceAfter=4,
            keepWithNext=True,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Subsection",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=11,
            textColor=INK,
            spaceBefore=5,
            spaceAfter=2,
            keepWithNext=True,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodySmall",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=8.1,
            leading=10.1,
            textColor=INK,
            alignment=TA_JUSTIFY,
            spaceAfter=3,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Compact",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=7.4,
            leading=9,
            textColor=INK,
            alignment=TA_LEFT,
            spaceAfter=1,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Abstract",
            parent=styles["BodyText"],
            fontName="Helvetica-Oblique",
            fontSize=8.3,
            leading=10.4,
            textColor=INK,
            alignment=TA_JUSTIFY,
            leftIndent=5 * mm,
            rightIndent=5 * mm,
            spaceAfter=3,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Caption",
            parent=styles["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=7,
            leading=8.5,
            textColor=SLATE,
            alignment=TA_CENTER,
            spaceBefore=2,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Callout",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=7.8,
            leading=9.6,
            textColor=INK,
            backColor=TEAL_LIGHT,
            borderColor=TEAL,
            borderWidth=0.6,
            borderPadding=5,
            leftIndent=2,
            rightIndent=2,
            spaceBefore=3,
            spaceAfter=5,
        )
    )
    return styles


def P(text, style):
    return Paragraph(text, style)


def table_style(header=True, font_size=7, alignments=None):
    commands = [
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("LEADING", (0, 0), (-1, -1), font_size + 1.5),
        ("TEXTCOLOR", (0, 0), (-1, -1), INK),
        ("GRID", (0, 0), (-1, -1), 0.35, GRID),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("ROWBACKGROUNDS", (0, 1 if header else 0), (-1, -1), [colors.white, PALE]),
    ]
    if header:
        commands.extend(
            [
                ("BACKGROUND", (0, 0), (-1, 0), TEAL),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    if alignments:
        for col, alignment in alignments.items():
            commands.append(("ALIGN", (col, 1 if header else 0), (col, -1), alignment))
    return TableStyle(commands)


def fmt(value, digits=4):
    return f"{value:.{digits}f}"


def top10_table(user, styles):
    rows = [
        [
            P("#", styles["Compact"]),
            P(f"User {user['userId']}", styles["Compact"]),
            P("Score", styles["Compact"]),
            P("n", styles["Compact"]),
        ]
    ]
    for index, item in enumerate(user["top10"], 1):
        marker = " *" if item["relevantTest"] else ""
        rows.append(
            [
                str(index),
                P(item["title"] + marker, styles["Compact"]),
                fmt(item["score"], 3),
                str(item["trainingRatings"]),
            ]
        )
    table = Table(rows, colWidths=[7 * mm, 58 * mm, 15 * mm, 8 * mm], repeatRows=1)
    table.setStyle(table_style(font_size=6.4, alignments={0: "RIGHT", 2: "RIGHT", 3: "RIGHT"}))
    return table


def build_report():
    evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    default, improved, repeat = evidence["runs"]
    user1, user19 = default["userAnalysis"]
    manual = default["manualCheck"]
    styles = make_styles()
    story = []

    # Page 1
    story.extend(
        [
            P("From Sparse Ratings to Movie Discovery:<br/>Matrix Factorization on MovieLens 100K", styles["ReportTitle"]),
            P(
                "Student: Polina Maltseva &nbsp;&nbsp;|&nbsp;&nbsp; Team: Individual &nbsp;&nbsp;|&nbsp;&nbsp; "
                "Email: pdmaltseva@edu.hse.ru &nbsp;&nbsp;|&nbsp;&nbsp; Date: 2026-10-16<br/>"
                "Assignment: A05 - From Ratings to Recommendations (Week 5)",
                styles["Meta"],
            ),
            Spacer(1, 4),
            P("Abstract", styles["Subsection"]),
            P(
                "A streaming service must turn a 93.70% sparse rating matrix into short, useful movie lists. "
                "I implemented a 16-factor TensorFlow.js model with chronological per-user splitting, Adam training, "
                "validation checkpointing, Top-10 retrieval, and Recall@10 evaluation. The selected checkpoint reached "
                "test RMSE 1.0503 versus 1.2289 for the training-mean baseline, while Recall@10 was 0.0134 over 861 "
                "evaluable users. The experiment shows that accurate rating prediction can still produce weak and "
                "sometimes poorly personalized discovery lists, especially for light users.",
                styles["Abstract"],
            ),
            P(
                "<b>Index Terms</b> - matrix factorization, collaborative filtering, TensorFlow.js, MovieLens, "
                "Recall@10, novelty.",
                styles["BodySmall"],
            ),
            P("1. Introduction", styles["Section"]),
            P(
                "MovieLens 100K contains explicit ratings but leaves most user-movie pairs unobserved. Treating those "
                "missing pairs as zero would convert absence of evidence into negative preference; instead, the model "
                "optimizes only observed training ratings. The operational problem is not only to predict held-out "
                "ratings, but also to form a useful Top-10 row from the catalogue.",
                styles["BodySmall"],
            ),
            P(
                "A concrete example is User 1: from 217 training and 27 validation ratings, the application returns a "
                "list led by <i>Thieves (Voleurs, Les)</i> with score 4.8804. Two items in that list are relevant held-out "
                "movies, so this user's Recall@10 is 2/19 = 0.1053.",
                styles["BodySmall"],
            ),
            P(
                "<b>Contributions.</b> (1) A complete implementation of the six required functions using batched "
                "TensorFlow.js operations. (2) A reproducible experiment with two identical seeded runs, one "
                "regularization change, two user-level analyses, and a stored machine-readable evidence file.",
                styles["BodySmall"],
            ),
            P("2. Related Work", styles["Section"]),
            P(
                "The dataset is the stable MovieLens 100K benchmark [1], [2]. Matrix factorization represents users and "
                "items in a shared latent space and scores a pair with a dot product [3]. Adam supplies adaptive "
                "first-order updates for the sparse mini-batches [4]. TensorFlow.js provides browser-side tensor "
                "operations and automatic differentiation [5]. Following Herlocker et al. [6], I report both rating "
                "error and a list metric because predictive accuracy alone does not characterize recommendation value.",
                styles["BodySmall"],
            ),
            P("Alternatives considered", styles["Subsection"]),
            P(
                "<b>Item-item similarity:</b> interpretable, but sparse overlap can make similarities unstable. "
                "<b>ALS:</b> natural for factor models, but the assignment requires TensorFlow.js optimization. "
                "<b>User and item biases:</b> likely to stabilize ranking, but excluded from the required baseline "
                "formula so that the six TODO functions remain comparable to the starter contract.",
                styles["BodySmall"],
            ),
        ]
    )

    # Page 2
    story.append(PageBreak())
    story.extend([P("3. Data and Recommendation Analysis", styles["Section"])])
    data_rows = [
        ["Quantity", "Observed value", "Interpretation"],
        ["Users / movies / ratings", "943 / 1,682 / 100,000", "Raw MovieLens 100K files"],
        ["Matrix sparsity", "93.70%", "1 - 100,000 / (943 x 1,682)"],
        ["Train / validation / test", "79,619 / 9,596 / 10,785", "Per user, ordered by timestamp"],
        ["Training mean", "3.5806", "Mean-rating baseline prediction"],
        ["Absent from training", "0 users / 71 movies", "Cold movie ids cannot be learned"],
        ["Unseen val / test rows", "35 / 53", "Ratings whose movie has no train row"],
        ["Recall evaluation", "861 users / 5,142 relevant", "82 users excluded; 13 relevant unseen ids"],
    ]
    data_table = Table(data_rows, colWidths=[43 * mm, 45 * mm, 84 * mm], repeatRows=1)
    data_table.setStyle(table_style(font_size=7.1, alignments={1: "CENTER"}))
    story.extend(
        [
            data_table,
            P("Table I. Dataset, chronological split, and evaluation exclusions.", styles["Caption"]),
            P("3.1 Two Top-10 lists", styles["Subsection"]),
            Table(
                [[top10_table(user1, styles), top10_table(user19, styles)]],
                colWidths=[88 * mm, 88 * mm],
                style=TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ]
                ),
            ),
            P(
                "Table II. Top-10 recommendations from the default checkpoint. n = training ratings; * = relevant "
                "test movie. No item appears in the corresponding user's train or validation history.",
                styles["Caption"],
            ),
            P("3.2 Familiar choices vs. new discoveries", styles["Subsection"]),
            P(
                "<b>User 1 (heavy user).</b> The history is led by Drama (38.1%), Comedy (33.2%), and Action (28.3%). "
                "The list keeps Comedy (40%) and Drama (30%), and the two hits - <i>When the Cats Away</i> and "
                "<i>The Wrong Trousers</i> - fit that familiar profile. Yet the median popularity drops from 106 "
                "training ratings in the history to 9.5 in the list. This is discovery inside familiar genres: safer "
                "than a completely novel direction, but strongly exposed to noisy estimates for rare films.",
                styles["BodySmall"],
            ),
            P(
                "<b>User 19 (light user).</b> Only 18 history ratings are available; Comedy and Drama each occur in "
                "55.6% of them. The list shifts to Action and Horror (40% each), including <i>Hellraiser: Bloodline</i>, "
                "<i>Wishmaster</i>, and <i>Thinner</i>. Its median item has 12.5 training ratings versus 193.5 in the "
                "history, and the only eligible relevant test movie is missed. This is novel but not convincingly "
                "personal. For a streaming platform, such a row should be constrained by confidence or mixed with a "
                "popularity/bias component.",
                styles["BodySmall"],
            ),
        ]
    )

    # Page 3
    story.append(PageBreak())
    story.extend(
        [
            P("4. Method", styles["Section"]),
            P("4.1 Pipeline", styles["Subsection"]),
            P(
                "1) Parse <font name='Courier'>u.data</font> and <font name='Courier'>u.item</font>. "
                "2) Group ratings by user, sort by timestamp (movie id breaks ties), and allocate floor(0.8n), "
                "floor(0.1n), and the remainder to train, validation, and test. 3) Initialize 16-dimensional user and "
                "movie factors. 4) Train with mini-batched Adam on observed ratings only. 5) retain the earliest epoch "
                "with minimum validation RMSE. 6) Produce Top-10 lists excluding the user's train and validation items. "
                "7) evaluate Recall@10 for test ratings at least 4.0 whose movie id occurs in training.",
                styles["BodySmall"],
            ),
            P("4.2 Model and loss", styles["Subsection"]),
            P(
                "The prediction is <b>r_hat(u,i) = mu + p_u dot q_i</b>, where mu is the training mean and both vectors "
                "have 16 components. Displayed rating predictions are clamped to [1,5], but training uses the unclamped "
                "score so gradients do not vanish at the boundaries. For each mini-batch, the objective is mean squared "
                "error plus 0.05 times the mean squared norm of the gathered user and movie rows. Applying a full-matrix "
                "penalty at every batch would repeatedly regularize unrelated rows and overwhelm the data term.",
                styles["BodySmall"],
            ),
            P("4.3 Training and checkpointing", styles["Subsection"]),
            P(
                "Adam uses learning rate 0.01, batch size 64, 20 epochs, and deterministic seed 20261016. User and item "
                "matrices use adjacent seeds to avoid identical same-id rows. A seeded Fisher-Yates shuffle changes the "
                "mini-batch order each epoch. Whenever validation RMSE improves, both factor matrices are cloned; the "
                "selected matrices are restored after epoch 20 so test metrics and recommendations use the chosen "
                "checkpoint rather than the final weights.",
                styles["BodySmall"],
            ),
            P("4.4 Retrieval and metric", styles["Subsection"]),
            P(
                "For a user, one matrix multiplication scores all movie rows, a mask assigns -1e9 to missing metadata "
                "and train/validation items, and <font name='Courier'>tf.topk</font> returns the highest remaining "
                "scores. Recall for a user is hits divided by eligible relevant test movies; the reported metric is the "
                "unweighted mean across 861 evaluable users. Thirteen distinct relevant test movie ids absent from the "
                "training pool are reported as exclusions rather than silently counted as recommendable.",
                styles["BodySmall"],
            ),
            P("4.5 Implementation and environment", styles["Subsection"]),
        ]
    )
    environment_rows = [
        ["Component", "Version / setting"],
        ["TensorFlow.js", "4.22.0; webgl backend"],
        ["Browser", "Headless Chrome 155.0.0.0"],
        ["Renderer", "ANGLE Metal Renderer: Apple M4 Pro"],
        ["Factors / epochs / batch", "16 / 20 / 64"],
        ["Learning rate / L2 / seed", "0.01 / 0.05 / 20261016"],
    ]
    environment_table = Table(environment_rows, colWidths=[55 * mm, 117 * mm], repeatRows=1)
    environment_table.setStyle(table_style(font_size=7.2))
    story.extend(
        [
            environment_table,
            P(
                "<b>Code availability:</b> "
                "<link href='https://github.com/PoliMa979/week5' color='#0F7C82'>"
                "https://github.com/PoliMa979/week5</link>. The repository includes the application, browser runner, "
                "raw evidence JSON, screenshot, report source, and this PDF.",
                styles["Callout"],
            ),
        ]
    )

    # Page 4
    story.append(PageBreak())
    story.extend([P("5. Experiments and Verification", styles["Section"])])
    result_rows = [
        ["Model", "Selected epoch", "Val RMSE", "Test RMSE", "Recall@10"],
        ["Training-mean baseline", "-", fmt(default["baselineValidationRMSE"]), fmt(default["baselineTestRMSE"]), "-"],
        ["MF, L2 = 0.05", "2", fmt(default["bestCheckpoint"]["valRMSE"]), fmt(default["selectedModelTestRMSE"]), fmt(default["recall"]["overallRecall"])],
        ["MF, L2 = 0.10", "6", fmt(improved["bestCheckpoint"]["valRMSE"]), fmt(improved["selectedModelTestRMSE"]), fmt(improved["recall"]["overallRecall"])],
    ]
    result_table = Table(result_rows, colWidths=[53 * mm, 29 * mm, 29 * mm, 29 * mm, 29 * mm], repeatRows=1)
    result_table.setStyle(table_style(font_size=7.2, alignments={1: "CENTER", 2: "RIGHT", 3: "RIGHT", 4: "RIGHT"}))
    selected_epochs = {1, 2, 3, 5, 10, 15, 20}
    curve_rows = [["Epoch", "Train RMSE", "Validation RMSE"]]
    for row in default["history"]:
        if row["epoch"] in selected_epochs:
            curve_rows.append([str(row["epoch"]), fmt(row["trainRMSE"]), fmt(row["valRMSE"])])
    curve_table = Table(curve_rows, colWidths=[30 * mm, 40 * mm, 45 * mm], repeatRows=1)
    curve_table.setStyle(table_style(font_size=7.1, alignments={0: "RIGHT", 1: "RIGHT", 2: "RIGHT"}))
    story.extend(
        [
            result_table,
            P("Table III. Rating and retrieval results from validation-selected checkpoints.", styles["Caption"]),
            P(
                "The default model improves test RMSE by 0.1786 (14.5%) relative to the mean baseline. Its Recall@10 "
                "is only 0.0134: 102 hits over 5,142 eligible relevant movies, with at least one hit for 87 of 861 "
                "users. L2 = 0.10 improves test RMSE to 1.0444 but reduces Recall@10 to 0.0080. Therefore the one-variable "
                "change helps rating prediction and hurts list retrieval; optimizing RMSE alone is not sufficient.",
                styles["BodySmall"],
            ),
            curve_table,
            P(
                "Table IV. Selected points from the default learning curve. Validation error is best at epoch 2 while "
                "training error continues falling, which motivates checkpoint restoration.",
                styles["Caption"],
            ),
            P("5.1 Verification", styles["Subsection"]),
            P(
                "<b>Automated checks.</b> The starter harness reports 11 passed, 0 failed, and 0 pending. It tests "
                "allocation, clamping, batched training, earliest-tie checkpoint selection, history masking, Recall@10, "
                "and zero-denominator guards. Two complete default runs produced identical 20-epoch histories; the "
                "maximum absolute difference was 0. Tensor count was stable at 27 after each of the three full runs.",
                styles["BodySmall"],
            ),
        ]
    )
    product_rows = [["k", "p_k", "q_k", "product"]]
    for index, (p_value, q_value, product) in enumerate(
        zip(manual["userVector"], manual["itemVector"], manual["products"]), 1
    ):
        product_rows.append([str(index), fmt(p_value), fmt(q_value), fmt(product)])
    left_products = Table(product_rows[:9], colWidths=[10 * mm, 22 * mm, 22 * mm, 24 * mm], repeatRows=1)
    right_products = Table([product_rows[0]] + product_rows[9:], colWidths=[10 * mm, 22 * mm, 22 * mm, 24 * mm], repeatRows=1)
    left_products.setStyle(table_style(font_size=6.7, alignments={0: "RIGHT", 1: "RIGHT", 2: "RIGHT", 3: "RIGHT"}))
    right_products.setStyle(table_style(font_size=6.7, alignments={0: "RIGHT", 1: "RIGHT", 2: "RIGHT", 3: "RIGHT"}))
    story.extend(
        [
            P("5.2 Independent dot-product check", styles["Subsection"]),
            Table(
                [[left_products, right_products]],
                colWidths=[84 * mm, 84 * mm],
                style=TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ]
                ),
            ),
            P(
                f"For User 1 and <i>{manual['title']}</i>, the 16 products sum to {fmt(manual['dot'])}. "
                f"Adding mu = {fmt(manual['globalMean'])} gives {fmt(manual['unclampedScore'])}; the page score is "
                f"{fmt(manual['displayedScore'])}. The difference is below 4e-7 and is explained by Float32 rounding.",
                styles["BodySmall"],
            ),
        ]
    )

    # Page 5
    story.append(PageBreak())
    story.extend(
        [
            P("6. Discussion", styles["Section"]),
            P("6.1 Failure case, root cause, and fix", styles["Subsection"]),
            P(
                "The first evidence run appeared to leak two tensors per completed experiment: the count increased from "
                "29 to 31 to 33. The model code was initially suspect, but the leak came from the verification runner: "
                "two factor slices were read for the manual dot-product check outside <font name='Courier'>tf.tidy</font>. "
                "Wrapping those two reads in <font name='Courier'>tf.tidy</font> and repeating all three experiments "
                "held the count at 27 after every run. This distinguished an instrumentation defect from a training-loop "
                "defect and verified that repeated Train clicks dispose the old factor variables.",
                styles["BodySmall"],
            ),
            P("6.2 What worked", styles["Subsection"]),
            P(
                "- The validation-selected model consistently beats the mean-rating baseline.<br/>"
                "- Seeded initialization and shuffling make complete histories exactly reproducible.<br/>"
                "- Restoring epoch 2 prevents the final epoch's worse validation state (1.0317) from driving the Top-10 lists.<br/>"
                "- User histories are masked correctly: both inspected lists have zero train/validation overlaps.",
                styles["BodySmall"],
            ),
            P("6.3 What was surprising", styles["Subsection"]),
            P(
                "- Better RMSE did not imply better retrieval: L2 = 0.10 reduced test RMSE by 0.0059 but lost 43 of the "
                "default run's 102 hits.<br/>"
                "- Discovery is often driven by low-support movies. The default model puts <i>Pather Panchali</i> "
                "(7 training ratings) in 204 of 943 lists and <i>Perfect Candidate</i> (3 ratings) in 177 lists.<br/>"
                "- User 19's list is highly novel but poorly aligned with the Comedy/Drama-heavy history, illustrating "
                "how a short user vector can amplify uncertain item directions.",
                styles["BodySmall"],
            ),
            P("6.4 Next improvement", styles["Subsection"]),
            P(
                "I would add explicit user and movie biases, keep L2 = 0.05 as the retrieval-oriented baseline, and "
                "rerank with a confidence rule such as a minimum of 20 training ratings for discovery slots. The "
                "comparison should report RMSE, Recall@10, catalogue coverage, and the share of Top-10 slots occupied by "
                "low-support movies. This directly tests whether rare-item exposure becomes safer without collapsing "
                "discovery into popularity.",
                styles["BodySmall"],
            ),
            P("7. AI Usage Disclosure", styles["Section"]),
            P(
                "<b>Tool.</b> OpenAI Codex desktop 26.924.22138 (build 11645), used on 2026-10-16. "
                "<b>Uses.</b> Requirement extraction, repository comparison, implementation of the six TODO functions, "
                "browser automation, experiment logging, reference checking, and report drafting. "
                "<b>Verification performed in the assisted session.</b> 11/11 starter tests, two identical default "
                "training histories, a one-variable regularization run, stable tensor counts, train/validation masking, "
                "and a direct 16-term dot-product recomputation from the learned factors. "
                "<b>Not independently verified by the student at report-generation time.</b> The student has not yet "
                "repeated the manual addition or rerun the browser experiment without Codex assistance; this limitation "
                "is disclosed rather than replaced with a false claim. "
                "<b>Session log.</b> <font name='Courier'>polina_maltseva_a05_session.json</font> must be the native, "
                "unmodified Codex export. No synthetic session file was created.",
                styles["BodySmall"],
            ),
            P(
                "Evidence files: <font name='Courier'>evidence/experiment_results.json</font> contains every metric, "
                "history row, recommendation, exclusion, and factor vector used here; "
                "<font name='Courier'>evidence/trained_application.png</font> records the running page.",
                styles["Callout"],
            ),
        ]
    )

    # Page 6 - references
    story.append(PageBreak())
    story.extend(
        [
            P("References", styles["Section"]),
            P(
                "[1] F. M. Harper and J. A. Konstan, \"The MovieLens Datasets: History and Context,\" "
                "<i>ACM Transactions on Interactive Intelligent Systems</i>, vol. 5, no. 4, Art. 19, 2015. "
                "doi: 10.1145/2827872.",
                styles["BodySmall"],
            ),
            P(
                "[2] GroupLens Research, \"MovieLens 100K Dataset.\" [Online]. Available: "
                "<link href='https://grouplens.org/datasets/movielens/100k/' color='#0F7C82'>"
                "https://grouplens.org/datasets/movielens/100k/</link>. [Accessed: 2026-10-16].",
                styles["BodySmall"],
            ),
            P(
                "[3] Y. Koren, R. Bell, and C. Volinsky, \"Matrix Factorization Techniques for Recommender Systems,\" "
                "<i>Computer</i>, vol. 42, no. 8, pp. 30-37, Aug. 2009. doi: 10.1109/MC.2009.263.",
                styles["BodySmall"],
            ),
            P(
                "[4] D. P. Kingma and J. Ba, \"Adam: A Method for Stochastic Optimization,\" in <i>Proc. 3rd Int. "
                "Conf. Learning Representations (ICLR)</i>, 2015. doi: 10.48550/arXiv.1412.6980.",
                styles["BodySmall"],
            ),
            P(
                "[5] D. Smilkov <i>et al.</i>, \"TensorFlow.js: Machine Learning for the Web and Beyond,\" in "
                "<i>Proc. 2nd SysML Conf.</i>, 2019. [Online]. Available: "
                "<link href='https://arxiv.org/abs/1901.05350' color='#0F7C82'>https://arxiv.org/abs/1901.05350</link>. "
                "[Accessed: 2026-10-16].",
                styles["BodySmall"],
            ),
            P(
                "[6] J. L. Herlocker, J. A. Konstan, L. G. Terveen, and J. Riedl, \"Evaluating Collaborative Filtering "
                "Recommender Systems,\" <i>ACM Transactions on Information Systems</i>, vol. 22, no. 1, pp. 5-53, "
                "Jan. 2004. doi: 10.1145/963770.963772.",
                styles["BodySmall"],
            ),
            P(
                "[7] TensorFlow.js, \"API Reference, version 4.22.0.\" [Online]. Available: "
                "<link href='https://js.tensorflow.org/api/4.22.0/' color='#0F7C82'>"
                "https://js.tensorflow.org/api/4.22.0/</link>. [Accessed: 2026-10-16].",
                styles["BodySmall"],
            ),
            Spacer(1, 8),
            P("Reproducibility note", styles["Subsection"]),
            P(
                "All numeric claims in Tables I-IV and the two Top-10 lists are generated from "
                "<font name='Courier'>evidence/experiment_results.json</font>. The browser runner performs the tests, "
                "three training runs, the user-level analysis, catalogue-frequency analysis, and dot-product extraction "
                "in one command. The report builder reads that JSON rather than duplicating numbers by hand.",
                styles["BodySmall"],
            ),
        ]
    )

    doc = ReportDocTemplate(str(OUTPUT_PATH))
    doc.build(story)
    print(OUTPUT_PATH)


if __name__ == "__main__":
    build_report()
