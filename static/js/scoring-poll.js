/**
 * Poll submission scoring status until scored or failed.
 */

function scoreBadgeClass(score) {
  if (score >= 80) return 'score-badge score-high';
  if (score >= 60) return 'score-badge score-medium';
  return 'score-badge score-low';
}

function updateScoreBadge(submissionId, text, className) {
  const byData = document.querySelector(
    '[data-submission-id="' + submissionId + '"] .score-badge'
  );
  const byId = document.getElementById('score-badge-' + submissionId);
  const badge = byData || byId;
  if (badge) {
    if (className) badge.className = className;
    badge.textContent = text;
  }
}

function pollStatus(submissionId) {
  const interval = setInterval(function () {
    fetch('/api/submission/' + submissionId + '/status')
      .then(function (r) {
        if (!r.ok) throw new Error('status ' + r.status);
        return r.json();
      })
      .then(function (data) {
        if (data.scoring_status === 'scored') {
          clearInterval(interval);
          if (data.score != null) {
            const score = Number(data.score);
            updateScoreBadge(
              submissionId,
              score.toFixed(1) + '/100',
              scoreBadgeClass(score)
            );
          } else {
            updateScoreBadge(submissionId, 'N/A', 'score-badge score-low');
          }
          setTimeout(function () {
            location.reload();
          }, 1000);
        }
        if (data.scoring_status === 'failed') {
          clearInterval(interval);
          updateScoreBadge(submissionId, 'Failed', 'score-badge score-low');
        }
      })
      .catch(function () {
        clearInterval(interval);
      });
  }, 5000);
}

function initScoringPoll(submissionIds) {
  if (!submissionIds || !submissionIds.length) return;
  submissionIds.forEach(function (id) {
    pollStatus(id);
  });
}

window.pollStatus = pollStatus;
window.initScoringPoll = initScoringPoll;
