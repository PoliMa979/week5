import { chromium } from "/Users/polinamaltseva/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs";
import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";

const projectDir = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const evidenceDir = path.join(projectDir, "evidence");
const baseUrl = process.env.HW5_URL || "http://127.0.0.1:8765/";
const chromePath = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";

await fs.mkdir(evidenceDir, { recursive: true });

const browser = await chromium.launch({
  headless: true,
  executablePath: chromePath,
  args: ["--enable-gpu", "--ignore-gpu-blocklist", "--use-angle=metal"],
});

try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1800 } });
  page.on("console", (message) => {
    if (message.type() === "error") process.stderr.write(`[browser] ${message.text()}\n`);
  });

  process.stdout.write(`Opening ${baseUrl}\n`);
  await page.goto(baseUrl, { waitUntil: "networkidle", timeout: 120_000 });
  await page.waitForFunction(() => typeof trainSet !== "undefined" && trainSet.length > 0, null, {
    timeout: 120_000,
  });

  const environment = await page.evaluate(() => {
    const canvas = document.createElement("canvas");
    const gl = canvas.getContext("webgl");
    const debug = gl && gl.getExtension("WEBGL_debug_renderer_info");
    return {
      userAgent: navigator.userAgent,
      tfVersion: tf.version.tfjs,
      tfBackend: tf.getBackend(),
      webglRenderer: debug ? gl.getParameter(debug.UNMASKED_RENDERER_WEBGL) : "unavailable",
    };
  });
  process.stdout.write(`Backend ${environment.tfBackend}; ${environment.webglRenderer}\n`);

  const selfChecks = await page.evaluate(() => runTests());
  process.stdout.write(
    `Self-checks: ${selfChecks.passed} passed, ${selfChecks.failed} failed, ${selfChecks.pending} pending\n`,
  );
  if (selfChecks.failed || selfChecks.pending) {
    throw new Error("The built-in self-checks did not pass completely.");
  }

  const collectRun = async ({ label, reg }) => {
    process.stdout.write(`Starting ${label} (reg=${reg})\n`);
    await page.evaluate((value) => {
      document.getElementById("epochs").value = "20";
      document.getElementById("lr").value = "0.01";
      document.getElementById("reg").value = String(value);
      document.getElementById("batch-size").value = "64";
    }, reg);

    const result = await page.evaluate(({ label: runLabel, reg: runReg }) => {
      const started = performance.now();
      runPipeline();
      const durationSeconds = (performance.now() - started) / 1000;

      const movieById = new Map(movies.map((movie) => [movie.id, movie]));
      const trainPool = new Set(trainSet.map((row) => row.movieId));
      const trainPopularity = new Map();
      for (const row of trainSet) {
        trainPopularity.set(row.movieId, (trainPopularity.get(row.movieId) || 0) + 1);
      }

      const median = (values) => {
        if (!values.length) return null;
        const sorted = values.slice().sort((a, b) => a - b);
        const middle = Math.floor(sorted.length / 2);
        return sorted.length % 2
          ? sorted[middle]
          : (sorted[middle - 1] + sorted[middle]) / 2;
      };

      const genreSummary = (movieIds) => {
        const counts = new Map();
        for (const movieId of movieIds) {
          const movie = movieById.get(movieId);
          for (const genre of movie ? movie.genres : []) {
            counts.set(genre, (counts.get(genre) || 0) + 1);
          }
        }
        return Array.from(counts, ([genre, count]) => ({
          genre,
          count,
          share: movieIds.length ? count / movieIds.length : 0,
        })).sort((a, b) => b.count - a.count || a.genre.localeCompare(b.genre));
      };

      const selectedUsers = [1, 19];
      const userAnalysis = selectedUsers.map((userId) => {
        const trainRows = trainSet.filter((row) => row.userId === userId);
        const valRows = valSet.filter((row) => row.userId === userId);
        const testRows = testSet.filter((row) => row.userId === userId);
        const historyRows = [...trainRows, ...valRows];
        const historyIds = historyRows.map((row) => row.movieId);
        const top10 = recommendTopK(userId, 10).map((row) => ({
          ...row,
          genres: movieById.get(row.movieId)?.genres || [],
          trainingRatings: trainPopularity.get(row.movieId) || 0,
          relevantTest: testRows.some(
            (testRow) => testRow.movieId === row.movieId && testRow.rating >= 4,
          ),
        }));
        const relevantIds = new Set(
          testRows
            .filter((row) => row.rating >= 4 && trainPool.has(row.movieId))
            .map((row) => row.movieId),
        );
        const hits = top10.filter((row) => relevantIds.has(row.movieId)).length;
        const excludedRated = top10.filter((row) => historyIds.includes(row.movieId));

        return {
          userId,
          trainRatings: trainRows.length,
          validationRatings: valRows.length,
          testRatings: testRows.length,
          relevantTestMovies: relevantIds.size,
          hitsAt10: hits,
          recallAt10: relevantIds.size ? hits / relevantIds.size : null,
          historyGenres: genreSummary(historyIds),
          recommendationGenres: genreSummary(top10.map((row) => row.movieId)),
          historyMedianPopularity: median(
            historyIds.map((movieId) => trainPopularity.get(movieId) || 0),
          ),
          recommendationMedianPopularity: median(
            top10.map((row) => row.trainingRatings),
          ),
          excludedRatedCount: excludedRated.length,
          highRatedHistoryExamples: historyRows
            .filter((row) => row.rating >= 4)
            .sort((a, b) => b.timestamp - a.timestamp || a.movieId - b.movieId)
            .slice(0, 10)
            .map((row) => ({
              movieId: row.movieId,
              title: movieById.get(row.movieId)?.title || `Movie #${row.movieId}`,
              rating: row.rating,
              genres: movieById.get(row.movieId)?.genres || [],
            })),
          top10,
        };
      });

      const recommendationFrequency = new Map();
      for (let userId = 1; userId <= numUsers; userId++) {
        for (const recommendation of recommendTopK(userId, 10)) {
          recommendationFrequency.set(
            recommendation.movieId,
            (recommendationFrequency.get(recommendation.movieId) || 0) + 1,
          );
        }
      }
      const mostRecommended = Array.from(recommendationFrequency, ([movieId, count]) => ({
        movieId,
        title: movieById.get(movieId)?.title || `Movie #${movieId}`,
        listCount: count,
        listShare: count / numUsers,
        trainingRatings: trainPopularity.get(movieId) || 0,
      }))
        .sort((a, b) => b.listCount - a.listCount || a.movieId - b.movieId)
        .slice(0, 10);

      const primaryTop = userAnalysis[0].top10[0];
      const userVector = tf.tidy(() =>
        Array.from(model.userFactors.slice([1, 0], [1, NUM_FACTORS]).dataSync()),
      );
      const itemVector = tf.tidy(() =>
        Array.from(
          model.itemFactors.slice([primaryTop.movieId, 0], [1, NUM_FACTORS]).dataSync(),
        ),
      );
      const products = userVector.map((value, index) => value * itemVector[index]);
      const dot = products.reduce((sum, value) => sum + value, 0);

      const recall = recallAtK(10);
      const distinctTrainUsers = new Set(trainSet.map((row) => row.userId));
      const distinctTrainMovies = new Set(trainSet.map((row) => row.movieId));
      const valUnseenRows = valSet.filter((row) => !distinctTrainMovies.has(row.movieId));
      const testUnseenRows = testSet.filter((row) => !distinctTrainMovies.has(row.movieId));

      return {
        label: runLabel,
        config: {
          factors: NUM_FACTORS,
          epochs: 20,
          learningRate: 0.01,
          regularization: runReg,
          batchSize: 64,
          seed: 20261016,
        },
        durationSeconds,
        history: trainingHistory.map((row) => ({ ...row })),
        bestCheckpoint: bestCheckpoint ? { ...bestCheckpoint } : null,
        baselineValidationRMSE: computeBaselineRMSE(valSet),
        baselineTestRMSE: computeBaselineRMSE(testSet),
        selectedModelTestRMSE: computeRMSEFor(testSet),
        recall: {
          overallRecall: recall.overallRecall,
          evaluableUsers: recall.perUser.length,
          totalHits: recall.perUser.reduce((sum, row) => sum + row.hit, 0),
          totalRelevant: recall.perUser.reduce((sum, row) => sum + row.relevant, 0),
          usersWithHits: recall.perUser.filter((row) => row.hit > 0).length,
          unseenRelevantIds: recall.excluded.unseenIds,
          usersWithoutRelevant: recall.excluded.usersWithoutRelevant,
        },
        data: {
          users: numUsers,
          movies: movies.length,
          ratings: ratings.length,
          sparsity: 1 - ratings.length / (numUsers * movies.length),
          trainRatings: trainSet.length,
          validationRatings: valSet.length,
          testRatings: testSet.length,
          trainingMean: model.globalMean,
          usersAbsentFromTraining: numUsers - distinctTrainUsers.size,
          moviesAbsentFromTraining: movies.length - distinctTrainMovies.size,
          validationRowsOnUnseenMovies: valUnseenRows.length,
          testRowsOnUnseenMovies: testUnseenRows.length,
        },
        userAnalysis,
        catalogue: {
          moviesAppearingInAnyTop10: recommendationFrequency.size,
          mostRecommended,
        },
        manualCheck: {
          userId: 1,
          movieId: primaryTop.movieId,
          title: primaryTop.title,
          userVector,
          itemVector,
          products,
          dot,
          globalMean: model.globalMean,
          unclampedScore: model.globalMean + dot,
          clampedPrediction: predictRating(1, primaryTop.movieId),
          displayedScore: primaryTop.score,
        },
        tfNumTensors: tf.memory().numTensors,
      };
    }, { label, reg });

    process.stdout.write(
      `${label}: best epoch ${result.bestCheckpoint.epoch}, val ${result.bestCheckpoint.valRMSE.toFixed(6)}, test ${result.selectedModelTestRMSE.toFixed(6)}, recall ${result.recall.overallRecall.toFixed(6)}, ${result.durationSeconds.toFixed(1)} s\n`,
    );
    return result;
  };

  const defaultRun = await collectRun({ label: "default", reg: 0.05 });
  const strongerRegularizationRun = await collectRun({ label: "reg-0.10", reg: 0.1 });
  const repeatRun = await collectRun({ label: "default-repeat", reg: 0.05 });

  const historyMaxAbsDifference = Math.max(
    ...defaultRun.history.flatMap((row, index) => {
      const repeat = repeatRun.history[index];
      return [
        Math.abs(row.trainRMSE - repeat.trainRMSE),
        Math.abs(row.valRMSE - repeat.valRMSE),
      ];
    }),
  );

  const output = {
    generatedAt: new Date().toISOString(),
    environment,
    selfChecks,
    runs: [defaultRun, strongerRegularizationRun, repeatRun],
    reproducibility: {
      historyMaxAbsDifference,
      identical: historyMaxAbsDifference === 0,
    },
  };

  await fs.writeFile(
    path.join(evidenceDir, "experiment_results.json"),
    `${JSON.stringify(output, null, 2)}\n`,
    "utf8",
  );
  await page.evaluate(() => {
    const select = document.getElementById("user-select");
    if (select) select.value = "1";
    renderTopK(1);
    renderRecall(10);
    const rows = Array.from(document.querySelectorAll("#recall-results tbody tr"));
    rows.slice(15).forEach((row) => {
      row.style.display = "none";
    });
    if (rows.length > 15) {
      const note = document.createElement("p");
      note.className = "hint";
      note.textContent = `Screenshot shows the first 15 of ${rows.length} evaluable users; the complete table is stored in evidence/experiment_results.json.`;
      document.getElementById("recall-results").appendChild(note);
    }
  });
  await page.screenshot({
    path: path.join(evidenceDir, "trained_application.png"),
    fullPage: true,
  });
  process.stdout.write(
    `Saved evidence/experiment_results.json and evidence/trained_application.png\n`,
  );
} finally {
  await browser.close();
}
