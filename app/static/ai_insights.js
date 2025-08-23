document.getElementById('submitAiPrompt').addEventListener('click', async () => {
  const prompt = document.getElementById('aiPrompt').value.trim();
  const outputEl = document.getElementById('aiOutput');

  if (!prompt) {
    alert('Please enter a prompt.');
    return;
  }

  outputEl.textContent = 'Generating insight...';

  try {
    const response = await fetch('/api/ai-insights', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt })
    });

    const data = await response.json();
    outputEl.textContent = data.summary || 'No insight generated.';
  } catch (err) {
    outputEl.textContent = 'Error retrieving insight.';
    console.error(err);
  }
});
